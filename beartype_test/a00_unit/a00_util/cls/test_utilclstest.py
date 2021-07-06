#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **class-specific utility function** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.cls.utilclstest` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_is_class_builtin() -> None:
    '''
    Test the :func:`beartype._util.cls.utilclstest.is_type_builtin` tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.cls.utilclstest import is_type_builtin
    from beartype_test.a00_unit.data.data_type import (
        TYPES_BUILTIN, TYPES_NONBUILTIN)

    # Assert this tester accepts all builtin types.
    for type_builtin in TYPES_BUILTIN:
        assert is_type_builtin(type_builtin) is True

    # Assert this tester rejects non-builtin types.
    for type_nonbuiltin in TYPES_NONBUILTIN:
        assert is_type_builtin(type_nonbuiltin) is False
