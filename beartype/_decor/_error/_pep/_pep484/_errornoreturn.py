#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant :attr:`typing.NoReturn` **type hint exception
raisers** (i.e., functions raising human-readable exceptions called by
:mod:`beartype`-decorated callables on the first invalid parameter or return
value failing a type-check against the :pep:`484`-compliant
:attr:`typing.NoReturn` type hint annotating that parameter or return).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._decor._error._errorsleuth import CauseSleuth
from beartype._data.hint.pep.sign.datapepsigns import HintSignNoReturn
from beartype._util.text.utiltextlabel import prefix_callable
from beartype._util.text.utiltextrepr import represent_object

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS                           }....................
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
        f'"NoReturn"-annotated {prefix_callable(sleuth.func)}'
        f'returned {represent_object(sleuth.pith)}'
    )
