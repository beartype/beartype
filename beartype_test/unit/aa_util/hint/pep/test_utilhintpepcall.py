#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint call-time utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.utilhintpepcall` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import typing
from pytest import raises

# ....................{ TESTS                             }....................
#FIXME: To validate exception messages, refactor as follows:
#* In the ""beartype_test.unit.data._data_hint_pep" submodule:
#  * Define a new "PepHintPithUnsatisfiedMetadata" named tuple type defining
#    these fields:
#    * "pith", the desired object *NOT* satisfying this type hint.
#    * "exception_str_regexes", a possibly empty iterable of r''-style
#      uncompiled regular expression strings, each of which matches a substring
#      of the exception message expected to be raised by wrapper functions when
#      passed this pith object.
#  * Refactor the existing "_PepHintMetadata.piths_unsatisfied" field from an
#    iterable of piths to an iterable of "PepHintPithUnsatisfiedMetadata"
#    instances containing the same piths in their "pith" fields.
#* Refactor existing tests in the "beartype_test.unit.pep.p484.test_p484"
#  submodule to:
#  * Capture exception messages raised by such unsatisfied pith objects.
#  * For each regex in the "exception_str_regexes" iterable, validate that the
#    currently captured message matches this regex.
def test_raise_pep_call_exception() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpepcall.raise_pep_call_exception`
    function.
    '''

    # Defer heavyweight imports.
    from beartype.roar import (
        BeartypeCallCheckPepParamException,
        BeartypeCallCheckPepReturnException,
        BeartypeDecorHintPepException,
        _BeartypeUtilRaisePepException,
    )
    from beartype._util.hint.pep.utilhintpepcall import (
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
            param_or_return_name='secret_orchard',
            param_or_return_value=(
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
            param_or_return_name='return',
            param_or_return_value=(
                'Sunbirds leave their dark recesses.',
                'Shadows glide the archways.',
            ),
        )

    # Assert this function raises the expected exception when passed an
    # unannotated parameter.
    with raises(_BeartypeUtilRaisePepException):
        raise_pep_call_exception(
            func=forest_unknown,
            param_or_return_name='achromatic_voice',
            param_or_return_value=(
                'And your voice is vast and achromatic,'
                'But still so precious.'
            ),
        )

    # Assert this function raises the expected exception when passed a
    # parameter annotated by an object that is *not* a PEP-compliant type hint.
    with raises(BeartypeDecorHintPepException):
        raise_pep_call_exception(
            func=forest_unknown,
            param_or_return_name='amaranth_symbol',
            param_or_return_value=(
                'I have kept it,'
                'The Amaranth symbol,',
                'Hidden inside the golden shrine'
                'Until we rejoice in the meadow'
                'Of the end.'
                'When we both walk the shadows,'
                'It will set ablaze and vanish.'
            ),
        )
