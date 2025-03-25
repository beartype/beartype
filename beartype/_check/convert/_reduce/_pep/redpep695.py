#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`695`-compliant **type alias reducers** (i.e., low-level
callables converting higher-level objects created via the ``type`` statement
under Python >= 3.12 to lower-level type hints more readily consumable by
:mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep695Exception
from beartype.typing import Optional
from beartype._cave._cavefast import HintPep695TypeAlias
from beartype._check.metadata.hint.hintsane import (
    HINT_IGNORABLE,
    HintOrSane,
    HintSane,
)
from beartype._data.hint.datahintpep import (
    Hint,
)
from beartype._util.error.utilerrget import get_name_error_attr_name
from beartype._util.hint.pep.proposal.pep695 import (
    get_hint_pep695_unsubscripted_alias)

# ....................{ REDUCERS                           }....................
def reduce_hint_pep695_subscripted(
    hint: Hint,
    parent_hint_sane: Optional[HintSane],
    exception_prefix: str,
    **kwargs,
) -> HintOrSane:
    '''
    Reduce the passed :pep:`695`-compliant **subscripted type alias** (i.e.,
    object created by a statement of the form ``type
    {alias_name}[{typevar_name}] = {alias_value}``) to that unsubscripted alias
    and corresponding **type variable lookup table** (i.e., immutable dictionary
    mapping from those same type variables to those same child hints).

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : Hint
        Subscripted hint to be inspected.
    parent_hint_sane : Optional[HintSane]
        Either:

        * If the passed hint is a **root** (i.e., top-most parent hint of a tree
          of child hints), :data:`None`.
        * Else, the passed hint is a **child** of some parent hint. In this
          case, the **sanified parent type hint metadata** (i.e., immutable and
          thus hashable object encapsulating *all* metadata previously returned
          by :mod:`beartype._check.convert.convsanify` sanifiers after
          sanitizing the possibly PEP-noncompliant parent hint of this child
          hint into a fully PEP-compliant parent hint).
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    Returns
    -------
    HintSane
        **Sanified type hint metadata** (i.e., :class:`.HintSane` object)
        describing this reduction.

    Raises
    ------
    BeartypeDecorHintPep484TypeVarViolation
        If one of these type hints violates the bounds or constraints of one of
        these type variables.

    See Also
    --------
    ``reduce_hint_pep484_subscripted_typevars_to_hints``
        Further details.
    '''

    # Avoid circular import dependencies.
    from beartype._check.convert._reduce._pep.pep484.redpep484typevar import (
        reduce_hint_pep484_subscripted_typevars_to_hints)

    # Reduce this PEP 695-compliant subscripted type alias to:
    # * The semantically useful unsubscripted alias originating this
    #   semantically useless subscripted alias.
    # * The type variable lookup table mapping all type variables parametrizing
    #   this unsubscripted alias to all non-type variable hints subscripting
    #   this subscripted alias.
    # print(f'[reduce_hint_pep484585_generic_subscripted] Reducing subscripted generic {repr(hint)}...')
    hint_sane = reduce_hint_pep484_subscripted_typevars_to_hints(
        hint=hint,
        parent_hint_sane=parent_hint_sane,
        exception_prefix=exception_prefix,
    )

    #FIXME: *THIS DEFINITELY REQUIRES DOCUMENTATION.* Basically:
    #* This function operates in two phases:
    #  * The first phase above decides the type variable lookup table for this
    #    subscripted PEP 695 type alias.
    #  * The second phase here decides the recursion guard. Crucially, this
    #    recursion guard also intentionally applies to the original
    #    *SUBSCRIPTED* (rather than unsubscripted) PEP 695 type alias. This is
    #    why we pass "hint=hint". That said, we also have to preserve the type
    #    variable lookup table decided in the first phase. This is why we pass
    #    the 'parent_hint_sane=hint_sane". It is, indeed, complicated.

    # Sanified metadata to be returned, guarded against infinite recursion.
    hint_sane = _make_hint_pep695_recursable_hints(
        hint=hint, parent_hint_sane=hint_sane)

    # Return this metadata.
    return hint_sane


def reduce_hint_pep695_unsubscripted(
    hint: Hint,
    parent_hint_sane: Optional[HintSane],
    exception_prefix: str,
    **kwargs,
) -> HintOrSane:
    '''
    Reduce the passed :pep:`695`-compliant **unsubscripted type alias** (i.e.,
    object created by a statement of the form ``type {alias_name} =
    {alias_value}``) to the underlying type hint referred to by this alias.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : HintPep695TypeAlias
        Unsubscripted type alias to be reduced.
    parent_hint_sane : Optional[HintSane]
        Either:

        * If the passed hint is a **root** (i.e., top-most parent hint of a tree
          of child hints), :data:`None`.
        * Else, the passed hint is a **child** of some parent hint. In this
          case, the **sanified parent type hint metadata** (i.e., immutable and
          thus hashable object encapsulating *all* metadata previously returned
          by :mod:`beartype._check.convert.convsanify` sanifiers after
          sanitizing the possibly PEP-noncompliant parent hint of this child
          hint into a fully PEP-compliant parent hint).
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    All remaining passed keyword parameters are silently ignored.

    Returns
    -------
    HintSane
        **Sanified type hint metadata** (i.e., :class:`.HintSane` object)
        describing this reduction.

    Raises
    ------
    BeartypeDecorHintPep695Exception
        If this alias contains one or more unquoted relative forward references
        to undefined attributes. Note that this *only* occurs when callers avoid
        beartype import hooks in favour of manually decorating callables and
        classes with the :func:`beartype.beartype` decorator.
    '''
    assert isinstance(hint, HintPep695TypeAlias), (
        f'{repr(hint)} not PEP 695-compliant unsubscripted type alias.')

    # ....................{ RECURSE                        }....................
    #FIXME: *NON-IDEAL.* Ideally, @beartype would actually generate code
    #recursively type-checking recursive hints. However, doing so is *EXTREMELY*
    #non-trivial. Why?
    #
    #Non-triviality is one obvious concern. For each recursive hint, @beartype
    #must now:
    #* Dynamically generate one low-level recursive type-checking function
    #  unique to that recursive hint.
    #* Call each such function in higher-level wrapper functions to type-check
    #  each pith against the corresponding recursive hint.
    #
    #Safety is another obvious concern. Generated code *MUST* explicitly guard
    #against infinitely recursive containers:
    #    >>> infinite_list = []
    #    >>> infinite_list.append(infinite_list)  # <-- gg fam
    #
    #But guarding against infinitely recursive containers requires maintaining a
    #(...waitforit) frozen set of the IDs of all previously type-checked
    #objects, which must then be passed to each dynamically generated recursive
    #type-checking function that type-checks a specific recursive hint.
    #Maintaining these frozen sets then incurs a probably significant space and
    #time complexity hit.
    #
    #In short, it's pretty brutal stuff. For now, simply ignoring recursion
    #strikes us the sanest and certainly simplest approach. *sigh*

    #FIXME: Propagate this logic above. Doing so should be trivial. \o/
    # If...
    if (
        # This hint has a parent *AND*...
        parent_hint_sane is not None and
        # This hint is a transitive parent of itself, this hint has already been
        # visited by the current breadth-first search (BFS) and thus constitutes
        # a recursive hint. Certainly, various approaches to generating code
        # type-checking recursive hints exists. @beartype currently embraces the
        # easiest, fastest, and laziest approach: simply ignore all recursion!
        hint in parent_hint_sane.recursable_hints
    ):
        return HINT_IGNORABLE
    # Else, this hint is either the root *OR* not a transitive parent of itself.
    # In either case, this hint is *NOT* a recursive hint..... yet. I sigh.

    # ....................{ REDUCE                         }....................
    # Underlying type hint to be returned.
    hint_aliased: Hint = None  # pyright: ignore

    # Attempt to...
    try:
        # Reduce this alias to the type hint it lazily refers to. If this alias
        # contains *NO* forward references to undeclared attributes, this
        # reduction *SHOULD* succeed. Let's pretend we mean that.
        #
        # Note that this getter is memoized and thus intentionally called with
        # positional arguments.
        hint_aliased = get_hint_pep695_unsubscripted_alias(
            hint, exception_prefix)
    # If doing so raises a builtin "NameError" exception, this alias contains
    # one or more forward references to undeclared attributes. In this case...
    except NameError as exception:
        # Unqualified basename of this alias (i.e., name of the global or local
        # variable assigned to by the left-hand side of this alias).
        hint_name = repr(hint)

        # Fully-qualified name of the third-party module defining this alias.
        hint_module_name = hint.__module__
        # print(f'hint_module_name: {hint_module_name}')

        # Unqualified basename of the next remaining undeclared attribute
        # contained in this alias relative to that module.
        hint_ref_name = get_name_error_attr_name(exception)
        # print(f'hint: {hint}; hint_ref_name: {hint_ref_name}')

        # Raise a human-readable exception describing this issue.
        raise BeartypeDecorHintPep695Exception(
            f'{exception_prefix}PEP 695 type alias "{hint_name}" '
            f'unquoted relative forward reference {repr(hint_ref_name)} in '
            f'module "{hint_module_name}" unsupported outside '
            f'"beartype.claw" import hooks. Consider either:\n'
            f'* Quoting this forward reference in this type alias: e.g.,\n'
            f'      # Instead of an unquoted forward reference...\n'
            f'      type {hint_name} = ... {hint_ref_name} ...\n'
            f'\n'
            f'      # Prefer a quoted forward reference.\n'
            f'      type {hint_name} = ... "{hint_ref_name}" ...\n'
            f'* Applying "beartype.claw" import hooks to '
            f'module "{hint_module_name}": e.g.,\n'
            f'      # In your "this_package.__init__" submodule:\n'
            f'      from beartype.claw import beartype_this_package\n'
            f'      beartype_this_package()'
        ) from exception
    # Else, doing so raised *NO* exceptions, implying this alias contains *NO*
    # forward references to undeclared attributes.

    # ....................{ RETURN                         }....................
    # Sanified metadata to be returned, guarded against infinite recursion.
    hint_sane = _make_hint_pep695_recursable_hints(
        hint=hint_aliased, parent_hint_sane=parent_hint_sane)

    # Return this metadata.
    return hint_sane

# ....................{ PRIVATE ~ factories                }....................
#FIXME: Docstring us up, please. *sigh*
def _make_hint_pep695_recursable_hints(
    hint: Hint, parent_hint_sane: Optional[HintSane]) -> HintSane:

    # Sanified metadata to be returned.
    hint_sane: HintSane = None  # type: ignore[assignment]

    # Recursion guard containing *ONLY* this pre-sanified unsubscripted hint
    # (which is what the initial recursion logic above will then subsequently
    # test against if this a recursive alias).
    recursable_hints = frozenset((hint,))

    # If this hint has *NO* parent, this is a root hint. In this case...
    if parent_hint_sane is None:
        # Metadata encapsulating this hint and recursion guard containing *ONLY*
        # this pre-sanified unsubscripted hint (which is what the initial
        # recursion logic above will then subsequently test against if this a
        # recursive alias).
        hint_sane = HintSane(
            hint=hint, recursable_hints=recursable_hints)
    # Else, this hint has a parent. In this case...
    else:
        # If the parent hint is also associated with a recursion guard...
        if parent_hint_sane.recursable_hints:
            # Full recursion guard merging the guard associated this parent hint
            # with the guard containing only this child hint, efficiently
            # defined as...
            recursable_hints = (
                # The guard protecting all transitive parent hints of this hint
                # with...
                parent_hint_sane.recursable_hints |  # type: ignore[operator]
                # The guard protecting this hint. Note that the order of
                # operands in this "|" operation is insignificant.
                recursable_hints
            )
        # Else, the parent hint is associated with *NO* such guard.

        # Metadata encapsulating this hint and recursion guard, while
        # "cascading" any other metadata associated with this parent hint (e.g.,
        # type variable lookup table) down onto this child hint as well.
        hint_sane = parent_hint_sane.permute(
            hint=hint, recursable_hints=recursable_hints)

    # Return this underlying type hint.
    return hint_sane
