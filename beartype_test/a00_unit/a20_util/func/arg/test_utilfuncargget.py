#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
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

# ....................{ TESTS ~ arg                        }....................
def test_get_func_arg_first_name_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.func.arg.utilfuncargget.get_func_arg_first_name_or_none`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.arg.utilfuncargget import (
        get_func_arg_first_name_or_none)
    from beartype_test.a00_unit.data.func.data_func import (
        func_args_0_wrapped,
        func_args_1_varpos_wrapped,
        func_args_3_flex_mandatory_optional_varkw_wrapped,
    )
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this getter returns "None" for argumentless callables.
    assert get_func_arg_first_name_or_none(func_args_0_wrapped) is None

    # Assert this getter returns the expected names of the first parameters
    # accepted by argumentative callables.
    assert get_func_arg_first_name_or_none(func_args_1_varpos_wrapped) == (
        'and_in_her_his_one_delight')
    assert get_func_arg_first_name_or_none(
        func_args_3_flex_mandatory_optional_varkw_wrapped) == (
        'and_the_wolf_tracks_her_there')

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed a C-based
    # callable.
    with raises(_BeartypeUtilCallableException):
        get_func_arg_first_name_or_none(iter)

# ....................{ TESTS ~ args                       }....................
def test_get_func_args_len_flexible() -> None:
    '''
    Test the
    :func:`beartype._util.func.arg.utilfuncargget.get_func_args_flexible_len`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.arg.utilfuncargget import (
        get_func_args_flexible_len)
    from beartype_test.a00_unit.data.func.data_func import (
        func_args_0,
        func_args_1_flex_mandatory,
        func_args_1_varpos,
        func_args_2_flex_mandatory,
        func_args_0_wrapped,
        func_args_1_flex_mandatory_wrapped,
        func_args_1_varpos_wrapped,
        func_args_2_flex_mandatory_wrapped,
    )
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this getter returns the expected lengths of unwrapped callables.
    assert get_func_args_flexible_len(func_args_0) == 0
    assert get_func_args_flexible_len(func_args_1_varpos) == 0
    assert get_func_args_flexible_len(func_args_1_flex_mandatory) == 1
    assert get_func_args_flexible_len(func_args_2_flex_mandatory) == 2

    # Assert this getter returns the expected lengths of wrapped callables.
    assert get_func_args_flexible_len(func_args_0_wrapped) == 0
    assert get_func_args_flexible_len(func_args_1_varpos_wrapped) == 0
    assert get_func_args_flexible_len(func_args_1_flex_mandatory_wrapped) == 1
    assert get_func_args_flexible_len(func_args_2_flex_mandatory_wrapped) == 2

    # Assert this getter returns 0 when passed a wrapped callable and an option
    # disabling callable unwrapping.
    assert get_func_args_flexible_len(
        func_args_0_wrapped, is_unwrap=False) == 0
    assert get_func_args_flexible_len(
        func_args_1_varpos_wrapped, is_unwrap=False) == 0
    assert get_func_args_flexible_len(
        func_args_1_flex_mandatory_wrapped, is_unwrap=False) == 0
    assert get_func_args_flexible_len(
        func_args_2_flex_mandatory_wrapped, is_unwrap=False) == 0

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed a C-based
    # callable.
    with raises(_BeartypeUtilCallableException):
        get_func_args_flexible_len(iter)
