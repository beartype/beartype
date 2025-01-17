#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **object utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.utilobject` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_is_object_hashable() -> None:
    '''
    Test the :func:`beartype._util.utilobject.is_object_hashable` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.utilobject import is_object_hashable
    from beartype_test.a00_unit.data.hint.data_hint import (
        NOT_HINTS_HASHABLE, NOT_HINTS_UNHASHABLE,)

    # Assert this tester accepts unhashable objects.
    for object_hashable in NOT_HINTS_HASHABLE:
        assert is_object_hashable(object_hashable) is True

    # Assert this tester rejects unhashable objects.
    for object_unhashable in NOT_HINTS_UNHASHABLE:
        assert is_object_hashable(object_unhashable) is False

# ....................{ TESTS ~ getter : name              }....................
def test_get_object_basename_scoped() -> None:
    '''
    Test the :func:`beartype._util.utilobject.get_object_basename_scoped`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilObjectNameException
    from beartype._util.utilobject import get_object_basename_scoped
    from beartype_test.a00_unit.data.data_type import (
        CALLABLES,
        closure_factory,
    )
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this getter returns the fully-qualified names of non-nested
    # callables unmodified.
    for callable_obj in CALLABLES:
        assert get_object_basename_scoped(callable_obj) == (
            callable_obj.__qualname__)

    # Assert this getter returns the fully-qualified names of closures stripped
    # of meaningless "<locals>." substrings.
    assert get_object_basename_scoped(closure_factory()) == (
        'closure_factory.closure')

    # ....................{ FAIL                           }....................
    # Assert this getter raises "AttributeError" exceptions when passed objects
    # declaring neither "__qualname__" nor "__name__" dunder attributes.
    with raises(_BeartypeUtilObjectNameException):
        get_object_basename_scoped(
            'From the ice-gulfs that gird his secret throne,')


def test_get_object_filename_or_none() -> None:
    '''
    Test the :func:`beartype._util.utilobject.get_object_filename_or_none`
    getter.
    '''

    # Defer test-specific imports.
    from beartype._util.utilobject import get_object_filename_or_none
    from beartype_test.a00_unit.data.data_type import (
        Class,
        function,
    )

    # Assert this getter returns the expected filename for a physical class.
    assert 'data_type' in get_object_filename_or_none(Class)

    # Assert this getter returns the expected filename for a physical callable.
    assert 'data_type' in get_object_filename_or_none(function)

    # Assert this getter returns "None" when passed an object that is neither a
    # class *NOR* callable.
    assert get_object_filename_or_none(Class()) is None


def test_get_object_name() -> None:
    '''
    Test the :func:`beartype._util.utilobject.get_object_name` getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilObjectNameException
    from beartype._util.utilobject import get_object_name
    from beartype_test.a00_unit.data.data_type import function_partial
    from pytest import raises

    # ....................{ CALLABLES                      }....................
    def meet_in_the_vale(and_one_majestic_river: str) -> str:
        '''
        Arbitrary nested function.
        '''

        return and_one_majestic_river

    # ....................{ PASS                           }....................
    # Assert this getter returns the expected name for a nested function.
    assert get_object_name(meet_in_the_vale) == (
        'beartype_test.a00_unit.a20_util.test_utilobject.'
        'test_get_object_name.meet_in_the_vale'
    )

    # ....................{ FAIL                           }....................
    # Assert this getter raises "AttributeError" exceptions when passed objects
    # declaring neither "__qualname__" nor "__name__" dunder attributes.
    with raises(_BeartypeUtilObjectNameException):
        get_object_name(function_partial)
