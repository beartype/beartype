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
    is_hint_recursive,
    make_hint_sane_recursable,
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
    hint_parent_sane: Optional[HintSane],
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
    hint_parent_sane : Optional[HintSane]
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

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype._check.convert._reduce._pep.pep484.redpep484typevar import (
        reduce_hint_pep484_subscripted_typevars_to_hints)

    # ....................{ RECURSE                        }....................
    # If this hint is recursive, ignore this hint to avoid infinite recursion.
    #
    # Certainly, various approaches to generating code type-checking recursive
    # hints exists. @beartype currently embraces the easiest, fastest, and
    # laziest approach: just ignore all recursion! Ignorance works wonders.
    if is_hint_recursive(hint=hint, hint_parent_sane=hint_parent_sane):
        return HINT_IGNORABLE
    # Else, this hint is *NOT* recursive.

    # ....................{ REDUCE                         }....................
    # This reducer is divided into two phases:
    # 1. The first phase decides the type variable lookup table for this alias.
    # 2. The second phase decides the recursion guard for this alias.
    #
    # Both phases are non-trivial. The output of each phase is sanified hint
    # metadata (i.e., a "HintSane" object) containing the result of the decision
    # problem decided by that phase.

    # ....................{ REDUCE ~ phase : 1             }....................
    # Decide the type variable lookup table for this alias. Specifically, reduce
    # this PEP 695-compliant subscripted type alias to:
    # * The semantically useful unsubscripted alias originating this
    #   semantically useless subscripted alias.
    # * The type variable lookup table mapping all type variables parametrizing
    #   this unsubscripted alias to all non-type variable hints subscripting
    #   this subscripted alias.
    # print(f'[reduce_hint_pep484585_generic_subscripted] Reducing subscripted generic {repr(hint)}...')
    hint_sane = reduce_hint_pep484_subscripted_typevars_to_hints(
        hint=hint,
        hint_parent_sane=hint_parent_sane,
        exception_prefix=exception_prefix,
    )

    # ....................{ REDUCE ~ phase : 2             }....................
    # Decide the recursion guard protecting this possibly recursive alias
    # against infinite recursion. Note that:
    # * This guard intentionally applies to the original *SUBSCRIPTED* PEP
    #   695-compliant type alias (rather rather than the *UNSUBSCRIPTED* PEP
    #   695-compliant type alias decided by the prior phase). This is why we
    #   pass "hint=hint" rather than "hint=hint_sane.hint" here.
    # * The type variable lookup table decided in the first phase *MUST* also be
    #   preserved. This is why we pass the "hint_parent_sane=hint_sane" rather
    #   than "hint_parent_sane=hint_parent_sane" as in the prior phase. Indeed,
    #   "hint_sane" should safely encapsulate all metadata encapsulated by
    #   "hint_parent_sane".
    hint_sane = make_hint_sane_recursable(hint=hint, hint_parent_sane=hint_sane)

    # ....................{ RETURN                         }....................
    # Return this metadata.
    return hint_sane


def reduce_hint_pep695_unsubscripted(
    hint: Hint,
    hint_parent_sane: Optional[HintSane],
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
    hint_parent_sane : Optional[HintSane]
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

    # If this hint is recursive, ignore this hint to avoid infinite recursion.
    #
    # Certainly, various approaches to generating code type-checking recursive
    # hints exists. @beartype currently embraces the easiest, fastest, and
    # laziest approach: just ignore all recursion! Ignorance works wonders.
    if is_hint_recursive(hint=hint, hint_parent_sane=hint_parent_sane):
        return HINT_IGNORABLE
    # Else, this hint is *NOT* recursive.

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
    hint_sane = make_hint_sane_recursable(
        hint=hint_aliased, hint_parent_sane=hint_parent_sane)

    # Return this metadata.
    return hint_sane
