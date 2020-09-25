#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint call-time utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.utilhintpeperror` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import typing
from pytest import raises

# ....................{ TESTS                             }....................
def test_raise_pep_call_exception() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.error.error.utilhintpeperror.raise_pep_call_exception`
    function.
    '''

    # Defer heavyweight imports.
    from beartype.roar import (
        BeartypeCallCheckPepParamException,
        BeartypeCallCheckPepReturnException,
        BeartypeDecorHintPepException,
        _BeartypeUtilRaisePepException,
    )
    from beartype._util.hint.pep.error.utilhintpeperror import (
        raise_pep_call_exception)

    def forest_unknown(
        secret_orchard: typing.List[str],
        achromatic_voice,
        amaranth_symbol: str,
    ) -> typing.Union[int, typing.Tuple[str, ...]]:
        return achromatic_voice

    # Assert this function raises the expected exception when passed a
    # parameter annotated by a PEP-compliant type hint failing to satisfy this
    # type hint.
    with raises(BeartypeCallCheckPepParamException):
        raise_pep_call_exception(
            func=forest_unknown,
            pith_name='secret_orchard',
            pith_value=(
                'You are in a forest unknown:',
                'The secret orchard.',
            ),
        )

    # Assert this function raises the expected exception when returning a
    # return value annotated by a PEP-compliant type hint failing to satisfy
    # this type hint.
    with raises(BeartypeCallCheckPepReturnException):
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
    with raises(_BeartypeUtilRaisePepException):
        raise_pep_call_exception(
            func=forest_unknown,
            pith_name='achromatic_voice',
            pith_value=(
                'And your voice is vast and achromatic,'
                'But still so precious.'
            ),
        )

    # Assert this function raises the expected exception when passed a
    # parameter annotated by an object that is *not* a PEP-compliant type hint.
    with raises(BeartypeDecorHintPepException):
        raise_pep_call_exception(
            func=forest_unknown,
            pith_name='amaranth_symbol',
            pith_value=(
                'I have kept it,'
                'The Amaranth symbol,',
                'Hidden inside the golden shrine'
                'Until we rejoice in the meadow'
                'Of the end.'
                'When we both walk the shadows,'
                'It will set ablaze and vanish.'
            ),
        )
