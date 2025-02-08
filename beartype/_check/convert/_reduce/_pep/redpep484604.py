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
from beartype.typing import Any
from beartype._data.hint.datahintpep import Hint
from beartype._util.hint.pep.utilpepget import get_hint_pep_args

# ....................{ TESTERS                            }....................
def reduce_hint_pep484604(hint: Hint, exception_prefix: str, **kwargs) -> Hint:
    '''
    Reduce the passed :pep:`484`- or :pep:`604`-compliant union to the
    ignorable :obj:`typing.Any` singleton if this union is subscripted by one or
    more **ignorable child hints** (i.e., hints that themselves reduce to the
    ignorable :obj:`typing.Any` singleton) *or* preserve this union as is
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
    possible hints (e.g., :class:`object`, :attr:`typing.Any`), which are so
    wide as to constrain nothing and convey no meaningful semantics. A union of
    one or more shallowly ignorable child hints is thus the widest possible
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
    Hint
        Either:

        * If this union is subscripted by one or more ignorable child hints,
          :obj:`typing.Any`.
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

    # Assert this union to be subscripted by two or more child hints.
    #
    # Note this should *ALWAYS* be the case, as:
    # * The unsubscripted "typing.Union" type hint factory is explicitly listed
    #   in the "HINTS_REPR_IGNORABLE_SHALLOW" set and should thus have already
    #   been ignored when present.
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
        hint_or_sane_child = reduce_hint_child(hint_child, kwargs)

        # If this sanified child hint is "Any", this child hint is ignorable. By
        # set logic, a union subscripted by one or more ignorable child hints is
        # itself ignorable. In this case...
        if hint_or_sane_child is Any:
            # Reduce this entire union to the ignorable "Any" singleton.
            hint = Any  # pyright: ignore

            # Immediately halt this iteration.
            break
        # Else, this sanified child hint is unignorable.

        # Increment the 0-based index of the currently iterated child hint.
        hint_childs_index += 1

    # ....................{ RETURN                         }....................
    # Return this possibly reduced union.
    return hint
