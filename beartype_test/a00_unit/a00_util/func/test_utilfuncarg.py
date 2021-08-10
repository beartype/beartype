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
from pytest import raises

# ....................{ TESTS ~ tester : kind             }....................
def test_is_func_argless() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncarg.is_func_argless` function.
    '''

    # Defer heavyweight imports.
    from beartype._util.func.utilfuncarg import is_func_argless
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8

    # Arbitrary callable accepting *NO* arguments.
    def when_can_i_take_you_from_this_place(): pass

    # Arbitrary callable accepting one or more variadic arguments.
    def when_is_the_word_but_a_sigh(*args): pass

    # Arbitrary callable accepting one non-variadic non-keyword-only argument.
    def when_is_death_our_lone_beholder(when): pass

    # Assert this tester accepts an argumentless callable.
    assert is_func_argless(when_can_i_take_you_from_this_place) is True

    # Assert this tester rejects all other callables.
    assert is_func_argless(when_is_the_word_but_a_sigh) is False
    assert is_func_argless(when_is_death_our_lone_beholder) is False

    # If the active Python interpreter targets Python >= 3.8 and thus supports
    # keyword-only arguments, declare an...
    if IS_PYTHON_AT_LEAST_3_8:
        # Arbitrary callable accepting one non-variadic keyword-only argument.
        def when_do_we_walk_the_final_steps(*, when): pass

        # Assert this tester rejects this callable.
        assert is_func_argless(when_do_we_walk_the_final_steps) is False


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

    # Arbitrary callable accepting both non-variadic and variadic positional
    # and keyword arguments.
    def of_inward_happiness(
        we_are_selfish_men,
        oh_raise_us_up,
        return_to_us_again,
        *and_give_us,
        **manners_virtue_freedom_power,
    ) -> str:
        # Arbitrary local variable declared in the body of this callable.
        thy_soul_was_like_a_star = 'and dwelt apart:'
        return thy_soul_was_like_a_star

    # Assert this tester accepts all argument names accepted by this callable.
    assert is_func_arg_name(of_inward_happiness, 'we_are_selfish_men') is True
    assert is_func_arg_name(of_inward_happiness, 'oh_raise_us_up') is True
    assert is_func_arg_name(of_inward_happiness, 'return_to_us_again') is True
    assert is_func_arg_name(of_inward_happiness, 'and_give_us') is True
    assert is_func_arg_name(
        of_inward_happiness, 'manners_virtue_freedom_power') is True

    # Assert this tester rejects all local variable names declared by this
    # callable's body.
    assert is_func_arg_name(
        of_inward_happiness, 'thy_soul_was_like_a_star') is False

# ....................{ TESTS ~ getter                    }....................
def test_get_func_arg_len_standard() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncarg.get_func_args_len_flexible` function.
    '''

    # Defer heavyweight imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.utilfuncarg import get_func_args_len_flexible

    # Arbitrary callable accepting no arguments.
    def the_coming_of_arthur() -> str:
        return 'And so there grew great tracts of wilderness,'

    # Arbitrary callable accepting one variadic argument.
    def guinevere(*and_in_her_his_one_delight: str) -> str:
        return 'Wherein the beast was ever more and more,'

    # Arbitrary callable accepting one standard argument.
    def leodogran_the_king_of_cameliard(had_one_fair_daughter: str) -> str:
        return 'But man was less and less, till Arthur came.'

    # Arbitrary callable accepting two or more standard arguments.
    def the_land_of_cameliard_was_waste(
        thick_with_wet_woods: str, and_many_a_beast_therein: str) -> str:
        return 'For here between the man and beast we die.'

    # Assert this tester returns the expected lengths of these callables.
    assert get_func_args_len_flexible(the_coming_of_arthur) == 0
    assert get_func_args_len_flexible(guinevere) == 0
    assert get_func_args_len_flexible(leodogran_the_king_of_cameliard) == 1
    assert get_func_args_len_flexible(the_land_of_cameliard_was_waste) == 2

    # Assert this tester raises the expected exception when passed a C-based
    # callable.
    with raises(_BeartypeUtilCallableException):
        get_func_args_len_flexible(iter)
