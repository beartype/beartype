#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
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

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.arg.utilfuncargget import (
        get_func_args_len_flexible)
    from beartype_test.a00_unit.data.data_type import decorator_wrapping
    from beartype_test.a00_unit.data.func.data_func import (
        func_args_0,
        func_args_1_flex_mandatory,
        func_args_1_varpos,
        func_args_2_flex_mandatory,
    )
    from pytest import raises

    # These callables when wrapped by a decorator wrapper reducing their
    # signatures to the standard idiom (i.e., "*args, **kwargs").
    func_args_0_wrapped = decorator_wrapping(func_args_0)
    func_args_1_flex_mandatory_wrapped = decorator_wrapping(
        func_args_1_flex_mandatory)
    func_args_1_varpos_wrapped = decorator_wrapping(func_args_1_varpos)
    func_args_2_flex_mandatory_wrapped = decorator_wrapping(
        func_args_2_flex_mandatory)

    # Assert this tester returns the expected lengths of these callables.
    assert get_func_args_len_flexible(func_args_0) == 0
    assert get_func_args_len_flexible(func_args_1_varpos) == 0
    assert get_func_args_len_flexible(func_args_1_flex_mandatory) == 1
    assert get_func_args_len_flexible(func_args_2_flex_mandatory) == 2

    # Assert this tester returns the expected lengths of these callables when
    # wrapped.
    assert get_func_args_len_flexible(func_args_0_wrapped) == 0
    assert get_func_args_len_flexible(func_args_1_varpos_wrapped) == 0
    assert get_func_args_len_flexible(func_args_1_flex_mandatory_wrapped) == 1
    assert get_func_args_len_flexible(func_args_2_flex_mandatory_wrapped) == 2

    # Assert this tester returns 0 when passed a wrapped callable and an option
    # disabling callable unwrapping.
    assert get_func_args_len_flexible(
        func_args_0_wrapped, is_unwrapping=False) == 0
    assert get_func_args_len_flexible(
        func_args_1_varpos_wrapped, is_unwrapping=False) == 0
    assert get_func_args_len_flexible(
        func_args_1_flex_mandatory_wrapped, is_unwrapping=False) == 0
    assert get_func_args_len_flexible(
        func_args_2_flex_mandatory_wrapped, is_unwrapping=False) == 0

    # Assert this tester raises the expected exception when passed a C-based
    # callable.
    with raises(_BeartypeUtilCallableException):
        get_func_args_len_flexible(iter)
