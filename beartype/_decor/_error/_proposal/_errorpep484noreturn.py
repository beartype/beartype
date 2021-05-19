#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint call-time utilities** (i.e., callables
operating on PEP-compliant type hints intended to be called by dynamically
generated wrapper functions wrapping decorated callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._decor._error._errorsleuth import CauseSleuth
from beartype._util.text.utiltextlabel import label_callable

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS                           }....................
def get_cause_or_none_noreturn(sleuth: CauseSleuth) -> str:
    '''
    Human-readable string describing the failure of the decorated callable to
    *not* return a value in violation of the `PEP 484`_-compliant
    :attr:`typing.NoReturn` type hint.

    Parameters
    ----------
    sleuth : CauseSleuth
        Type-checking error cause sleuth.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''
    assert isinstance(sleuth, CauseSleuth), f'{repr(sleuth)} not cause sleuth.'

    # Return a substring describing this failure intended to be embedded in a
    # longer string.
    return (
        f'"NoReturn"-annotated {label_callable(sleuth.func)} '
        f'returned {sleuth.pith}'
    )
