#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Callable argument getter utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.func.arg.utilfuncargget` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ getter                    }....................
def test_get_func_arg_len_flexible() -> None:
    '''
    Test the
    :func:`beartype._util.func.arg.utilfuncargtest.get_func_args_len_flexible`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.arg.utilfuncargget import (
        get_func_args_len_flexible)
    from beartype_test.a00_unit.data.func.data_func import (
        func_args_0,
        func_args_1_flex_mandatory,
        func_args_1_varpos,
        func_args_2_flex_mandatory,
    )
    from pytest import raises

    # Assert this tester returns the expected lengths of these callables.
    assert get_func_args_len_flexible(func_args_0) == 0
    assert get_func_args_len_flexible(func_args_1_varpos) == 0
    assert get_func_args_len_flexible(func_args_1_flex_mandatory) == 1
    assert get_func_args_len_flexible(func_args_2_flex_mandatory) == 2

    # Assert this tester raises the expected exception when passed a C-based
    # callable.
    with raises(_BeartypeUtilCallableException):
        get_func_args_len_flexible(iter)
