#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint call-time utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.peperror` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ TESTS                             }....................
def test_raise_pep_call_exception() -> None:
    '''
    Test the
    :func:`beartype._decor._code._pep._error.error.peperror.raise_pep_call_exception`
    function.
    '''

    # Defer heavyweight imports.
    from beartype.roar import (
        BeartypeCallHintPepParamException,
        BeartypeCallHintPepReturnException,
        BeartypeDecorHintNonPepException,
        _BeartypeCallHintPepRaiseException,
    )
    from beartype._decor._code._pep._error.peperror import (
        raise_pep_call_exception)
    from beartype._util.hint.data.pep.utilhintdatapepsign import (
        HINT_PEP_SIGN_LIST,
        HINT_PEP_SIGN_TUPLE,
    )
    from typing import Union

    def forest_unknown(
        secret_orchard: HINT_PEP_SIGN_LIST[str],
        achromatic_voice,
        to_bid_you_farewell: str,
        amaranth_symbol: 42,
    ) -> Union[int, HINT_PEP_SIGN_TUPLE[str, ...]]:
        return achromatic_voice

    # Assert this function raises the expected exception when passed a
    # parameter annotated by a PEP-compliant type hint failing to satisfy this
    # type hint.
    with raises(BeartypeCallHintPepParamException):
        raise_pep_call_exception(
            func=forest_unknown,
            pith_name='secret_orchard',
            pith_value=(
                'You are in a forest unknown:',
                'The secret orchard.',
            ),
        )

    # Assert this function raises the expected exception when passed a
    # parameter annotated by a PEP-noncompliant type hint failing to satisfy
    # this type hint.
    with raises(BeartypeCallHintPepParamException):
        raise_pep_call_exception(
            func=forest_unknown,
            pith_name='to_bid_you_farewell',
            pith_value=(
                b'Once it came you lied,'
                b"Embracing us over autumn's proud treetops."
            ),
        )

    # Assert this function raises the expected exception when returning a
    # return value annotated by a PEP-compliant type hint failing to satisfy
    # this type hint.
    with raises(BeartypeCallHintPepReturnException):
        raise_pep_call_exception(
            func=forest_unknown,
            pith_name='return',
            pith_value=[
                'Sunbirds leave their dark recesses.',
                'Shadows glide the archways.',
            ],
        )

    # Assert this function raises the expected exception when passed an
    # unannotated parameter.
    with raises(_BeartypeCallHintPepRaiseException):
        raise_pep_call_exception(
            func=forest_unknown,
            pith_name='achromatic_voice',
            pith_value=(
                'And your voice is vast and achromatic,'
                'But still so precious.'
            ),
        )

    # Assert this function raises the expected exception when passed a
    # parameter annotated by an object that is unsupported as a type hint
    # (i.e., is neither PEP-compliant nor -noncompliant).
    with raises(BeartypeDecorHintNonPepException):
        raise_pep_call_exception(
            func=forest_unknown,
            pith_name='amaranth_symbol',
            pith_value=(
                'I have kept it,'
                'The Amaranth symbol,'
                'Hidden inside the golden shrine'
                'Until we rejoice in the meadow'
                'Of the end.'
                'When we both walk the shadows,'
                'It will set ablaze and vanish.'
            ),
        )
