#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **class getter** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.cls.utilclsget` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ getter                     }....................
def test_get_type_filename_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.cls.utilclsget.get_type_filename_or_none` getter.
    '''

    # Defer test-specific imports.
    from beartype._util.cls.utilclsget import get_type_filename_or_none
    from beartype_test.a00_unit.data.data_type import (
        Class,
        ClassWithModuleNameNone,
        ClassWithModuleNameNonexistent,
    )

    # Filename of a class declared on-disk.
    type_filename = get_type_filename_or_none(Class) 

    # Assert this filename is that of the expected submodule.
    assert isinstance(type_filename, str)
    assert 'data_type' in type_filename

    # Assert this getter returns "None" for classes with either missing or
    # non-existent module names.
    assert get_type_filename_or_none(ClassWithModuleNameNone) is None
    assert get_type_filename_or_none(ClassWithModuleNameNonexistent) is None
