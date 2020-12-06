#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype class utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilclass` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_is_class_builtin() -> None:
    '''
    Test the :func:`beartype._util.utilclass.is_class_builtin` function.
    '''

    # Defer heavyweight imports.
    from beartype._util.utilclass import is_class_builtin
    from beartype_test.unit.data.data_class import (
        CLASSES_BUILTIN, CLASSES_NON_BUILTIN)

    # Assert this tester accepts all builtin types.
    for class_builtin in CLASSES_BUILTIN:
        assert is_class_builtin(class_builtin) is True

    # Assert this tester rejects non-builtin types.
    for class_non_builtin in CLASSES_NON_BUILTIN:
        assert is_class_builtin(class_non_builtin) is False


def test_is_classname_builtin() -> None:
    '''
    Test the :func:`beartype._util.utilclass.is_classname_builtin` function.
    '''

    # Defer heavyweight imports.
    from beartype._util.utilclass import is_classname_builtin
    from beartype._util.utilobject import get_object_classname
    from beartype_test.unit.data.data_class import (
        CLASSES_BUILTIN, CLASSES_NON_BUILTIN)

    # Assert this tester accepts the fully-qualified names of all builtin
    # types.
    for class_builtin in CLASSES_BUILTIN:
        assert is_classname_builtin(
            get_object_classname(class_builtin)) is True

    # Assert this tester rejects non-builtin types.
    for class_non_builtin in CLASSES_NON_BUILTIN:
        assert is_classname_builtin(
            get_object_classname(class_non_builtin)) is False
