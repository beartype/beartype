#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **class tester** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.cls.utilclstest` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_is_type_or_types() -> None:
    '''
    Test the :func:`beartype._util.cls.utilclstest.is_type_or_types` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.cls.utilclstest import is_type_or_types

    # Assert this tester accepts an arbitrary type.
    assert is_type_or_types(str) is True

    # Assert this tester accepts an arbitrary non-empty tuple of types.
    assert is_type_or_types((bool, int)) is True

    # Assert this tester rejects an arbitrary object that is neither a type
    # nor a non-empty tuple of types.
    assert is_type_or_types(
        'To drink their odours, and their mighty swinging') is False

    # Assert this tester rejects the empty tuple.
    assert is_type_or_types(()) is False

    # Assert this tester rejects an arbitrary non-empty tuple containing one or
    # more non-types.
    assert is_type_or_types(
        (dict, 'To hear—an old and solemn harmony;', float)) is False


def test_is_type_subclass() -> None:
    '''
    Test the :func:`beartype._util.cls.utilclstest.is_type_subclass` tester.
    '''

    # Defer test-specific imports.
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

# ....................{ TESTS ~ tester : builtin           }....................
def test_is_type_builtin() -> None:
    '''
    Test the :func:`beartype._util.cls.utilclstest.is_type_builtin` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.cls.utilclstest import is_type_builtin
    from beartype_test.a00_unit.data.data_type import (
        TYPES_BUILTIN,
        TYPES_NONBUILTIN,
    )

    # Assert this tester accepts all builtin types.
    for type_builtin in TYPES_BUILTIN:
        assert is_type_builtin(type_builtin) is True

    # Assert this tester rejects non-builtin types.
    for type_nonbuiltin in TYPES_NONBUILTIN:
        assert is_type_builtin(type_nonbuiltin) is False


def test_is_type_builtin_or_fake() -> None:
    '''
    Test the :func:`beartype._util.cls.utilclstest.is_type_builtin_or_fake`
    tester.
    '''

    # Defer test-specific imports.
    from beartype._util.cls.utilclstest import is_type_builtin_or_fake
    from beartype_test.a00_unit.data.data_type import (
        TYPES_BUILTIN,
        TYPES_BUILTIN_FAKE,
        Class,
    )

    # Assert this tester accepts all non-fake builtin types.
    for type_builtin in TYPES_BUILTIN:
        assert is_type_builtin_or_fake(type_builtin) is True

    # Assert this tester accepts all fake builtin types, too.
    for type_builtin_fake in TYPES_BUILTIN_FAKE:
        assert is_type_builtin_or_fake(type_builtin_fake) is True

    # Assert this tester rejects an arbitrary non-builtin type.
    assert is_type_builtin_or_fake(Class) is False
