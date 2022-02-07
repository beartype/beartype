#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint call-time utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._decor._error.errormain` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_raise_pep_call_exception() -> None:
    '''
    Test the
    :func:`beartype._decor._error.errormain.raise_pep_call_exception`
    function.
    '''

    # Defer heavyweight imports.
    from beartype.roar import (
        BeartypeCallHintParamViolation,
        BeartypeCallHintReturnViolation,
        BeartypeDecorHintNonpepException,
    )
    from beartype.roar._roarexc import _BeartypeCallHintPepRaiseException
    from beartype._decor._error.errormain import (
        raise_pep_call_exception)
    from beartype.typing import (
        List,
        Tuple,
    )
    from pytest import raises
    from typing import Union

    def forest_unknown(
        secret_orchard: List[str],
        achromatic_voice,
        to_bid_you_farewell: str,
        amaranth_symbol: 42,
    ) -> Union[int, Tuple[str, ...]]:
        '''
        Arbitrary callable exercised below.
        '''

        return achromatic_voice

    # Assert this function raises the expected exception when passed a
    # parameter annotated by a PEP-compliant type hint failing to shallowly
    # satisfy the type of that type hint.
    with raises(BeartypeCallHintParamViolation):
        raise_pep_call_exception(
            func=forest_unknown,
            pith_name='secret_orchard',
            pith_value=(
                'You are in a forest unknown:',
                'The secret orchard.',
            ),
        )

    # Assert this function raises the expected exception when passed a
    # parameter annotated by a PEP-compliant type hint failing to deeply
    # satisfy the type of that type hint.
    with raises(BeartypeCallHintParamViolation):
        raise_pep_call_exception(
            func=forest_unknown,
            pith_name='secret_orchard',
            pith_value=[
                b'I am awaiting the sunrise',
                b'Gazing modestly through the coldest morning',
            ],
        )

    # Assert this function raises the expected exception when passed another
    # parameter annotated by a PEP-noncompliant type hint failing to shallowly
    # satisfy the type of that type hint.
    with raises(BeartypeCallHintParamViolation):
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
    # that type hint.
    with raises(BeartypeCallHintReturnViolation):
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
    with raises(BeartypeDecorHintNonpepException):
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
