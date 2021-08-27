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
def test_is_type_builtin() -> None:
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


def test_is_type_subclass() -> None:
    '''
    Test the :func:`beartype._util.cls.utilclstest.is_type_subclass` tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.cls.utilclstest import is_type_subclass
    from beartype_test.a00_unit.data.data_type import Class, Subclass

    # Assert this tester accepts objects that are subclasses of superclasses.
    assert is_type_subclass(Subclass, Class) is True
    assert is_type_subclass(Class, object) is True
    assert is_type_subclass(Class, (Class, str)) is True

    # Assert this tester rejects objects that are superclasses of subclasses.
    assert is_type_subclass(object, Class) is False
    assert is_type_subclass(Class, Subclass) is False
    assert is_type_subclass(Class, (Subclass, str)) is False

    # Assert this tester rejects objects that are unrelated classes.
    assert is_type_subclass(str, bool) is False

    # Assert this tester rejects objects that are non-classes *WITHOUT* raising
    # an exception.
    assert is_type_subclass(
        "Thou many-colour'd, many-voiced vale,", str) is False
