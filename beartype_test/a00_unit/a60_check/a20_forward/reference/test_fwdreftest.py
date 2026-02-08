#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype decorator **forward reference tester** unit tests.

This submodule unit tests the
:func:`beartype._check.forward.reference.fwdreftest` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_is_forwardref() -> None:
    '''
    Test the
    :func:`beartype._check.forward.reference.fwdreftest.is_beartype_forwardref`
    tester.
    '''

    # ....................{ LOCALS                         }....................
    # Defer test-specific imports.
    from beartype_test.a00_unit.data.check.forward.data_fwdref import (
        FORWARDREF_ABSOLUTE)
    from beartype._check.forward.reference.fwdreftest import (
        is_beartype_forwardref)
    from beartype_test.a00_unit.data.data_type import Class

    # ....................{ ASSERTS                        }....................
    # Assert that this tester accepts a forward reference proxy.
    assert is_beartype_forwardref(FORWARDREF_ABSOLUTE) is True

    # Assert that this tester rejects an arbitrary class that is *NOT* a forward
    # reference proxy.
    assert is_beartype_forwardref(Class) is False

    # Assert that this tester rejects an arbitrary non-class.
    assert is_beartype_forwardref('A mighty voice invokes thee. Ruin calls') is False
