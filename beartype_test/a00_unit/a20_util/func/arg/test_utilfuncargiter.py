#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Callable argument iterator utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.arg.utilfuncargiter` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ iterator                  }....................
def test_iter_func_args() -> None:
    '''
    Test the
    :func:`beartype._util.func.arg.utilfuncargtest.iter_func_args` generator.
    '''

    # Defer heavyweight imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.arg.utilfuncargiter import (
        ParameterKind,
        ParameterMandatory,
        iter_func_args,
    )
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
    from beartype_test.a00_unit.data.func.data_func import (
        func_args_0,
        func_args_1_flex_mandatory,
        func_args_1_varpos,
        func_args_1_kwonly_mandatory,
        func_args_2_flex_mandatory,
        func_args_3_flex_mandatory_optional_varkw,
        func_args_5_flex_mandatory_varpos_varkw,
    )
    from pytest import raises

    # Assert this iterator returns the empty generator for an argument-less
    # callable, explicitly coerced into a tuple to trivialize testing.
    assert len(tuple(iter_func_args(func_args_0))) == 0

    # Assert this iterator returns the expected generator for argumentative
    # callables accepting multiple kinds of parameters, explicitly coerced into
    # tuples to trivialize testing.
    assert _iter_func_args_tuple(func_args_1_flex_mandatory) == (
        ('had_one_fair_daughter', ParameterKind.POSITIONAL_OR_KEYWORD, ParameterMandatory,),
    )
    assert _iter_func_args_tuple(func_args_1_varpos) == (
        ('and_in_her_his_one_delight', ParameterKind.VAR_POSITIONAL, ParameterMandatory,),
    )
    assert _iter_func_args_tuple(func_args_1_kwonly_mandatory) == (
        ('when_can_I_take_you_from_this_place', ParameterKind.KEYWORD_ONLY, ParameterMandatory,),
    )
    assert _iter_func_args_tuple(func_args_2_flex_mandatory) == (
        ('thick_with_wet_woods', ParameterKind.POSITIONAL_OR_KEYWORD, ParameterMandatory,),
        ('and_many_a_beast_therein', ParameterKind.POSITIONAL_OR_KEYWORD, ParameterMandatory,),
    )
    assert _iter_func_args_tuple(func_args_3_flex_mandatory_optional_varkw) == (
        ('and_the_wolf_tracks_her_there', ParameterKind.POSITIONAL_OR_KEYWORD, ParameterMandatory,),
        ('how_hideously', ParameterKind.POSITIONAL_OR_KEYWORD, "Its shapes are heap'd around!",),
        ('rude_bare_and_high', ParameterKind.VAR_KEYWORD, ParameterMandatory,),
    )
    assert _iter_func_args_tuple(func_args_5_flex_mandatory_varpos_varkw) == (
        ('we_are_selfish_men', ParameterKind.POSITIONAL_OR_KEYWORD, ParameterMandatory,),
        ('oh_raise_us_up', ParameterKind.POSITIONAL_OR_KEYWORD, ParameterMandatory,),
        ('and_give_us', ParameterKind.VAR_POSITIONAL, ParameterMandatory,),
        ('return_to_us_again', ParameterKind.KEYWORD_ONLY, 'Of inward happiness.',),
        ('manners_virtue_freedom_power', ParameterKind.VAR_KEYWORD, ParameterMandatory,),
    )

    # If the active Python interpreter targets Python >= 3.8 and thus supports
    # PEP 570-compliant positional-only parameters...
    if IS_PYTHON_AT_LEAST_3_8:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.func.data_pep570 import (
            func_args_10_all_except_flex_mandatory)

        # Assert this iterator returns the expected generator for argumentative
        # callables accepting multiple kinds of parameters -- including
        # positional-only parameters.
        assert _iter_func_args_tuple(func_args_10_all_except_flex_mandatory) == (
            ('in_solitude_i_wander', ParameterKind.POSITIONAL_ONLY, ParameterMandatory,),
            ('through_the_vast_enchanted_forest', ParameterKind.POSITIONAL_ONLY, ParameterMandatory,),
            ('the_surrounding_skies', ParameterKind.POSITIONAL_ONLY, 'are one',),
            ('torn_apart_by', ParameterKind.POSITIONAL_OR_KEYWORD, 'the phenomenon of lightning',),
            ('rain_is_pouring_down', ParameterKind.POSITIONAL_OR_KEYWORD, 'my now shivering shoulders',),
            ('in_the_rain_my_tears_are_forever_lost', ParameterKind.VAR_POSITIONAL, ParameterMandatory,),
            ('the_darkened_oaks_are_my_only_shelter', ParameterKind.KEYWORD_ONLY, ParameterMandatory,),
            ('red_leaves_are_blown_by', ParameterKind.KEYWORD_ONLY, 'the wind',),
            ('an_ebony_raven_now_catches', ParameterKind.KEYWORD_ONLY, 'my eye.',),
            ('sitting_in_calmness', ParameterKind.VAR_KEYWORD, ParameterMandatory,),
        )

    # Assert this iterator returns a generator raising the expected exception
    # when passed a C-based callable.
    with raises(_BeartypeUtilCallableException):
        next(iter_func_args(iter))

# ....................{ PRIVATE ~ coercer                 }....................
def _iter_func_args_tuple(func) -> tuple:
    '''
    Trivial-to-test **parameter metadata tuple** (i.e., tuple of one 3-tuple
    ``({arg_name}, {arg_kind}, {arg_default_value_or_mandatory})`` describing
    each parameter accepted by the passed callable) internally coerced from the
    non-trivial-to-test **parameter metadata generator** (i.e., generator
    implicitly created and returned by the
    :func:`beartype._util.func.arg.utilfuncargiter.iter_func_args` generator
    callable) for the passed pure-Python callable.

    Parameters
    ----------
    func : Callable
        Pure-Python callable to be inspected.

    Returns
    ----------
    Tuple[Tuple[str, EnumMemberType, Any], ...]
        Variable-length tuple nesting one 3-tuple ``(arg_name, arg_kind,
        arg_default)`` for each parameter accepted by this callable.
    '''

    # Defer heavyweight imports.
    from beartype._util.func.arg.utilfuncargiter import iter_func_args
    from collections.abc import Generator

    # Parameter metadata generator created by this iterator for that callable.
    param_meta_generator = iter_func_args(func)

    # Assert this generator actually is a generator.
    assert isinstance(param_meta_generator, Generator)

    # Return a tuple comprehension of...
    return tuple(
        # 3-tuples describing each parameter accepted by an arbitrary callable
        # passed to this generator...
        (
            param_meta.name,
            param_meta.kind,
            param_meta.default_value_or_mandatory,
        )
        # For each parameter metadata object yielded by this generator.
        for param_meta in param_meta_generator
    )
