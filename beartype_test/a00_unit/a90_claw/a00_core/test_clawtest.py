#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **import hook tester** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype.claw._clawtest` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ testers                    }....................
def test_is_beartype_initted_partial() -> None:
    '''
    Test the
    :func:`beartype.claw._clawtest.is_beartype_claw_initted_partial` tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.claw._clawtest import is_beartype_claw_initted_partial

    # ....................{ ASSERTS                        }....................
    # Assert that this tester reports the "beartype" package to be fully
    # initialized from within any arbitrary unit test.
    assert is_beartype_claw_initted_partial() is False
