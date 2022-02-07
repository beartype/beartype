#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype abby unit tests.**

This submodule unit tests the public API of the public
:mod:`beartype.abby` subpackage.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning
from beartype_test.util.mark.pytmark import ignore_warnings

# ....................{ TESTS                             }....................
# Prevent pytest from capturing and displaying all expected non-fatal
# beartype-specific warnings emitted by the @beartype decorator below. Urgh!
@ignore_warnings(BeartypeDecorHintPep585DeprecationWarning)
def test_api_abby_die_if_unbearable_pass() -> None:
    '''
    Test successful usage of the private
    :class:`beartype.abby.die_if_unbearable` tester.

    Note that the corresponding ``test_api_abby_die_if_unbearable_fail`` test resides
    under the :mod:`beartype_test.a20_api.abby` subpackage for orthogonality
    with other core API unit tests.
    '''

    # Defer heavyweight imports.
    from beartype.abby import die_if_unbearable
    from beartype.roar import BeartypeAbbyHintViolation
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPithUnsatisfiedMetadata)
    from beartype_test.util.hint.pythint import iter_hints_piths_meta
    from pytest import raises

    # For each predefined type hint and associated metadata...
    for hint_pith_meta in iter_hints_piths_meta():
        # Type hint to be type-checked.
        hint = hint_pith_meta.hint_meta.hint

        # Object to type-check against this type hint.
        pith = hint_pith_meta.pith

        # If this pith violates this hint...
        if isinstance(hint_pith_meta.pith_meta, HintPithUnsatisfiedMetadata):
            # Assert this validator raises the expected exception when passed
            # this pith and hint.
            with raises(BeartypeAbbyHintViolation) as exception_info:
                die_if_unbearable(pith, hint)

            # Exception message raised by this wrapper function.
            exception_str = str(exception_info.value)

            # Assert this validator successfully replaced the irrelevant
            # substring previously prefixing this message.
            assert exception_str.startswith('Object ')
        # Else, this pith satisfies this hint. In this case...
        else:
            # Assert this validator raises *NO* exception when passed this pith
            # and hint.
            die_if_unbearable(pith, hint)


# Prevent pytest from capturing and displaying all expected non-fatal
# beartype-specific warnings emitted by the @beartype decorator below. Urgh!
@ignore_warnings(BeartypeDecorHintPep585DeprecationWarning)
def test_api_abby_is_bearable_pass() -> None:
    '''
    Test successful usage of the private
    :class:`beartype.abby.is_bearable` tester.

    Note that the corresponding ``test_api_abby_is_bearable_fail`` test resides
    under the :mod:`beartype_test.a20_api.abby` subpackage for orthogonality
    with other core API unit tests.
    '''

    # Defer heavyweight imports.
    from beartype.abby import is_bearable
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPithUnsatisfiedMetadata)
    from beartype_test.util.hint.pythint import iter_hints_piths_meta

    # For each predefined type hint and associated metadata...
    for hint_pith_meta in iter_hints_piths_meta():
        # Type hint to be type-checked.
        hint = hint_pith_meta.hint_meta.hint

        # Object to type-check against this type hint.
        pith = hint_pith_meta.pith

        # If this pith violates this hint...
        if isinstance(hint_pith_meta.pith_meta, HintPithUnsatisfiedMetadata):
            # Assert this tester returns false when passed this pith and hint.
            assert is_bearable(pith, hint) is False
        # Else, this pith satisfies this hint. In this case...
        else:
            # Assert this tester returns true when passed this pith and hint.
            assert is_bearable(pith, hint) is True
