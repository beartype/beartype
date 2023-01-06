#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python module tester** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.mod.utilmodtest` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ getter                     }....................
def test_die_unless_module_attr_name() -> None:
    '''
    Test the :func:`beartype._util.mod.utilmodtest.die_unless_module_attr_name`
    validator.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilModuleException
    from beartype._util.mod.utilmodget import (
        get_object_module_line_number_begin)
    from beartype_test.a00_unit.data.util.mod.data_utilmodule_line import (
        SlowRollingOn,
        like_snakes_that_watch_their_prey,
    )
    from pytest import raises

    # Assert this getter returns the expected line number for this callable.
    assert get_object_module_line_number_begin(
        like_snakes_that_watch_their_prey) == 20

    #FIXME: The inspect.findsource() function underlying this call incorrectly
    #suggests this class to be declared at this line of its submodule, when in
    #fact this class is declared at the following line of its submodule. Sadly,
    #there's nothing meaningful we can do about this. Just be aware, please.
    # Assert this getter returns the expected line number for this class.
    assert get_object_module_line_number_begin(SlowRollingOn) == 39

    # Assert this validator raises the expected exception when passed an object
    # that is neither a callable nor class.
    with raises(_BeartypeUtilModuleException):
        get_object_module_line_number_begin(
            'Frost and the Sun in scorn of mortal power')
