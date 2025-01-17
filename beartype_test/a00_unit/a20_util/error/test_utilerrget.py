#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype exception getter utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.error.utilerrget` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To get human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_get_name_error_attr_name() -> None:
    '''
    Test the
    :func:`beartype._util.error.utilerrget.get_name_error_attr_name` getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.error.utilerrget import get_name_error_attr_name

    # ....................{ ASSERT                         }....................
    # Attempt to access an attribute *NEVER* defined in either the global or
    # local scopes of this unit test.
    try:
        undefined_attr
    # When doing so necessarily raises the standard "NameError" exception...
    except NameError as exception:
        # Assert that the unqualified basename of this undefined attribute
        # returned by this getter is the expected basename.
        assert get_name_error_attr_name(exception) == 'undefined_attr'

    # Attempt to access a currently undefined free attribute (i.e., local
    # attribute subsequently defined in the local scope of this unit test).
    try:
        FreeAttr
    # When doing so necessarily raises the standard "NameError" exception...
    except NameError as exception:
        # Assert that the unqualified basename of this currently undefined free
        # attribute returned by this getter is the expected basename.
        assert get_name_error_attr_name(exception) == 'FreeAttr'

    # ....................{ ATTRIBUTES                     }....................
    class FreeAttr(object):
        '''
        Arbitrary class whose name is that of a previously undefined free
        attribute referenced above.
        '''

        pass
