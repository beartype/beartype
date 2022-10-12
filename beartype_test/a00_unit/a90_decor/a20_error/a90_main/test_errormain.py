#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype main error-handling unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._decor._error.errormain` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_get_beartype_violation() -> None:
    '''
    Test the
    :func:`beartype._decor._error.errormain.get_beartype_violation`
    function.
    '''

    # Defer heavyweight imports.
    from beartype import BeartypeConf
    from beartype.roar import (
        BeartypeCallHintParamViolation,
        BeartypeCallHintReturnViolation,
        BeartypeDecorHintNonpepException,
    )
    from beartype.roar._roarexc import _BeartypeCallHintPepRaiseException
    from beartype.typing import (
        List,
        Tuple,
    )
    from beartype._decor._error.errormain import get_beartype_violation
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

    # Keyword arguments to be unconditionally passed to *ALL* calls of the
    # get_beartype_violation() getter below.
    kwargs = dict(
        func=forest_unknown,
        conf=BeartypeConf(),
    )

    # Assert this function returns the expected exception when passed a
    # parameter annotated by a PEP-compliant type hint failing to shallowly
    # satisfy the type of that type hint.
    violation = get_beartype_violation(
        pith_name='secret_orchard',
        pith_value=(
            'You are in a forest unknown:',
            'The secret orchard.',
        ),
        **kwargs
    )
    assert isinstance(violation, BeartypeCallHintParamViolation)

    # Assert this function returns the expected exception when passed a
    # parameter annotated by a PEP-compliant type hint failing to deeply
    # satisfy the type of that type hint.
    violation = get_beartype_violation(
        pith_name='secret_orchard',
        pith_value=[
            b'I am awaiting the sunrise',
            b'Gazing modestly through the coldest morning',
        ],
        **kwargs
    )
    assert isinstance(violation, BeartypeCallHintParamViolation)

    # Assert this function returns the expected exception when passed another
    # parameter annotated by a PEP-noncompliant type hint failing to shallowly
    # satisfy the type of that type hint.
    violation = get_beartype_violation(
        pith_name='to_bid_you_farewell',
        pith_value=(
            b'Once it came you lied,'
            b"Embracing us over autumn's proud treetops."
        ),
        **kwargs
    )
    assert isinstance(violation, BeartypeCallHintParamViolation)

    # Assert this function returns the expected exception when returning a
    # return value annotated by a PEP-compliant type hint failing to satisfy
    # that type hint.
    violation = get_beartype_violation(
        pith_name='return',
        pith_value=[
            'Sunbirds leave their dark recesses.',
            'Shadows glide the archways.',
        ],
        **kwargs
    )
    assert isinstance(violation, BeartypeCallHintReturnViolation)

    # Assert this function raises the expected exception when passed an
    # unannotated parameter.
    with raises(_BeartypeCallHintPepRaiseException):
        get_beartype_violation(
            pith_name='achromatic_voice',
            pith_value=(
                'And your voice is vast and achromatic,'
                'But still so precious.'
            ),
            **kwargs
        )

    # Assert this function raises the expected exception when passed a
    # parameter annotated by an object that is unsupported as a type hint
    # (i.e., is neither PEP-compliant nor -noncompliant).
    with raises(BeartypeDecorHintNonpepException):
        get_beartype_violation(
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
            **kwargs
        )
