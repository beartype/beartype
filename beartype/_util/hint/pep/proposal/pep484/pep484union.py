#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **union type hint utilities** (i.e.,
callables generically applicable to :pep:`484`-compliant :attr:`typing.Union`
subscriptions).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep484Exception
from beartype.typing import Union
from beartype._data.hint.datahintpep import (
    Hint,
    TupleHints,
)
from beartype._util.cache.utilcachecall import callable_cached

# ....................{ FACTORIES                          }....................
@callable_cached
def make_hint_pep484_union(hints: TupleHints) -> Hint:
    '''
    :pep:`484`-compliant **union type hint** (:attr:`typing.Union`
    subscription) synthesized from the passed tuple of two or more
    PEP-compliant type hints if this tuple contains two or more items, the one
    PEP-compliant type hint in this tuple if this tuple contains only one item,
    *or* raise an exception otherwise (i.e., if this tuple is empty).

    This factory is memoized for efficiency. Technically, the
    :attr:`typing.Union` type hint factory already caches its subscripted
    arguments. Pragmatically, that caching is slow and thus worth optimizing
    with trivial optimization on our end. Moreover, this factory is called by
    the performance-sensitive
    :func:`beartype._check.convert._convcoerce.coerce_hint_any` coercer in an
    early-time code path of the :func:`beartype.beartype` decorator. Optimizing
    this factory thus optimizes :func:`beartype.beartype` itself.

    Parameters
    ----------
    hint : TupleHints
        Type hint to be inspected.

    Returns
    -------
    Hint
        Either:

        * If this tuple contains two or more items, the union type hint
          synthesized from these items.
        * If this tuple contains only one item, this item as is.

    Raises
    ------
    BeartypeDecorHintPep484Exception
        If this tuple is empty.
    '''
    assert isinstance(hints, tuple), f'{repr(hints)} not tuple.'

    # If this tuple is empty, raise an exception.
    if not hints:
        raise BeartypeDecorHintPep484Exception('"hints" tuple empty.')
    # Else, this tuple contains one or more child type hints.

    # These are the one-liners of our lives.
    return Union.__getitem__(hints)  # type: ignore[return-value]
