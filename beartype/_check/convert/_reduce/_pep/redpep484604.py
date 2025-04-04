#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- or :pep:`604`-compliant **union reducers** (i.e.,
low-level callables converting union type hints to lower-level type hints more
readily consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.metadata.hint.hintsane import (
    HINT_IGNORABLE,
    HintOrSane,
)
from beartype._data.hint.datahintpep import Hint
from beartype._util.hint.pep.utilpepget import get_hint_pep_args

# ....................{ TESTERS                            }....................
def reduce_hint_pep484604(hint: Hint, exception_prefix: str, **kwargs) -> (
    HintOrSane):
    '''
    Reduce the passed :pep:`484`- or :pep:`604`-compliant union to the ignorable
    :data:`.HINT_IGNORABLE` singleton if this union is subscripted by one or
    more **ignorable child hints** (i.e., hints that themselves reduce to the
    ignorable :data:`.HINT_IGNORABLE` singleton) *or* preserve this union as is
    otherwise (i.e., if this union is subscripted by *no* ignorable child
    hints).

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Design
    ------
    This reducer recursively reduces all child hints subscripting this union as
    a necessary prerequisite to deciding whether one or more of these hints are
    ignorable. Since one or more of these child hints may require an uncached
    reduction in the worst case, reducing unions *also* requires an uncached
    reduction in the worst case. This is that case.

    This reducer ignores all union type hint factories subscripted by one or
    more ignorable child hints, including:

    * The :pep:`484`-compliant :obj:`typing.Optional` (e.g.,
      ``typing.Optional[object]``).
    * The :pep:`484`-compliant :obj:`typing.Union` (e.g.,
      ``typing.Union[typing.Any, bool]``).
    * All :pep:`604`-compliant new-style unions (e.g., ``bool | object``).

    Why? Because unions are only as narrow as their widest child type hints.
    Shallowly ignorable hints are ignorable exactly because they are the widest
    possible hints (e.g., :class:`object`, :data:`.HINT_IGNORABLE`), which are
    so wide as to constrain nothing and convey no meaningful semantics. A union
    of one or more shallowly ignorable child hints is thus the widest possible
    union, which is so wide as to constrain nothing and convey no meaningful
    semantics. There exist a countably infinite number of possible unions
    subscripted by one or more ignorable child hints. Ergo, these subscriptions
    *cannot* be explicitly listed in the
    :data:`beartype._data.hint.pep.datapeprepr.HINTS_REPR_IGNORABLE_SHALLOW`
    set. Instead, these subscriptions are dynamically detected by this tester at
    runtime and thus referred to as **deeply ignorable unions.**

    Parameters
    ----------
    hint : HintPep695TypeAlias
        Union hint to be reduced.
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    All remaining passed keyword parameters are passed to the parent
    :func:`beartype._check.convert._reduce.redhint.reduce_hint` function
    recursively called by this reducer.

    Returns
    -------
    HintOrSane
        Either:

        * If this union is subscripted by one or more ignorable child hints,
          :data:`.HINT_IGNORABLE`.
        * Else, this union unmodified.
    '''
    # print(f'[484/604] Detecting union {repr(hint)} ignorability...')

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype._check.convert._reduce.redhint import reduce_hint_child

    # ....................{ LOCALS                         }....................
    # Tuple of the two or more child hints subscripting this union.
    hint_childs = get_hint_pep_args(hint)

    # 0-based index of the currently iterated child hint.
    hint_childs_index = 0

    # Number of these child hints.
    hint_childs_len = len(hint_childs)

    # If this union is subscripted by *NO* child hints, this union is ignorable.
    # In this case, reduce this union to the ignorable "HINT_IGNORABLE"
    # singleton.
    #
    # Why are unsubscripted unions ignorable? First, consider the case of the
    # unsubscripted "typing.Union" type hint factory. When unsubscripted, this
    # factory semantically expands to the implicit "Union[Any]" singleton by the
    # same argument. Since PEP 484 stipulates that a union of one type
    # semantically reduces to only that type, "Union[Any]" semantically reduces
    # to merely "Any". Despite their semantic equivalency, however, these
    # objects remain syntactically distinct with respect to object
    # identification: e.g.,
    #     >>> Union is not Union[Any]
    #     True
    #     >>> Union is not Any
    #     True
    #
    # This intentionally excludes:
    # * The "Union[Any]" and "Union[object]" singletons, since the "typing"
    #   module physically reduces:
    #   * "Union[Any]" to merely "Any" (i.e., "Union[Any] is Any"), which is
    #     already ignored by reducers elsewhere.
    #   * "Union[object]" to merely "object" (i.e., "Union[object] is
    #     object"), which is already ignored by reducers elsewhere.
    # * The "Union" singleton subscripted by one or more ignorable type hints
    #   contained in this set (e.g., "Union[Any, bool, str]"). Since there exist
    #   a countably infinite number of these subscriptions, these subscriptions
    #   are recursively detected below.
    #
    # Next, consider the case of the unsubscripted "typing.Optional" type hint
    # factory. When unsubscripted, this factory semantically expands to the
    # implicit "Optional[Any]" singleton by the same argument. Since PEP 484
    # also stipulates that all "Optional[t]" singletons semantically expand to
    # "Union[t, type(None)]" singletons for arbitrary arguments "t",
    # "Optional[Any]" semantically expands to merely "Union[Any, type(None)]".
    # Since all unions subscripted by "Any" semantically reduce to merely "Any",
    # the "Optional" singleton also reduces to merely "Any".
    #
    # This intentionally excludes "Optional[type(None)]", which the "typing"
    # module physically reduces to merely "type(None)". *shrug*
    if not hint_childs_len:
        return HINT_IGNORABLE
    # Else, this union is subscripted by one or more child hints.

    # Assert this union to be subscripted by two or more child hints.
    #
    # Note this should *ALWAYS* be the case, as:
    # * The "typing" module explicitly prohibits empty union subscription: e.g.,
    #       >>> typing.Union[]
    #       SyntaxError: invalid syntax
    #       >>> typing.Union[()]
    #       TypeError: Cannot take a Union of no types.
    # * The "typing" module reduces unions of one child hint to that hint: e.g.,
    #     >>> import typing
    #     >>> typing.Union[int]
    #     int
    assert hint_childs_len >= 2, (
        f'{exception_prefix}'
        f'PEP 484 or 604 union type hint {repr(hint)} either unsubscripted '
        f'or subscripted by only one child type hint.'
    )

    # ....................{ REDUCE                         }....................
    # Note that the low-level C-based "types.UnionType" class underlying PEP
    # 604-compliant |-style unions (e.g., "int | float") imposes no constraints
    # and is thus also semantically synonymous with the ignorable "typing.Any"
    # singleton. Nonetheless, that class *CANNOT* be instantiated from Python
    # code: e.g.,
    #     >>> import types
    #     >>> types.UnionType(int, bool)
    #     TypeError: cannot create 'types.UnionType' instances
    #
    # Likewise, that class *CANNOT* be subscripted. It follows that there exists
    # no meaningful equivalent of shallow type-checking for these unions. While
    # trivially feasible, listing "<class 'types.UnionType'>" here would only
    # prevent callers from meaningfully type-checking these unions passed as
    # valid parameters or returned as valid returns: e.g.,
    #     @beartype
    #     def muh_union_printer(muh_union: UnionType) -> None: print(muh_union)
    #
    # Ergo, we intentionally omit that class from consideration here.

    #FIXME: [SPEED] It'd be *REALLY* nice if this reducer completely
    #reconstituted the union it returns from the child hints it reduces below.
    #Currently, this reducer doesn't do that. Why? Because the rest of the
    #codebase isn't quite ready to support unions that contain *TOTALLY
    #PEP-VIOLATING OBJECTS* -- namely, "HintSane" objects. To support this,
    #we'll need to at least:
    #* Generalize sanify_hint_child() to avoid resanifying the passed hint if
    #  the passed hint is already a "HintSane" object. In that case, the passed
    #  hint should simply be returned unmodified.
    #* Probably lots else. Kinda seems dangerous, the more we consider it.

    # For each child hint of this union...
    while hint_childs_index < hint_childs_len:
        # Currently visited child hint of this union.
        hint_child = hint_childs[hint_childs_index]
        # print(f'Recursively reducing {hint} child {hint_child}...')
        # print(f'hints_overridden: {kwargs["hints_overridden"]}')

        # Sane child hint sanified from this possibly insane child hint if
        # sanifying this child hint did not generate supplementary metadata *OR*
        # that metadata otherwise (i.e., if sanifying this child hint generated
        # supplementary metadata).
        hint_sane_child = reduce_hint_child(hint_child, kwargs)

        # If...
        if (
            # This sanified child hint is ignorable *AND*...
            hint_sane_child is HINT_IGNORABLE and
            # This child hint is *NOT* a transitive parent of itself...
            #
            # If this child hint is a transitive parent of itself, this child
            # hint has already been visited by the current breadth-first search
            # (BFS) and so constitutes a recursive child hint. Although
            # recursive child hints are ignorable in (most) other contexts,
            # recursive child hints are *NOT* ignorable in the usual sense
            # inside union hints. In this context, a recursive child hint is
            # simply a union hint to be shallowly rather than deeply ignored.
            # That is, a recursive child hint of a union does *NOT* propagate
            # its ignorability to that union. That union remains unignorable
            # regardless of whether that union contains a recursive child hint.
            #
            # Consider a PEP 695-compliant recursive type alias trivially
            # aliasing a union: e.g.,
            #     type recursive_union = int | recursive_union
            #
            # That union contains the recursive child hint "recursive_union" but
            # is *NOT* ignorable. Rather, that union semantically reduces to the
            # trivial type "int".
            hint not in hint_sane_child.recursable_hints
        ):
            # print(f'Ignoring union {hint} with ignorable child {hint_sane_child}...')
            # Reduce this entire union to the "HINT_IGNORABLE" singleton. Why?
            # By set logic, a union subscripted by one or more ignorable child
            # hints is itself ignorable.
            return HINT_IGNORABLE
        # Else, this sanified child hint is unignorable.

        # Increment the 0-based index of the currently iterated child hint.
        hint_childs_index += 1

    # ....................{ RETURN                         }....................
    # Return this possibly reduced union.
    return hint
