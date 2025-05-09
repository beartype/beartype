#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **type variable reducers** (i.e., low-level
callables converting :pep:`484`-compliant type variables to lower-level type
hints more readily consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeDecorHintPep484TypeVarException,
    BeartypeDecorHintPep484TypeVarViolation,
)
from beartype.typing import (
    Optional,
    TypeVar,
)
from beartype._check.convert._reduce._redrecurse import (
    is_hint_recursive,
    make_hint_sane_recursable,
)
from beartype._check.metadata.hint.hintsane import (
    HINT_SANE_IGNORABLE,
    HINT_SANE_RECURSIVE,
    HintOrSane,
    HintSane,
)
from beartype._data.hint.datahintpep import (
    Hint,
    TupleHints,
    TypeVarToHint,
)
from beartype._data.hint.datahinttyping import (
    TupleTypeVars,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cls.pep.clspep3119 import is_object_issubclassable
from beartype._util.hint.nonpep.utilnonpeptest import is_hint_nonpep_type
from beartype._util.hint.pep.proposal.pep484.pep484typevar import (
    get_hint_pep484_typevar_bound_or_none,
    is_hint_pep484_typevar,
)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_args,
    get_hint_pep_origin,
    get_hint_pep_typevars,
)
from beartype._util.hint.pep.utilpeptest import is_hint_pep
from beartype._util.kind.map.utilmapfrozen import FrozenDict

# ....................{ REDUCERS                           }....................
def reduce_hint_pep484_typevar(
    hint: Hint,
    hint_parent_sane: Optional[HintSane],
    exception_prefix: str,
    **kwargs
) -> HintSane:
    '''
    Reduce the passed :pep:`484`-compliant **type variable** (i.e.,
    :class:`typing.TypedDict` instance) to a lower-level type hint currently
    supported by :mod:`beartype`.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : Hint
        Type variable to be reduced.
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

    All remaining passed arguments are silently ignored.

    Returns
    -------
    HintSane
        Either:

        * If the type variable lookup table encapsulated by the passed sanified
          parent type hint metadata maps this type variable to another type
          hint, the latter.
        * Else if this type variable is both unbounded and unconstrained, this
          type variable is ignorable. In this case, the
          :data:`.HINT_SANE_IGNORABLE` singleton.
        * Else, this type variable's lover-level bounds or constraints.
    '''
    # print(f'Reducing PEP 484 type variable {hint} with parent hint {hint_parent_sane}...')

    # ....................{ RECURSE                        }....................
    # If this subscripted hint is recursive, ignore this subscripted hint to
    # avoid infinite recursion.
    if is_hint_recursive(
        hint=hint,
        hint_parent_sane=hint_parent_sane,
        hint_recursable_depth_max=_HINT_PEP484_TYPEVAR_RECURSABLE_DEPTH_MAX,
    ):
        # print(f'Ignoring recursive type variable {hint} with parent {hint_parent_sane}!')
        return HINT_SANE_RECURSIVE
    # Else, this subscripted hint is *NOT* recursive.

    # ....................{ PHASE                          }....................
    # This reducer is divided into two phases:
    # 1. The first phase decides the type variable lookup table for this alias.
    # 2. The second phase decides the recursion guard for this alias.
    #
    # Both phases are non-trivial. The output of each phase is sanified hint
    # metadata (i.e., a "HintSane" object) containing the result of the decision
    # problem decided by that phase.

    # Reduced hint to be returned, defaulting to this type variable.
    hint_reduced = hint

    # ....................{ PHASE ~ 1 : lookup             }....................
    # If...
    if (
        # This type variable is not a root hint and thus has a parent hint
        # *AND*...
        hint_parent_sane is not None and
        # A parent hint of this type variable maps one or more type variables...
        hint_parent_sane.typevar_to_hint
    ):
        # Type variable lookup table of this parent hint, localized for
        # usability and negligible efficiency.
        typevar_to_hint = hint_parent_sane.typevar_to_hint

        # If a parent hint of this type variable maps exactly one type variable,
        # prefer a dramatically faster and simpler approach.
        if len(typevar_to_hint) == 1:
            # Hint mapped to by this type variable if one or more parent hints
            # previously mapped this type variable to a hint *OR* this hint as
            # is otherwise (i.e., if this type variable is unmapped).
            #
            # Note that this one-liner looks ridiculous, but actually works.
            # More importantly, this is the fastest way to accomplish this.
            hint_reduced = typevar_to_hint.get(hint, hint)  # type: ignore[call-overload]
        # Else, a parent hint of this type variable mapped two or more type
        # variables. In this case, fallback to a slower and more complicated
        # approach that avoids worst-case edge cases. This includes recursion in
        # type variable mappings, which arises in non-trivial class hierarchies
        # involving two or more generics subscripted by two or more type
        # variables that circularly cycle between one another: e.g.,
        #     from typing import Generic
        #     class GenericRoot[T](Generic[T]): pass
        #
        #     # This directly maps {T: S}.
        #     class GenericLeaf[S](GenericStem[S]): pass
        #
        #     # This directly maps {S: T}, which then combines with the above
        #     # mapping to indirectly map {S: T, T: S}. Clearly, this indirect
        #     # mapping provokes infinite recursion unless explicitly handled.
        #     GenericLeaf[T]
        else:
            # Type hints previously reduced from this type variable, initialized
            # to this type variable.
            hint_reduced_prev = hint

            # Shallow copy of this type variable lookup table, coerced from an
            # immutable frozen dictionary into a mutable standard dictionary.
            # This enables type variables reduced by the iteration below to be
            # popped off this copy as a simple (but effective) recursion guard.
            typevar_to_hint_stack = typevar_to_hint.copy()

            #FIXME: [SPEED] *INEFFICIENT.* This has to be done either way, but
            #rather than reperform this O(n) algorithm on every single instance
            #of this type variable, this algorithm should simply be performed
            #exactly *ONCE* in the
            #reduce_hint_pep484_subbed_typevars_to_hints() reducer. Please
            #refactor this iteration over there *AFTER* the dust settles here.
            #FIXME: Actually, it's unclear how exactly this could be refactored
            #into the reduce_hint_pep484_subbed_typevars_to_hints()
            #reducer. This reduction here only searches for a single typevar in
            #O(n) time. Refactoring this over to
            #reduce_hint_pep484_subbed_typevars_to_hints() would require
            #generalizing this into an O(n**2) algorithm there, probably. Yow!

            # While...
            while (
                # This stack still contains one or more type variables that have
                # yet to be reduced by this iteration *AND*...
                typevar_to_hint_stack and
                # This hint is still a type variable...
                isinstance(hint_reduced, TypeVar)
            ):
                # Hint mapped to by this type variable if one or more parent
                # hints previously mapped this type variable to a hint *OR* this
                # hint as is (i.e., if this type variable is unmapped).
                #
                # Note that this one-liner destructively pops this type variable
                # off this temporary stack to prevent this type variable from
                # being reduced more than once by an otherwise recursive
                # mapping. Since this stack is local to this reducer, this
                # behaviour is only locally destructive and thus safe.
                hint_reduced = typevar_to_hint_stack.pop(
                    hint_reduced_prev, hint_reduced_prev)  # pyright: ignore

                # If this type variable maps to itself, this mapping is both
                # ignorable *AND* terminates this reduction.
                if hint_reduced is hint_reduced_prev:
                    break
                # Else, this type variable does *NOT* map to itself.

                # Map this type variable to this hint.
                hint_reduced_prev = hint_reduced
        # print(f'...to hint {hint} via type variable lookup table!')
    # Else, this type variable is unmapped.

    # ....................{ PHASE ~ 1 : bounds             }....................
    # If this hint is still a type variable (e.g., due to either not being
    # mapped by this lookup table *OR* being mapped by this lookup table to yet
    # another type variable)...
    if isinstance(hint_reduced, TypeVar):
        # PEP-compliant hint synthesized from all bounded constraints
        # parametrizing this type variable if any *OR* "None" otherwise (i.e.,
        # if this type variable is both unbounded *AND* unconstrained).
        #
        # Note this call is passed positional parameters due to memoization.
        hint_reduced = get_hint_pep484_typevar_bound_or_none(
            hint_reduced, exception_prefix)  # pyright: ignore

        # If this type variable is both unbounded *AND* unconstrained, this type
        # variable is currently *NOT* type-checkable and is thus ignorable.
        # Reduce this type variable to the ignorable singleton.
        if hint_reduced is None:
            return HINT_SANE_IGNORABLE
        # Else, this type variable is either bounded *OR* constrained. In either
        # case, preserve this newly synthesized hint.
        # print(f'Reducing PEP 484 type variable {repr(hint)} to {repr(hint_bound)}...')
        # print(f'Reducing non-beartype PEP 593 type hint {repr(hint)}...')
    # Else, one or more transitive parent hints previously mapped this type
    # variable to another hint.

    # ....................{ PHASE ~ 2                      }....................
    # Decide the recursion guard protecting this possibly recursive type
    # variable against infinite recursion. Note that:
    # * This guard intentionally applies to the original unreduced type variable
    #   (rather rather than the newly reduced hint decided by the prior phase).
    #   Thus, we pass "hint_recursable=hint" rather than
    #   "hint_recursable=hint_reduced".
    hint_sane = make_hint_sane_recursable(
        # The recursable form of this type alias is the original subscripted
        # hint tested above by the is_hint_recursive() recursion guard.
        hint_recursable=hint,
        # The non-recursable form of this type alias is the unsubscripted hint
        # underlying the original subscripted hint.
        hint_nonrecursable=hint_reduced,
        hint_parent_sane=hint_parent_sane,
    )

    # ....................{ RETURN                         }....................
    # Return this metadata.
    return hint_sane


def reduce_hint_pep484_subbed_typevars_to_hints(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    hint_parent_sane: Optional[HintSane] = None,
    exception_prefix: str = '',
) -> HintOrSane:
    '''
    Reduce the passed :pep:`484`-compliant **subscripted hint** (i.e., object
    produced by subscripting an unsubscripted hint originally parametrized by
    one or more :pep:`484`-compliant type variables with one or more child
    hints) to that unsubscripted hint and corresponding **type variable lookup
    table** (i.e., immutable dictionary mapping from those same type variables
    to those same child hints).

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Caveats
    -------
    This reducer does *not* validate these type variables to actually be type
    variables. Instead, this function defers that validation to the caller. Why?
    Efficiency, mostly. Avoiding the need to explicitly validate these type
    variables reduces the underlying mapping operation to a fast one-liner.

    This reducer validates the sizes of these two tuples to be constrained as:

    .. code-block:: python

       len(typevars) >= len(hints) > 0

    Informally, the passed hint *must* be subscripted by at least one child
    hint. For each such child hint, the unsubscripted hint originating this
    subscripted hint *must* be parametrized by a corresponding type variable.
    The converse is *not* the case, as:

    * For the first type variable, there also *must* exist a corresponding child
      hint to map to that type variable.
    * For *all* type variables following the first, there need *not* exist a
      corresponding child hint to map to that type variable. Type variables with
      *no* corresponding child hints are simply silently ignored (i.e.,
      preserved as type variables rather than mapped to other type hints).

    Equivalently:

    * Both of these tuples *must* be **non-empty** (i.e., contain one or more
      items).
    * This tuple of type variables *must* contain at least as many items as this
      tuple of child hints. Therefore:

      * This tuple of type variables *may* contain exactly as many items as this
        tuple of child hints.
      * This tuple of type variables *may* contain strictly more items than this
        tuple of child hints.
      * This tuple of type variables must *not* contain fewer items than this
        tuple of child hints.

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

        Defaults to :data:`None`.
    exception_prefix : str, optional
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    HintOrSane
        Either:

        * If the unsubscripted hint (e.g., :class:`typing.Generic`) originating
          this subscripted hint (e.g., ``typing.Generic[S, T]``) is
          unparametrized by type variables, that unsubscripted hint as is.
        * Else, that unsubscripted hint is parametrized by one or more type
          variables. In this case, the **sanified type hint metadata** (i.e.,
          :class:`.HintSane` object) describing this reduction.

    Raises
    ------
    exception_cls
        If this type hint is unsubscripted.
    BeartypeDecorHintPep484TypeVarViolation
        If one of these type hints violates the bounds or constraints of one of
        these type variables.
    '''

    # ....................{ LOCALS                         }....................
    # Unsubscripted type alias originating this subscripted hint.
    hint_unsubbed = get_hint_pep_origin(
        hint=hint,
        exception_cls=BeartypeDecorHintPep484TypeVarException,
        exception_prefix=exception_prefix,
    )

    # Tuple of all type variables parametrizing this unsubscripted hint.
    #
    # Note that PEP 695-compliant "type" alias syntax superficially appears to
    # erroneously permit type aliases to be parametrized by non-type variables.
    # In truth, "type" syntax simply permits type aliases to be parametrized by
    # type variables that ambiguously share the same names as builtin types --
    # which then silently shadow those types for the duration of those aliases:
    #     >>> type muh_alias[int] = float | complex  # <-- *gulp*
    #     >>> muh_alias.__parameters__
    #     (int,)  # <-- doesn't look good so far
    #     >>> muh_alias.__parameters__[0] is int
    #     False  # <-- something good finally happened
    hint_unsubbed_typevars = get_hint_pep_typevars(hint_unsubbed)

    # Tuple of all child hints subscripting this subscripted hint.
    hint_childs = get_hint_pep_args(hint)
    # print(f'hint_childs: {repr(hint_childs)}')

    # ....................{ REDUCE                         }....................
    # Decide the type variable lookup table for this hint. Specifically, reduce
    # this subscripted hint to:
    # * The semantically useful unsubscripted hint originating this
    #   semantically useless subscripted hint.
    # * The type variable lookup table mapping all type variables parametrizing
    #   this unsubscripted hint to all non-type variable hints subscripting
    #   this subscripted hint.

    # ....................{ REDUCE ~ noop                  }....................
    # If either...
    if (
        # This unsubscripted hint is parametrized by *NO* type variables, *NO*
        # type variable lookup table can be produced by this reduction.
        #
        # Note this this is an uncommon edge case. Examples include:
        # * Parametrizations of the PEP 484-compliant "typing.Generic"
        #   superclass (e.g., "typing.Generic[S, T]"). In this case, the
        #   original unsubscripted "typing.Generic" superclass remains
        #   unparametrized despite that superclass later being parametrized.
        not hint_unsubbed_typevars or
        # This unsubscripted hint is parametrized by the exact same type
        # variables as this subscripted hint is subscripted by, in which case
        # the resulting type variable lookup table would uselessly be the
        # identity mapping from each of these type variables to itself. While an
        # identity type variable lookup table could trivially be produced, doing
        # so would convey *NO* meaningful semantics and thus be pointless.
        hint_childs == hint_unsubbed_typevars
    # Then reduce this subscripted hint to simply this unsubscripted hint, as
    # type variable lookup tables are then irrelevant.
    ):
        return hint_unsubbed
    # Else, this unsubscripted hint is parametrized by one or more type
    # variables. In this case, produce a type variable lookup table mapping
    # these type variables to child hints subscripting this subscripted hint.

    # ....................{ REDUCE ~ map                   }....................
    # Type variable lookup table mapping from each of these type variables to
    # each of these corresponding child hints.
    #
    # Note that we pass parameters positionally due to memoization.
    typevar_to_hint = _get_hint_pep484_typevars_to_hints(
        hint, hint_unsubbed_typevars, hint_childs, exception_prefix)
    # print(f'Mapped hint {hint} to type variable lookup table {typevar_to_hint}!')

    # ....................{ REDUCE ~ composite             }....................
    # Sanified metadata to be returned.
    hint_sane: HintSane = None  # type: ignore[assignment]

    # If this hint has *NO* parent, this is a root hint. In this case...
    if hint_parent_sane is None:
        # Metadata encapsulating this hint and type variable lookup table.
        hint_sane = HintSane(
            hint=hint_unsubbed, typevar_to_hint=typevar_to_hint)
    # Else, this hint has a parent. In this case...
    else:
        # If the parent hint is also associated with a type variable lookup
        # table...
        if hint_parent_sane.typevar_to_hint:
            # Full type variable lookup table merging the table associated this
            # parent hint with the table just decided above for this child hint,
            # efficiently defined as...
            typevar_to_hint = (
                # The type variable lookup table describing all transitive
                # parent hints of this hint with...
                hint_parent_sane.typevar_to_hint |  # type: ignore[operator]
                # The type variable lookup table describing this hint.
                #
                # Note that this table is intentionally the second rather than
                # first operand of this "|" operation, efficiently ensuring that
                # type variables mapped by this hint take precedence over type
                # variables mapped by transitive parent hints of this hint.
                typevar_to_hint
            )
        # Else, the parent hint is associated with *NO* such table.

        # Metadata encapsulating this hint and type variable lookup table, while
        # "cascading" any other metadata associated with this parent hint (e.g.,
        # recursable hint IDs) down onto this child hint as well.
        hint_sane = hint_parent_sane.permute_sane(
            hint=hint_unsubbed, typevar_to_hint=typevar_to_hint)

    # ....................{ RETURN                         }....................
    # print(f'Reduced subscripted hint {repr(hint)} to unsubscripted hint metadata {repr(hint_sane)}.')

    # Return this metadata.
    return hint_sane

# ....................{ PRIVATE ~ constants                }....................
_HINT_PEP484_TYPEVAR_RECURSABLE_DEPTH_MAX = 0
'''
Value of the optional ``hint_recursable_depth_max`` parameter passed to the
:func:`.is_hint_recursive` tester by the :func:`.reduce_hint_pep484_typevar`
reducer.

This depth ensures that :pep:`484`-compliant type variables are considered to be
recursive *only* after having been recursed into at most this many times before
(i.e., *only* after having been visited exactly once as a child hint of an
arbitrary parent hint). By definition, :pep:`484`-compliant type variables are
guaranteed to *never* be parent hints. Ergo, recursing into type variables
exactly once suffices to expand exactly one nesting level of non-trivial
recursive data structures. This mirrors the restrained recursion allowed by
other reducers.

Consider :pep:`695`-compliant type aliases, for example. Unlike type variables,
type aliases are guaranteed to *always* be parent hints. The value of the
optional ``hint_recursable_depth_max`` parameter passed to the
:func:`.is_hint_recursive` tester by :pep:`695`-specific reducers is thus one
greater than the value of this global. Nonetheless, the real-world effect is
exactly the same: exactly one nesting level of type aliases is expanded.

Consider the following :pep:`484`-compliant generic recursively subscripted by
itself via a :pep:`484`-compliant type variable ``T``:

.. code-block:: python

   class GenericList[T](): ...
   RecursiveGenericList = GenericList[GenericList]

Instances of this generic satisfying the type hint ``RecursiveGenericList``
contain an arbitrary number of other instances of this generic, exhibiting this
internal structure:

.. code-block:: python

   recursive_generic_list = GenericList()
   recursive_generic_list.append(recursive_generic_list)

Halting recursion at the first expansion of the type variable ``T`` then reduces
the type hint ``RecursiveGenericList`` to
``GenericList[GenericList[T]]``, , which reduces to
``GenericList[GenericList[HINT_SANE_RECURSIVE]]``, , which reduces to
``GenericList[GenericList]`` -- conveying exactly one layer of the internal
semantics of this recursive data structure.
'''

# ....................{ PRIVATE ~ getters                  }....................
@callable_cached
def _get_hint_pep484_typevars_to_hints(
    # Mandatory parameters.
    hint: Hint,
    hint_child_typevars: TupleTypeVars,
    hint_child_hints: TupleHints,

    # Optional parameters.
    exception_prefix: str = '',
) -> TypeVarToHint:
    '''
    Type variable lookup table mapping from the passed :pep:`484`-compliant
    **type variables** (i.e., :class:`.TypeVar` objects) to the associated
    passed type hints as key-value pairs of this table.

    This getter is memoized for efficiency. Notably, this getter creates and
    returns a dictionary mapping each type variable in the passed tuple of type
    variables to the associated type hint in the passed tuple of type hints with
    the same 0-based tuple index as that type variable.

    Parameters
    ----------
    hint: Hint
        Parent hint presumably both subscripted by these child hints. This
        parent hint is currently only used to generate human-readable exception
        messages in the event of fatal errors.
    hint_child_typevars : TupleTypeVars
        Tuple of one or more child type variables originally subscripting the
        origin underlying this parent hint.
    hint_child_hints : TupleHints
        Tuple of one or more child type hints subscripting this parent hint,
        which those type variables map to.
    exception_prefix: str, optional
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    TypeVarToHint
        Type variable lookup table mapping these type variables to hint_child_hints.

    Raises
    ------
    BeartypeDecorHintPep484TypeVarException
        If either:

        * This tuple of type variables is empty.
        * This tuple of type hints is empty.
        * This tuple of type hints contains more items than this tuple of type
          variables.
    BeartypeDecorHintPep484TypeVarViolation
        If one of these type hints violates the bounds or constraints of one of
        these type variables.
    '''
    assert isinstance(hint_child_typevars, tuple), (
        f'{repr(hint_child_typevars)} not tuple.')
    assert isinstance(hint_child_hints, tuple), (
        f'{repr(hint_child_hints)} not tuple.')
    assert isinstance(exception_prefix, str), (
        f'{repr(exception_prefix)} not string.')

    # ....................{ PREAMBLE                       }....................
    # If *NO* type variables were passed, raise an exception.
    if not hint_child_typevars:
        raise BeartypeDecorHintPep484TypeVarException(
            f'{exception_prefix}type hint {repr(hint)} '
            f'parametrized by no PEP 484 type variables.'
        )
    # Else, one or more type variables were passed.
    #
    # If *NO* type hint_child_hints were passed, raise an exception.
    elif not hint_child_hints:
        raise BeartypeDecorHintPep484TypeVarException(
            f'{exception_prefix}type hint {repr(hint)} '
            f'subscripted by no type hints.'
        )
    # Else, one or more type hint_child_hints were passed.
    #
    # If more type hints than type variables were passed, raise an exception.
    elif len(hint_child_hints) > len(hint_child_typevars):
        raise BeartypeDecorHintPep484TypeVarException(
            f'{exception_prefix}type hint {repr(hint)} '
            f'number of subscripted type hints {len(hint_child_hints)} exceeds '
            f'number of parametrized type variables {len(hint_child_typevars)} '
            f'(i.e., {len(hint_child_hints)} > {len(hint_child_typevars)}).'
        )
    # Else, either the same number of type hints and type variables were passed
    # *OR* more type variables than type hints were passed.

    # ....................{ MAP                            }....................
    # Type variable lookup table to be returned.
    typevar_to_hint: TypeVarToHint = {}

    #FIXME: Optimize into a "while" loop at some point. *sigh*
    # For each passed type variable and corresponding type hint...
    #
    # Note that:
    # * The C-based zip() builtin has been profiled to be the fastest means of
    #   iterating pairs in pure-Python, interestingly.
    # * If more type variables than type hints were passed, zip() silently
    #   ignores type variables with *NO* corresponding type hints -- exactly as
    #   required and documented by the above docstring.
    # print(f'Mapping hint_child_typevars {hint_child_typevars} -> hint_child_hints {hint_child_hints}...')
    for hint_child_typevar, hint_child_hint in zip(
        hint_child_typevars, hint_child_hints):
        # print(f'Mapping typevar {typevar} -> hint {hint}...')
        # print(f'is_hint_nonpep_type({hint})? {is_hint_nonpep_type(hint, False)}')

        # If this is *NOT* actually a type variable, raise an exception.
        #
        # Note that Python itself typically fails to validate this constraint,
        # thus requiring that we do so explicitly. For example:
        # * Ideally, *ALL* child hints parametrizing a PEP 695-compliant
        #   subscripted type alias would actually be type variables. Sadly, the
        #   "type" statement is excessively permissive under at least Python <=
        #   3.13 (and possibly newer Python releases as well): e.g.,
        #       >>> type muh_alias[int] = float | complex
        #       >>> muh_alias.__parameters__
        #       (int,)  # <-- pretty sure that's *NOT* a parameter, Python
        if not is_hint_pep484_typevar(hint_child_typevar):
            raise BeartypeDecorHintPep484TypeVarException(
                f'{exception_prefix}type hint {repr(hint)} '
                f'parametrization {repr(hint_child_typevar)} not '
                f'PEP 484 type variable (i.e., "typing.TypeVar" object).'
            )
        # Else, this is actually a type variable.

        #FIXME: Insufficient. Ideally, we would also validate this hint to be a
        #*SUBHINT* of this type variable. Specifically, if this type variable is
        #bounded by one or more bounded constraints, then we should validate
        #this hint to be a *SUBHINT* of those constraints: e.g.,
        #    class MuhClass(object): pass
        #
        #    # PEP 695 type alias parametrized by a type variable bound to a
        #    # subclass of the "MuhClass" type.
        #    type muh_alias[T: MuhClass] = T | int
        #
        #    # *INVALID.* Ideally, @beartype should reject this, as "int" is
        #    # *NOT* a subhint of "MuhClass".
        #    def muh_func(muh_arg: muh_alias[int]) -> None: pass
        #
        #Doing so is complicated, however, by forward reference proxies. For
        #obvious reasons, forward reference proxies are *NOT* safely resolvable
        #at this early decoration time that this function is typically called
        #at. If this hint either:
        #* Is itself a forward reference proxy, ignore rather than validate this
        #  hint as a subhint of these bounded constraints. Doing so is trivial
        #  by simply calling "is_beartype_forwardref(hint)" here.
        #* Is *NOT* itself a forward reference proxy but is transitively
        #  subscripted by one or more forward reference proxies, ignore rather
        #  than validate this hint as a subhint of these bounded constraints.
        #  Doing so is *EXTREMELY NON-TRIVIAL.* Indeed, there's *NO* reasonable
        #  way to do so directly here. Rather, we'd probably have to embrace an
        #  EAFP approach: that is, just crudely try to:
        #  * Detect whether this hint is a subhint of these bounded constraints.
        #  * If doing so raises an exception indicative of a forward reference
        #    issue, silently ignore that exception.
        #
        #  Of course, we're unclear what exception type that would even be. Does
        #  the beartype.door.is_subhint() tester even explicitly detect forward
        #  reference issues and raise an appropriate exception type? No idea.
        #  Probably *NOT*, honestly. Interestingly, is_subhint() currently even
        #  fails to support standard PEP 484-compliant forward references:
        #      >>> is_subhint('int', int)
        #      beartype.roar.BeartypeDoorNonpepException: Type hint 'int'
        #      currently unsupported by "beartype.door.TypeHint".
        #
        #Due to these (and probably more) issues, we currently *ONLY* validate
        #this hint to be a subhint of these bounded constraints...

        # If this hint is a PEP-noncompliant isinstanceable type (and thus *NOT*
        # an unresolvable forward reference proxy, which by definition is *NOT*
        # isinstanceable)...
        elif is_hint_nonpep_type(
            hint=hint_child_hint, is_forwardref_valid=False):
            # PEP-compliant type hint synthesized from all bounded constraints
            # parametrizing this type variable if any *OR* "None" otherwise.
            #
            # Note that this call is intentionally passed positional rather
            # positional keywords due to memoization.
            typevar_bound = get_hint_pep484_typevar_bound_or_none(
                hint_child_typevar, exception_prefix)
            # print(f'[{typevar}] is_object_issubclassable({typevar_bound})? ...')
            # print(f'{is_object_issubclassable(typevar_bound, False)}')

            # If...
            if (
                # This type variable was bounded or constrained *AND*...
                typevar_bound is not None and
                # These bounded constraints are PEP-noncompliant *AND*...
                #
                # PEP-compliant constraints are *NOT* safely passable to the
                # isinstance() or issubclass() testers, even if they technically
                # are isinstanceable or issubclassable. Why? Consider the
                # "typing.Any" singleton. Under newer Python versions, the
                # "typing.Any" singleton is actually defined as a subclassable
                # type. Although effectively *NO* real-world types subclass
                # "typing.Any", literally *ALL* objects (including types)
                # satisfy the "typing.Any" type hint. Passing "typing.Any" as
                # the second parameter to the issubclass() tester below would
                # thus erroneously reject (rather than silently accept) *ALL*
                # objects as unconditionally violating these bounds.
                not is_hint_pep(typevar_bound) and
                #FIXME: As follows, please:
                #* Unit test with "bound=Any". *sigh*
                #* Integration test with "sqlalchemy". *sigh*

                # These bounded constraints are issubclassable (i.e., an object
                # safely passable as the second parameter to the issubclass()
                # builtin) *AND*...
                #
                # Note that this function is memoized and thus permits *ONLY*
                # positional parameters.
                is_object_issubclassable(
                    typevar_bound,
                    # Ignore unresolvable forward reference proxies (i.e.,
                    # beartype-specific objects referring to user-defined
                    # external types that have yet to be defined).
                    False,
                ) and
                # This PEP-noncompliant isinstanceable type hint is *NOT* a
                # subclass of these bounded constraints...
                not issubclass(hint_child_hint, typevar_bound)  # type: ignore[arg-type]
            ):
                # Raise a type-checking violation.
                raise BeartypeDecorHintPep484TypeVarViolation(
                    message=(
                        f'{exception_prefix}type hint {repr(hint)} '
                        f'originally parametrized by '
                        f'PEP 484 type variable {repr(hint_child_typevar)} '
                        f'subsequently subscripted by '
                        f'child type hint {repr(hint_child_hint)} violating '
                        f"this type variable's bounds or constraints "
                        f'{repr(typevar_bound)}.'
                    ),
                    culprits=(hint_child_hint,),
                )
            # Else, this type variable was either:
            # * Unbounded and unconstrained.
            # * Bounded or constrained by a hint that is *NOT* issubclassable.
            # * Bounded or constrained by an issubclassable object that is the
            #   superclass of this corresponding hint, which thus satisfies
            #   these bounded constraints.
        # Else, this hint is *NOT* a PEP-noncompliant isinstanceable type.

        # Map this type variable to this hint with an optimally efficient
        # one-liner, silently overwriting any prior such mapping of this type
        # variable by either this call or a prior call of this function.
        typevar_to_hint[hint_child_typevar] = hint_child_hint

    # ....................{ RETURN                         }....................
    # Return this table, coerced into an immutable frozen dictionary.
    return FrozenDict(typevar_to_hint)
