#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward reference tester** unit tests.

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
    :func:`beartype._check.forward.reference.fwdreftest.is_beartype_ref_proxy`
    tester.
    '''

    # ....................{ LOCALS                         }....................
    # Defer test-specific imports.
    from beartype._check.forward.reference.fwdreftest import (
        is_beartype_ref_proxy)
    from beartype_test.a00_unit.data.data_type import Class
    from beartype_test.a00_unit.data.pep.pep484.forward.data_pep484ref_proxy import (
        FORWARDREF_ABSOLUTE)

    # ....................{ ASSERTS                        }....................
    # Assert that this tester accepts a forward reference proxy.
    assert is_beartype_ref_proxy(FORWARDREF_ABSOLUTE) is True

    # Assert that this tester rejects an arbitrary class that is *NOT* a forward
    # reference proxy.
    assert is_beartype_ref_proxy(Class) is False

    # Assert that this tester rejects an arbitrary non-class.
    assert is_beartype_ref_proxy('A mighty voice invokes thee. Ruin calls') is False
