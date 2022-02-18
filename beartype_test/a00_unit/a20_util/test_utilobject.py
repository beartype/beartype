#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype object utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilobject` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                    }....................
def test_is_object_hashable() -> None:
    '''
    Test the :func:`beartype._util.utilobject.is_object_hashable` tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.utilobject import is_object_hashable
    from beartype_test.a00_unit.data.hint.data_hint import (
        NOT_HINTS_HASHABLE, NOT_HINTS_UNHASHABLE,)

    # Assert this tester accepts unhashable objects.
    for object_hashable in NOT_HINTS_HASHABLE:
        assert is_object_hashable(object_hashable) is True

    # Assert this tester rejects unhashable objects.
    for object_unhashable in NOT_HINTS_UNHASHABLE:
        assert is_object_hashable(object_unhashable) is False

# ....................{ TESTS ~ getter                    }....................
def test_get_object_basename_scoped() -> None:
    '''
    Test the :func:`beartype._util.utilobject.get_object_basename_scoped` getter.
    '''

    # Defer heavyweight imports.
    from beartype.roar._roarexc import _BeartypeUtilObjectNameException
    from beartype._util.utilobject import get_object_basename_scoped
    from beartype_test.a00_unit.data.data_type import (
        CALLABLES,
        closure_factory,
    )
    from pytest import raises

    # Assert this getter returns the fully-qualified names of non-nested
    # callables unmodified.
    for callable_obj in CALLABLES:
        assert get_object_basename_scoped(callable_obj) == (
            callable_obj.__qualname__)

    # Assert this getter returns the fully-qualified names of closures stripped
    # of meaningless "<locals>." substrings.
    assert get_object_basename_scoped(closure_factory()) == (
        'closure_factory.closure')

    # Assert this getter raises "AttributeError" exceptions when passed objects
    # declaring neither "__qualname__" nor "__name__" dunder attributes.
    with raises(_BeartypeUtilObjectNameException):
        get_object_basename_scoped(
            'From the ice-gulfs that gird his secret throne,')
