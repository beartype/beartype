#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`675`-compliant **literal string type hint reducers** (i.e.,
low-level callables converting objects created by by subscripting the
:obj:`typing.Final` type hint factory to lower-level type hints more readily
consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Type

# ....................{ REDUCERS                           }....................
#FIXME: Unit test us up, please.
def reduce_hint_pep675(**kwargs) -> Type[str]:
    '''
    Reduce the passed :pep:`675`-compliant **literal string type hint** (i.e.,
    :obj:`typing.LiteralString` singleton) to the builtin :class:`str` class as
    advised by :pep:`675` when performing runtime type-checking.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    All passed keyword parameters are silently ignored.

    Returns
    -------
    Type[str]
        Builtin :class:`str` class.
    '''

    # Unconditionally reduce this hint to the builtin "str" class.
    return str
