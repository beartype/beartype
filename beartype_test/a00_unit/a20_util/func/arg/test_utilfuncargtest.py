#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Callable argument tester utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.func.arg.utilfuncargtest` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ kind                       }....................
def test_is_func_argless() -> None:
    '''
    Test the
    :func:`beartype._util.func.arg.utilfuncargtest.is_func_argless` tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.func.arg.utilfuncargtest import is_func_argless
    from beartype_test.a00_unit.data.func.data_func import (
        func_args_0,
        func_args_1_flex_mandatory,
        func_args_1_varpos,
        func_args_1_kwonly_mandatory,
    )

    # ....................{ ASSERTS                        }....................
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

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.func.arg.utilfuncargtest import is_func_arg_variadic

    # ....................{ CALLABLES                      }....................
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

    # ....................{ ASSERTS                        }....................
    # Assert this tester accepts callables accepting variadic arguments.
    assert is_func_arg_variadic(of_childhood) is True
    assert is_func_arg_variadic(the_passions) is True

    # Assert this tester rejects callables accepting *NO* variadic arguments.
    assert is_func_arg_variadic(by_day_or_starlight) is False

# ....................{ TESTS ~ name                       }....................
def test_is_func_arg_name() -> None:
    '''
    Test the
    :func:`beartype._util.func.arg.utilfuncargtest.is_func_arg_name` tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.func.arg.utilfuncargtest import is_func_arg_name
    from beartype_test.a00_unit.data.func.data_func import (
        func_args_5_flex_mandatory_varpos_kwonly_varkw)

    # ....................{ ASSERTS                        }....................
    # Assert this tester accepts all argument names accepted by the passed
    # callable.
    assert is_func_arg_name(
        func=func_args_5_flex_mandatory_varpos_kwonly_varkw,
        arg_name='we_are_selfish_men',
    ) is True
    assert is_func_arg_name(
        func=func_args_5_flex_mandatory_varpos_kwonly_varkw,
        arg_name='oh_raise_us_up',
    ) is True
    assert is_func_arg_name(
        func=func_args_5_flex_mandatory_varpos_kwonly_varkw,
        arg_name='return_to_us_again',
    ) is True
    assert is_func_arg_name(
        func=func_args_5_flex_mandatory_varpos_kwonly_varkw,
        arg_name='and_give_us',
    ) is True
    assert is_func_arg_name(
        func=func_args_5_flex_mandatory_varpos_kwonly_varkw,
        arg_name='manners_virtue_freedom_power',
    ) is True

    # Assert this tester rejects all local variable names declared in the body
    # of the passed callable.
    assert is_func_arg_name(
        func=func_args_5_flex_mandatory_varpos_kwonly_varkw,
        arg_name='thy_soul_was_like_a_star',
    ) is False


def test_is_func_arg_name_is_func_arg_name_variadic_positional() -> None:
    '''
    Test the
    :func:`beartype._util.func.arg.utilfuncargtest.is_func_arg_name_variadic_positional`
    tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.func.arg.utilfuncargtest import (
        is_func_arg_name_variadic_positional)
    from beartype_test.a00_unit.data.func.data_func import (
        func_args_3_flex_mandatory_optional_varkw_wrapped)
    from beartype_test.a00_unit.data.func.data_pep570 import (
        func_args_10_all_except_flex_mandatory)

    # ....................{ ASSERTS                        }....................
    # Assert that this tester rejects a callable accepting a parameter with the
    # passed name that is *NOT* a variadic positional parameter.
    assert is_func_arg_name_variadic_positional(
        func=func_args_3_flex_mandatory_optional_varkw_wrapped,
        arg_name='rude_bare_and_high',
    ) is False

    # Assert that this tester rejects a callable accepting a variadic positional
    # parameter with a different name than that of the passed name.
    assert is_func_arg_name_variadic_positional(
        func=func_args_10_all_except_flex_mandatory,
        arg_name='rain_is_pouring_down',
    ) is False

    # Assert that this tester rejects a callable accepting a variadic positional
    # parameter but accepting *NO* parameter with the passed name.
    assert is_func_arg_name_variadic_positional(
        func=func_args_10_all_except_flex_mandatory,
        arg_name='before_spreading_his_black_wings',
    ) is False

    # Assert that this tester accepts a callable accepting a variadic positional
    # parameter with the passed name.
    assert is_func_arg_name_variadic_positional(
        func=func_args_10_all_except_flex_mandatory,
        arg_name='in_the_rain_my_tears_are_forever_lost',
    ) is True


def test_is_func_arg_name_is_func_arg_name_variadic_keyword() -> None:
    '''
    Test the
    :func:`beartype._util.func.arg.utilfuncargtest.is_func_arg_name_variadic_keyword`
    tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.func.arg.utilfuncargtest import (
        is_func_arg_name_variadic_keyword)
    from beartype_test.a00_unit.data.func.data_func import (
        func_args_1_varpos_wrapped)
    from beartype_test.a00_unit.data.func.data_pep570 import (
        func_args_10_all_except_flex_mandatory)

    # ....................{ ASSERTS                        }....................
    # Assert that this tester rejects a callable accepting a parameter with the
    # passed name that is *NOT* a variadic keyword parameter.
    assert is_func_arg_name_variadic_keyword(
        func=func_args_1_varpos_wrapped,
        arg_name='and_in_her_his_one_delight',
    ) is False

    # Assert that this tester rejects a callable accepting a variadic keyword
    # parameter with a different name than that of the passed name.
    assert is_func_arg_name_variadic_keyword(
        func=func_args_10_all_except_flex_mandatory,
        arg_name='rain_is_pouring_down',
    ) is False

    # Assert that this tester rejects a callable accepting a variadic keyword
    # parameter but accepting *NO* parameter with the passed name.
    assert is_func_arg_name_variadic_keyword(
        func=func_args_10_all_except_flex_mandatory,
        arg_name='before_spreading_his_black_wings',
    ) is False

    # Assert that this tester accepts a callable accepting a variadic keyword
    # parameter with the passed name.
    assert is_func_arg_name_variadic_keyword(
        func=func_args_10_all_except_flex_mandatory,
        arg_name='sitting_in_calmness',
    ) is True
