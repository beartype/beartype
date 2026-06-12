#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **object getter utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.utilobjget` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ getter : name              }....................
def test_get_object_basename_scoped() -> None:
    '''
    Test the :func:`beartype._util.utilobjget.get_object_basename_scoped`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilObjectNameException
    from beartype._util.utilobjget import get_object_basename_scoped
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
    Test the :func:`beartype._util.utilobjget.get_object_filename_or_none`
    getter.
    '''

    # Defer test-specific imports.
    from beartype._util.utilobjget import get_object_filename_or_none
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
    Test the :func:`beartype._util.utilobjget.get_object_name` getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilObjectNameException
    from beartype._util.utilobjget import get_object_name
    from beartype_test.a00_unit.data.data_type import function_partial
    from pytest import raises

    # ....................{ CALLABLES                      }....................
    def meet_in_the_vale(and_one_majestic_river: str) -> str:
        '''
        Arbitrary nested function.
        '''

        return and_one_majestic_river
    # print(f'meet_in_the_vale.__module__: {meet_in_the_vale.__module__}')

    # ....................{ PASS                           }....................
    # Assert this getter returns the expected name for a nested function.
    meet_in_the_vale_name = get_object_name(meet_in_the_vale)
    assert meet_in_the_vale_name == (
        'beartype_test.a00_unit.a20_util.a00_core.test_utilobjget.'
        'test_get_object_name.meet_in_the_vale'
    )

    # ....................{ FAIL                           }....................
    # Assert this getter raises "AttributeError" exceptions when passed objects
    # declaring neither "__qualname__" nor "__name__" dunder attributes.
    with raises(_BeartypeUtilObjectNameException):
        get_object_name(function_partial)
