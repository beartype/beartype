#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Callable parameter getter utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.func.arg.utilfuncargget` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ name                       }....................
def test_get_func_arg_name_first_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.func.arg.utilfuncargget.get_func_arg_name_first_or_none`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.arg.utilfuncargget import (
        get_func_arg_name_first_or_none)
    from beartype_test.a00_unit.data.func.data_func import (
        func_args_0_wrapped,
        func_args_1_varpos_wrapped,
        func_args_3_flex_mandatory_optional_varkw_wrapped,
    )
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this getter returns "None" for argumentless callables.
    assert get_func_arg_name_first_or_none(func_args_0_wrapped) is None

    # Assert this getter returns the expected names of the first parameters
    # accepted by argumentative callables.
    assert get_func_arg_name_first_or_none(func_args_1_varpos_wrapped) == (
        'and_in_her_his_one_delight')
    assert get_func_arg_name_first_or_none(
        func_args_3_flex_mandatory_optional_varkw_wrapped) == (
        'and_the_wolf_tracks_her_there')

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed a C-based
    # callable.
    with raises(_BeartypeUtilCallableException):
        get_func_arg_name_first_or_none(iter)


def test_get_func_arg_names() -> None:
    '''
    Test the
    :func:`beartype._util.func.arg.utilfuncargget.get_func_arg_names`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.arg.utilfuncargget import get_func_arg_names
    from beartype_test.a00_unit.data.func.data_func import (
        func_args_0_wrapped,
        func_args_1_varpos_wrapped,
        func_args_3_flex_mandatory_optional_varkw_wrapped,
        func_args_5_flex_mandatory_varpos_kwonly_varkw_wrapped,
    )
    from beartype_test.a00_unit.data.func.data_pep570 import (
        func_args_10_all_except_flex_mandatory)
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this getter when passed an argumentless callable returns the empty
    # list.
    assert get_func_arg_names(func_args_0_wrapped) == ()

    # Assert this getter when passed argumentative callables returns the
    # expected lists of the names of the parameters accepted by these callables.
    assert get_func_arg_names(func_args_1_varpos_wrapped) == (
        'and_in_her_his_one_delight',)
    assert get_func_arg_names(
        func_args_3_flex_mandatory_optional_varkw_wrapped) == (
        'and_the_wolf_tracks_her_there',
        'how_hideously',
        'rude_bare_and_high',
    )
    assert get_func_arg_names(
        func_args_5_flex_mandatory_varpos_kwonly_varkw_wrapped) == (
        'we_are_selfish_men',
        'oh_raise_us_up',
        'return_to_us_again',
        'and_give_us',
        'manners_virtue_freedom_power',
    )

    assert get_func_arg_names(
        func_args_10_all_except_flex_mandatory) == (
        'in_solitude_i_wander',
        'through_the_vast_enchanted_forest',
        'the_surrounding_skies',
        'torn_apart_by',
        'rain_is_pouring_down',
        'the_darkened_oaks_are_my_only_shelter',
        'red_leaves_are_blown_by',
        'an_ebony_raven_now_catches',
        'in_the_rain_my_tears_are_forever_lost',
        'sitting_in_calmness',
    )

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed a C-based
    # callable.
    with raises(_BeartypeUtilCallableException):
        get_func_arg_names(iter)
