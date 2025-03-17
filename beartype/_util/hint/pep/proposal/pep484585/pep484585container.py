#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **container type hint
utilities** (i.e., low-level callables generically applicable to both
:pep:`484`- and :pep:`585`-compliant container type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Annotated,
    Collection,
    Tuple,
)
from beartype._data.hint.datahintpep import Hint
from collections.abc import (
    ItemsView as ItemsViewABC,
)

# ....................{ REDUCERS                           }....................
def reduce_hint_pep484585_itemsview(
    hint: Hint, exception_prefix: str, **kwargs) -> Hint:
    '''
    Reduce the passed :pep:`484`- or :pep:`585`-compliant **items view type
    hint** (i.e., of the form ``(collections.abc|typing).ItemsView[{hint_key},
    {hint_value}]``) to a more suitable type hint better supported by
    :mod:`beartype`.

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : Hint
        Items view type hint to be reduced.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this hint in
        exception messages raised by this reducer.

    All remaining passed arguments are silently ignored.

    Returns
    -------
    Hint
        More suitable type hint better supported by :mod:`beartype`.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.proposal.pep484585.pep484585 import (
        get_hint_pep484585_args)
    from beartype._util.hint.pep.utilpeptest import is_hint_pep_subscripted

    # Reduced hint to be returned, defaulting to the abstract base class (ABC)
    # of *ALL* items views.
    hint_reduced: Hint = ItemsViewABC  # pyright: ignore

    # If this hint is subscripted by one or more child type hints...
    if is_hint_pep_subscripted(hint):
        # Defer heavyweight imports.
        from beartype.vale import IsInstance

        # Child key and value type hints subscripting this parent type hint.
        hint_key, hint_value = get_hint_pep484585_args(  # type: ignore[misc]
            hint=hint, args_len=2, exception_prefix=exception_prefix)

        # Reduce this hint to a PEP 593-compliant hint annotating...
        hint_reduced = Annotated[
            # A collection of 2-tuples "(key, value)" -- which, interestingly,
            # is literally what an items view is.
            #
            # Look. @beartype doesn't make the insane rules. It just enforces
            # them. We pretend this makes the world a better place.
            Collection[Tuple[hint_key, hint_value]],  # type: ignore[assignment, valid-type]
            # Constrain this collection to be an instance of the expected
            # "collections.abc.ItemsView" abstract base class (ABC).
            IsInstance[ItemsViewABC],
        ]
    # Else, this hint is subscripted by *NO* child type hints. In this case,
    # reduce to type-checking that an items view is an instance of this ABC.

    # Return this reduced hint.
    return hint_reduced
