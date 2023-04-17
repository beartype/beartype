#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Callable argument tester utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.func.arg.utilfuncargtest` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester : kind             }....................
def test_is_func_argless() -> None:
    '''
    Test the
    :func:`beartype._util.func.arg.utilfuncargtest.is_func_argless` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.func.arg.utilfuncargtest import is_func_argless
    from beartype_test.a00_unit.data.func.data_func import (
        func_args_0,
        func_args_1_flex_mandatory,
        func_args_1_varpos,
        func_args_1_kwonly_mandatory,
    )

    # Assert this tester accepts an argumentless callable.
    assert is_func_argless(func_args_0) is True

    # Assert this tester rejects all other callables.
    assert is_func_argless(func_args_1_flex_mandatory) is False
    assert is_func_argless(func_args_1_varpos) is False
    assert is_func_argless(func_args_1_kwonly_mandatory) is False


def test_is_func_arg_variadic() -> None:
    '''
    Test the
    :func:`beartype._util.func.arg.utilfuncargtest.is_func_arg_variadic`
    tester.
    '''

    # Defer test-specific imports.
    from beartype._util.func.arg.utilfuncargtest import is_func_arg_variadic

    #FIXME: Generalize these callables into the
    #"beartype_test.a00_unit.data.func.data_func" submodule, please.

    # Arbitrary callable accepting *NO* variadic arguments.
    def by_day_or_starlight(thus_from: int, my_first_dawn: int) -> int:
        return thus_from + my_first_dawn

    # Arbitrary callable accepting a variadic positional argument.
    def of_childhood(
        didst_thou: str, *args: str, intertwine_for_me: str) -> str:
        return didst_thou + ''.join(args) + intertwine_for_me

    # Arbitrary callable accepting a variadic keyword argument.
    def the_passions(
        that_build_up: tuple, our_human_soul: tuple, **kwargs: tuple) -> tuple:
        return that_build_up + our_human_soul + (
            kwarg_tuple_item
            for kwarg_tuple in kwargs
            for kwarg_tuple_item in kwarg_tuple
        )

    # Assert this tester accepts callables accepting variadic arguments.
    assert is_func_arg_variadic(of_childhood) is True
    assert is_func_arg_variadic(the_passions) is True

    # Assert this tester rejects callables accepting *NO* variadic arguments.
    assert is_func_arg_variadic(by_day_or_starlight) is False

# ....................{ TESTS ~ tester : name             }....................
def test_is_func_arg_name() -> None:
    '''
    Test the
    :func:`beartype._util.func.arg.utilfuncargtest.is_func_arg_name` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.func.arg.utilfuncargtest import is_func_arg_name
    from beartype_test.a00_unit.data.func.data_func import (
        func_args_5_flex_mandatory_varpos_kwonly_varkw)

    # Assert this tester accepts all argument names accepted by this callable.
    assert is_func_arg_name(
        func_args_5_flex_mandatory_varpos_kwonly_varkw, 'we_are_selfish_men') is True
    assert is_func_arg_name(
        func_args_5_flex_mandatory_varpos_kwonly_varkw, 'oh_raise_us_up') is True
    assert is_func_arg_name(
        func_args_5_flex_mandatory_varpos_kwonly_varkw, 'return_to_us_again') is True
    assert is_func_arg_name(
        func_args_5_flex_mandatory_varpos_kwonly_varkw, 'and_give_us') is True
    assert is_func_arg_name(
        func_args_5_flex_mandatory_varpos_kwonly_varkw,
        'manners_virtue_freedom_power',
    ) is True

    # Assert this tester rejects all local variable names declared in the body
    # of this callable.
    assert is_func_arg_name(
        func_args_5_flex_mandatory_varpos_kwonly_varkw,
        'thy_soul_was_like_a_star',
    ) is False
