#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`484`-compliant :attr:`typing.NoReturn` **type hint violation
describers** (i.e., functions returning human-readable strings explaining
violations of :pep:`484`-compliant :attr:`typing.NoReturn` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.hint.pep.sign.datapepsigns import HintSignNoReturn
from beartype._decor._error._errorsleuth import CauseSleuth
from beartype._decor._error._errortext import represent_pith
from beartype._util.text.utiltextlabel import prefix_callable

# ....................{ GETTERS                            }....................
def get_cause_or_none_noreturn(sleuth: CauseSleuth) -> str:
    '''
    Human-readable string describing the failure of the decorated callable to
    *not* return a value in violation of the :pep:`484`-compliant
    :attr:`typing.NoReturn` type hint.

    Parameters
    ----------
    sleuth : CauseSleuth
        Type-checking error cause sleuth.
    '''
    assert isinstance(sleuth, CauseSleuth), f'{repr(sleuth)} not cause sleuth.'
    assert sleuth.hint_sign is HintSignNoReturn, (
        f'{repr(sleuth.hint)} not HintSignNoReturn.')

    # Return a substring describing this failure intended to be embedded in a
    # longer string.
    return (
        f'{prefix_callable(sleuth.func)} with PEP 484 return type hint '
        f'"typing.NoReturn" returned {represent_pith(sleuth.pith)}'
    )
