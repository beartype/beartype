#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
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
def reduce_hint_pep484604(hint: Hint, **kwargs) -> Hint:
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

    This reducer ignores all union factories subscripted by one or more
    ignorable child hints, including:

    * The :pep:`484`-compliant :obj:`typing.Optional` (e.g.,
      ``typing.Optional[object]``).
    * The :pep:`484`-compliant :obj:`typing.Union` (e.g.,
      ``typing.Union[typing.Any, bool]``).
    * All :pep:`604`-compliant new-style unions (e.g., ``bool | object``).

    Why? Because unions are by definition only as narrow as their widest child
    hint. However, shallowly ignorable type hints are ignorable precisely
    because they are the widest possible hints (e.g., :class:`object`,
    :attr:`typing.Any`), which are so wide as to constrain nothing and convey no
    meaningful semantics. A union of one or more shallowly ignorable child hints
    is thus the widest possible union, which is so wide as to constrain nothing
    and convey no meaningful semantics. Since there exist a countably infinite
    number of possible :data:`Union` subscriptions by one or more ignorable type
    hints, these subscriptions *cannot* be explicitly listed in the
    :data:`beartype._data.hint.pep.datapeprepr.HINTS_REPR_IGNORABLE_SHALLOW`
    frozenset. Instead, these subscriptions are dynamically detected by this
    tester at runtime and thus referred to as **deeply ignorable type hints.**

    Parameters
    ----------
    hint : HintPep695Type
        Union to be reduced.

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

    # Avoid circular import dependencies.
    from beartype._check.convert._reduce.redhint import reduce_hint_child

    # Tuple of the two or more child hints subscripting this union.
    hint_childs = get_hint_pep_args(hint)

    # For each child hint subscripting this union...
    for hint_child in hint_childs:
        # print(f'Recursively reducing {hint} child {hint_child}...')
        # print(f'hints_overridden: {kwargs["hints_overridden"]}')

        #FIXME: [SPEED] Inefficient. Each call to reduce_hint_child()
        #repetitiously removes the same three keys from "**kwargs". Given how
        #common unions are, this gets non-negligible kinda fast. *sigh*

        # Lower-level child hint reduced from this higher-level child hint.
        hint_child_reduced = reduce_hint_child(hint=hint_child, **kwargs)

        # If this reduced child hint is "Any", this child hint is ignorable.
        # However, by set logic, a union subscripted by one or more ignorable
        # child hints is itself ignorable. In this case, reduce this entire
        # union to "Any" as well.
        if hint_child_reduced is Any:
            return Any  # pyright: ignore
        # Else, this reduced child hint is *NOT* "Any". In this case, continue
        # to the next child hint.
    # Else, this union is subscripted by *NO* ignorable child hints. Ergo, this
    # union is unignorable.

    # Return this union unmodified.
    return hint
