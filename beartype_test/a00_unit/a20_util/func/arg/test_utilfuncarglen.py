#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Callable parameter length getter utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.func.arg.utilfuncarglen` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_get_func_args_len_flexible() -> None:
    '''
    Test the
    :func:`beartype._util.func.arg.utilfuncarglen.get_func_args_flexible_len`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.arg.utilfuncarglen import (
        get_func_args_flexible_len)
    from beartype_test.a00_unit.data.data_type import (
        ClassCallable,
        function_partial,
        function_partial_bad,
    )
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

    # ....................{ LOCALS                         }....................
    # Callable object whose class defines the __call__() dunder method.
    callable_object = ClassCallable()

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

    # Assert this getter returns the expected length of a partial callable.
    assert get_func_args_flexible_len(function_partial) == 0

    # Assert this getter returns the expected length of a callable object.
    assert get_func_args_flexible_len(callable_object) == 0

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
    # Assert this getter raises the expected exception when passed an uncallable
    # object.
    with raises(_BeartypeUtilCallableException):
        get_func_args_flexible_len('Following his eager soul, the wanderer')

    # Assert this getter raises the expected exception when passed a C-based
    # callable.
    with raises(_BeartypeUtilCallableException):
        get_func_args_flexible_len(iter)

    # Assert this getter raises the expected exception when passed an invalid
    # partial callable passing more parameters than the underlying function
    # actually accepts.
    with raises(_BeartypeUtilCallableException):
        get_func_args_flexible_len(function_partial_bad)
