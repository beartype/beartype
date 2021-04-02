#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **class utility** unit tests.

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
    Test the :func:`beartype._util.cls.utilclstest.is_type_builtin` function.
    '''

    # Defer heavyweight imports.
    from beartype._util.cls.utilclstest import is_type_builtin
    from beartype_test.a00_unit.data.data_type import (
        CLASSES_BUILTIN, CLASSES_NON_BUILTIN)

    # Assert this tester accepts all builtin types.
    for class_builtin in CLASSES_BUILTIN:
        assert is_type_builtin(class_builtin) is True

    # Assert this tester rejects non-builtin types.
    for class_non_builtin in CLASSES_NON_BUILTIN:
        assert is_type_builtin(class_non_builtin) is False


def test_is_classname_builtin() -> None:
    '''
    Test the :func:`beartype._util.cls.utilclstest.is_classname_builtin` function.
    '''

    # Defer heavyweight imports.
    from beartype._util.cls.utilclstest import is_classname_builtin
    from beartype._util.utilobject import get_object_type_name
    from beartype_test.a00_unit.data.data_type import (
        CLASSES_BUILTIN, CLASSES_NON_BUILTIN)

    # Assert this tester accepts the fully-qualified names of all builtin
    # types.
    for class_builtin in CLASSES_BUILTIN:
        assert is_classname_builtin(
            get_object_type_name(class_builtin)) is True

    # Assert this tester rejects non-builtin types.
    for class_non_builtin in CLASSES_NON_BUILTIN:
        assert is_classname_builtin(
            get_object_type_name(class_non_builtin)) is False
