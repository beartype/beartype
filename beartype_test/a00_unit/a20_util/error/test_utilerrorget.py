#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype exception getter utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.error.utilerrorget` submodule.
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
    :func:`beartype._util.error.utilerrorget.get_name_error_attr_name` getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.error.utilerrorget import get_name_error_attr_name

    # ....................{ ASSERT                         }....................
    # Attempt to access an undefined attribute.
    try:
        undefined_attr
    # When doing so necessarily raises the standard "NameError" exception...
    except NameError as name_error:
        # Assert that the unqualified basename of this undefined attribute
        # returned by this getter is the expected basename.
        assert get_name_error_attr_name(name_error) == 'undefined_attr'
