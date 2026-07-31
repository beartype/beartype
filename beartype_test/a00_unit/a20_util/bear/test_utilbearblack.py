#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**beartype blacklist utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.bear.utilbearblack` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ testers                    }....................
def test_is_object_blacklisted() -> None:
    '''
    Test the
    :func:`beartype._util.bear.utilbearblack.is_object_blacklisted` tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.bear.utilbearblack import is_object_blacklisted

    # ....................{ ASSERTS                        }....................
    #FIXME: Additionally pass various other kinds of objects commonly passed to
    #this tester in real-world code (e.g., callables, classes).

    # Assert that this tester rejects an arbitrary unhashable object that cannot
    # be weakly referenced *WITHOUT* raising an unexpected exception.
    assert is_object_blacklisted([
        'Lifted his curved lids', 'and kept them wide']) is False
