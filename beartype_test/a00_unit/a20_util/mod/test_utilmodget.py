#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python module tester** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.module.utilmodtest` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ object                     }....................
def test_get_object_module_or_none() -> None:
    '''
    Test the :func:`beartype._util.module.utilmodget.get_object_module_or_none`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.module.utilmodget import get_object_module_or_none
    from beartype_test.a00_unit.data import data_type

    # ....................{ PASS                           }....................
    # Assert this getter returns the expected module for:
    # * A user-defined class.
    # * A user-defined function.
    assert get_object_module_or_none(data_type.Class) is data_type
    assert get_object_module_or_none(data_type.function) is data_type

    # ....................{ FAIL                           }....................
    # Assert this getter returns "None" for an arbitrary object that is neither
    # a class *NOR* a callable.
    assert get_object_module_or_none(
        'And saw in sleep old palaces and towers') is None


def test_get_object_module() -> None:
    '''
    Test the :func:`beartype._util.module.utilmodget.get_object_module` getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilModuleException
    from beartype._util.module.utilmodget import get_object_module
    from beartype_test.a00_unit.data import data_type
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this getter returns the expected module for:
    # * A user-defined class.
    # * A user-defined function.
    assert get_object_module(data_type.Class) is data_type
    assert get_object_module(data_type.function) is data_type

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception for an arbitrary object
    # that is neither a class *NOR* a callable.
    with raises(_BeartypeUtilModuleException):
        get_object_module("Quivering within the wave's intenser day,")

# ....................{ TESTS ~ object : line              }....................
def test_get_object_module_line_number_begin() -> None:
    '''
    Test the
    :func:`beartype._util.module.utilmodget.get_object_module_line_number_begin`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilModuleException
    from beartype._util.module.utilmodget import (
        get_object_module_line_number_begin)
    from beartype_test.a00_unit.data.util.mod.data_utilmodule_line import (
        SlowRollingOn,
        like_snakes_that_watch_their_prey,
    )
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this getter returns the expected line number for this callable.
    assert get_object_module_line_number_begin(
        like_snakes_that_watch_their_prey) == 20

    #FIXME: The inspect.findsource() function underlying this call incorrectly
    #suggests this class to be declared at this line of its submodule, when in
    #fact this class is declared at the following line of its submodule. Sadly,
    #there's nothing meaningful we can do about this. Just be aware, please.
    # Assert this getter returns the expected line number for this class.
    assert get_object_module_line_number_begin(SlowRollingOn) == 39

    # ....................{ FAIL                           }....................
    # Assert this validator raises the expected exception when passed an object
    # that is neither a callable nor class.
    with raises(_BeartypeUtilModuleException):
        get_object_module_line_number_begin(
            'Frost and the Sun in scorn of mortal power')
