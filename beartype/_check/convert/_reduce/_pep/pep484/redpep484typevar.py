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
from beartype._data.typing.datatypingport import (
    Hint,
    Pep484646TypeArgToHint,
    TupleHints,
)
from beartype._data.typing.datatyping import TuplePep484646TypeArgs
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
    get_hint_pep_typeargs,
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
          by :mod:`beartype._check.convert.convmain` sanifiers after
          sanitizing the possibly PEP-noncompliant parent hint of this child
          hint into a fully PEP-compliant parent hint).
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    All remaining keyword-only parameters are silently ignored.

    Returns
    -------
    HintSane
        Either:

        * If this type variable is **recursive** (i.e., previously transitively
          mapped to itself by a prior call to this reducer), this type variable
          *must* be ignored to avoid infinite recursion. In this case, the
          :data:`.HINT_SANE_RECURSIVE` singleton.
        * Else if the type variable lookup table encapsulated by the passed
          sanified parent type hint metadata maps this type variable to another
          type hint, the latter.
        * Else if this type variable is both unbounded and unconstrained, this
          type variable is ignorable. In this case, the
          :data:`.HINT_SANE_IGNORABLE` singleton.
        * Else, this type variable's lover-level bounds or constraints.
    '''
    # print(f'Reducing PEP 484 type variable {hint} with parent hint {hint_parent_sane}...')

    # ....................{ PHASE                          }....................
    # This reducer is divided into four phases:
    # 0. The zeroth phase decides whether this type variable is recursive.
    # 1. The first phase maps this type variable to its associated target hint
    #    via lookup table associated with this type variable (if any).
    # 2. The second phase reduces this type variable to its bounded constraints
    #    (if any).
    # 3. The third phase decides the recursion guard for this type variable.
    #
    # All phases are non-trivial. The output of each phase is sanified hint
    # metadata (i.e., a "HintSane" object) containing the result of the decision
    # problem decided by that phase.

    # ....................{ PHASE ~ 0 : recurse            }....................
    # If this type variable is recursive (i.e., previously transitively mapped
    # to itself by a prior call to this reducer), ignore this type variable to
    # avoid infinite recursion.
    if is_hint_recursive(
        hint=hint,
        hint_parent_sane=hint_parent_sane,
        hint_recursable_depth_max=_TYPEVAR_RECURSABLE_DEPTH_MAX,
    ):
        # print(f'Ignoring recursive type variable {hint} with parent {hint_parent_sane}!')
        return HINT_SANE_RECURSIVE
    # Else, this type variable is *NOT* recursive.

    # ....................{ PHASE ~ 1 : lookup             }....................
    # Reduced hint to be returned, defaulting to this type variable.
    hint_reduced = hint

    # If...
    if (
        # This type variable is not a root hint and thus has a parent hint
        # *AND*...
        hint_parent_sane is not None and
        # A parent hint of this type variable maps one or more type variables...
        hint_parent_sane.typearg_to_hint
    ):
        # Type variable lookup table of this parent hint, localized for
        # usability and negligible efficiency.
        typearg_to_hint = hint_parent_sane.typearg_to_hint

        # If a parent hint of this type variable maps exactly one type variable,
        # prefer a dramatically faster and simpler approach.
        if len(typearg_to_hint) == 1:
            # Hint mapped to by this type variable if one or more parent hints
            # previously mapped this type variable to a hint *OR* this hint as
            # is otherwise (i.e., if this type variable is unmapped).
            #
            # Note that this one-liner looks ridiculous, but actually works.
            # More importantly, this is the fastest way to accomplish this.
            hint_reduced = typearg_to_hint.get(hint, hint)  # type: ignore[call-overload]
        # Else, a parent hint of this type variable mapped two or more type
        # variables. In this case, fallback to a slower and more complicated
        # approach that avoids worst-case edge cases. This includes recursion in
        # type variable mappings, which arises in non-trivial class hierarchies
        # involving two or more generics subscripted by two or more type
        # variables that circularly cycle between one another: e.g.,
        #     from typing import Generic
        #     class GenericRoot[T](Generic[T]): pass
        #
        #     # This directly maps "{T: S}".
        #     class GenericLeaf[S](GenericRoot[S]): pass
        #
        #     # This directly maps "{S: T}", which then combines with the above
        #     # mapping to indirectly map "{S: T, T: S}". Clearly, this indirect
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
            typearg_to_hint_stack = typearg_to_hint.copy()

            #FIXME: [SPEED] *INEFFICIENT.* This has to be done either way, but
            #rather than reperform this O(n) algorithm on every single instance
            #of this type variable, this algorithm should simply be performed
            #exactly *ONCE* in the
            #reduce_hint_pep484646_subbed_typeargs_to_hints() reducer. Please
            #refactor this iteration over there *AFTER* the dust settles here.
            #FIXME: Actually, it's unclear how exactly this could be refactored
            #into the reduce_hint_pep484646_subbed_typeargs_to_hints()
            #reducer. This reduction here only searches for a single typevar in
            #O(n) time. Refactoring this over to
            #reduce_hint_pep484646_subbed_typeargs_to_hints() would require
            #generalizing this into an O(n**2) algorithm there, probably. Yow!

            # While...
            while (
                # This stack still contains one or more type variables that have
                # yet to be reduced by this iteration *AND*...
                typearg_to_hint_stack and
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
                hint_reduced = typearg_to_hint_stack.pop(
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

    # ....................{ PHASE ~ 2 : bounds             }....................
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

    # ....................{ PHASE ~ 3 : guard              }....................
    # Decide the recursion guard protecting this possibly recursive type
    # variable against infinite recursion.
    #
    # Note that this guard intentionally applies to the original unreduced type
    # variable rather than the newly reduced hint decided by the prior phase.
    # Thus, we pass "hint_recursable=hint" rather than
    # "hint_recursable=hint_reduced".
    hint_sane = make_hint_sane_recursable(
        # The recursable form of this type variable is its original unreduced
        # form tested by the is_hint_recursive() recursion guard above.
        hint_recursable=hint,
        # The non-recursable form of this type variable is its new reduced form.
        hint_nonrecursable=hint_reduced,
        hint_parent_sane=hint_parent_sane,
    )

    # ....................{ RETURN                         }....................
    # Return this metadata.
    return hint_sane

# ....................{ PRIVATE ~ constants                }....................
_TYPEVAR_RECURSABLE_DEPTH_MAX = 0
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
