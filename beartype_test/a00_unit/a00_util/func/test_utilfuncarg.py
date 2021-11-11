#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Callable argument utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.utilfuncarg` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
from pytest import raises

# ....................{ CALLABLES                         }....................
def func_args_0() -> str:
    '''
    Arbitrary callable accepting *no* parameters
    '''

    return 'And so there grew great tracts of wilderness,'


def func_args_1_flex_mandatory(had_one_fair_daughter: str) -> str:
    '''
    Arbitrary callable accepting one mandatory flexible parameter.
    '''

    return 'But man was less and less, till Arthur came.'


def func_args_1_varpos(*and_in_her_his_one_delight: str) -> str:
    '''
    Arbitrary callable accepting one variadic positional parameter.
    '''

    return 'Wherein the beast was ever more and more,'


def func_args_1_kwonly_mandatory(
    *, when_can_I_take_you_from_this_place: str) -> str:
    '''
    Arbitrary callable accepting one mandatory keyword-only parameter.
    '''

    return 'When is the word but a sigh?'


def func_args_2_flex_mandatory(
    thick_with_wet_woods: str, and_many_a_beast_therein: str) -> str:
    '''
    Arbitrary callable accepting two or more mandatory flexible parameters.
    '''

    return 'For here between the man and beast we die.'


def func_args_5_flex_mandatory_varpos_varkw(
    we_are_selfish_men,
    oh_raise_us_up,
    *and_give_us,
    return_to_us_again='Of inward happiness.',
    **manners_virtue_freedom_power,
) -> str:
    '''
    Arbitrary callable accepting two mandatory flexible parameters, one
    variadic positional parameter, one optional keyword-only parameter (defined
    implicitly), and one variadic keyword parameter.
    '''

    # Arbitrary local variable declared in the body of this callable.
    thy_soul_was_like_a_star = 'and dwelt apart:'
    return thy_soul_was_like_a_star

# ....................{ TESTS ~ tester : kind             }....................
def test_is_func_argless() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncarg.is_func_argless` function.
    '''

    # Defer heavyweight imports.
    from beartype._util.func.utilfuncarg import is_func_argless

    # Assert this tester accepts an argument-less callable.
    assert is_func_argless(func_args_0) is True

    # Assert this tester rejects all other callables.
    assert is_func_argless(func_args_1_flex_mandatory) is False
    assert is_func_argless(func_args_1_varpos) is False
    assert is_func_argless(func_args_1_kwonly_mandatory) is False


def test_is_func_arg_variadic() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncarg.is_func_arg_variadic` function.
    '''

    # Defer heavyweight imports.
    from beartype._util.func.utilfuncarg import is_func_arg_variadic

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
    :func:`beartype._util.func.utilfuncarg.is_func_arg_name` function.
    '''

    # Defer heavyweight imports.
    from beartype._util.func.utilfuncarg import is_func_arg_name

    # Assert this tester accepts all argument names accepted by this callable.
    assert is_func_arg_name(
        func_args_5_flex_mandatory_varpos_varkw, 'we_are_selfish_men') is True
    assert is_func_arg_name(
        func_args_5_flex_mandatory_varpos_varkw, 'oh_raise_us_up') is True
    assert is_func_arg_name(
        func_args_5_flex_mandatory_varpos_varkw, 'return_to_us_again') is True
    assert is_func_arg_name(
        func_args_5_flex_mandatory_varpos_varkw, 'and_give_us') is True
    assert is_func_arg_name(
        func_args_5_flex_mandatory_varpos_varkw,
        'manners_virtue_freedom_power',
    ) is True

    # Assert this tester rejects all local variable names declared by this
    # callable's body.
    assert is_func_arg_name(
        func_args_5_flex_mandatory_varpos_varkw,
        'thy_soul_was_like_a_star',
    ) is False

# ....................{ TESTS ~ getter                    }....................
def test_get_func_arg_len_flexible() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncarg.get_func_args_len_flexible` getter.
    '''

    # Defer heavyweight imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.utilfuncarg import get_func_args_len_flexible

    # Assert this tester returns the expected lengths of these callables.
    assert get_func_args_len_flexible(func_args_0) == 0
    assert get_func_args_len_flexible(func_args_1_varpos) == 0
    assert get_func_args_len_flexible(func_args_1_flex_mandatory) == 1
    assert get_func_args_len_flexible(func_args_2_flex_mandatory) == 2

    # Assert this tester raises the expected exception when passed a C-based
    # callable.
    with raises(_BeartypeUtilCallableException):
        get_func_args_len_flexible(iter)

# ....................{ TESTS ~ iterator                  }....................
def test_iter_func_args() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncarg.iter_func_args` generator.
    '''

    # Defer heavyweight imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.utilfuncarg import (
        ParameterKind,
        iter_func_args,
    )

    # Assert this iterator returns the empty generator for an argument-less
    # callable, explicitly coerced into a tuple to trivialize testing.
    assert len(tuple(iter_func_args(func_args_0))) == 0

    # Assert this iterator returns the expected generator for argumentative
    # callables accepting multiple kinds of parameters, explicitly coerced into
    # tuples to trivialize testing.
    assert tuple(iter_func_args(func_args_1_flex_mandatory)) == (
        ('had_one_fair_daughter', ParameterKind.POSITIONAL_OR_KEYWORD, None,),
    )
    assert tuple(iter_func_args(func_args_1_varpos)) == (
        ('and_in_her_his_one_delight', ParameterKind.VAR_POSITIONAL, None,),
    )
    assert tuple(iter_func_args(func_args_1_kwonly_mandatory)) == (
        ('when_can_I_take_you_from_this_place', ParameterKind.KEYWORD_ONLY, None,),
    )
    assert tuple(iter_func_args(func_args_2_flex_mandatory)) == (
        ('thick_with_wet_woods', ParameterKind.POSITIONAL_OR_KEYWORD, None,),
        ('and_many_a_beast_therein', ParameterKind.POSITIONAL_OR_KEYWORD, None,),
    )
    assert tuple(iter_func_args(func_args_5_flex_mandatory_varpos_varkw)) == (
        ('we_are_selfish_men', ParameterKind.POSITIONAL_OR_KEYWORD, None,),
        ('oh_raise_us_up', ParameterKind.POSITIONAL_OR_KEYWORD, None,),
        ('and_give_us', ParameterKind.VAR_POSITIONAL, None,),
        ('return_to_us_again', ParameterKind.KEYWORD_ONLY, 'Of inward happiness.',),
        ('manners_virtue_freedom_power', ParameterKind.VAR_KEYWORD, None,),
    )

    # If the active Python interpreter targets Python >= 3.8 and thus supports
    # PEP 570-compliant positional-only parameters...
    if IS_PYTHON_AT_LEAST_3_8:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.data_pep570 import (
            func_args_10_all_except_flex_mandatory)

        # Assert this iterator returns the expected generator for argumentative
        # callables accepting multiple kinds of parameters -- including
        # positional-only parameters.
        assert tuple(iter_func_args(func_args_10_all_except_flex_mandatory)) == (
            ('in_solitude_i_wander', ParameterKind.POSITIONAL_ONLY, None,),
            ('through_the_vast_enchanted_forest', ParameterKind.POSITIONAL_ONLY, None,),
            ('the_surrounding_skies', ParameterKind.POSITIONAL_ONLY, 'are one',),
            ('torn_apart_by', ParameterKind.POSITIONAL_OR_KEYWORD, 'the phenomenon of lightning',),
            ('rain_is_pouring_down', ParameterKind.POSITIONAL_OR_KEYWORD, 'my now shivering shoulders',),
            ('in_the_rain_my_tears_are_forever_lost', ParameterKind.VAR_POSITIONAL, None,),
            ('the_darkened_oaks_are_my_only_shelter', ParameterKind.KEYWORD_ONLY, None,),
            ('red_leaves_are_blown_by', ParameterKind.KEYWORD_ONLY, 'the wind',),
            ('an_ebony_raven_now_catches', ParameterKind.KEYWORD_ONLY, 'my eye.',),
            ('sitting_in_calmness', ParameterKind.VAR_KEYWORD, None,),
        )

    # Assert this iterator returns a generator raising the expected exception
    # when passed a C-based callable.
    with raises(_BeartypeUtilCallableException):
        next(iter_func_args(iter))
