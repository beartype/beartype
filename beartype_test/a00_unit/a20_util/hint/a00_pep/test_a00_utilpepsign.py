#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-compliant type hint sign getter** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.utilpepsign` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_get_hint_pep_sign(hints_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_sign` getter.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPepSignException
    from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign
    from beartype_test.a00_unit.data.hint.data_hint import (
        HINTS_NONPEP, NonpepCustomFakeTyping)
    from pytest import raises

    # Assert this getter returns the expected unsubscripted "typing" attribute
    # for all PEP-compliant type hints associated with such an attribute.
    for hint_pep_meta in hints_pep_meta:
        assert get_hint_pep_sign(hint_pep_meta.hint) is hint_pep_meta.pep_sign

    # Assert this getter raises the expected exception for an instance of a
    # class erroneously masquerading as a "typing" class.
    with raises(BeartypeDecorHintPepSignException):
        # Localize this return value to simplify debugging.
        hint_nonpep_sign = get_hint_pep_sign(NonpepCustomFakeTyping())

    # Assert this getter raises the expected exception for non-"typing" hints.
    for hint_nonpep in HINTS_NONPEP:
        with raises(BeartypeDecorHintPepSignException):
            # Localize this return value to simplify debugging.
            hint_nonpep_sign = get_hint_pep_sign(hint_nonpep)
