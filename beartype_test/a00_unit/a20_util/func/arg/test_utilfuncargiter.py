#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable argument iterator utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.arg.utilfuncargiter` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ iterator                   }....................
def test_iter_func_args() -> None:
    '''
    Test the
    :func:`beartype._util.func.arg.utilfuncargtest.iter_func_args` generator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.arg.utilfuncargiter import (
        ArgKind,
        ArgMandatory,
        iter_func_args,
    )
    from beartype_test.a00_unit.data.func.data_func import (
        func_args_0,
        func_args_1_flex_mandatory,
        func_args_1_varpos,
        func_args_1_kwonly_mandatory,
        func_args_2_flex_mandatory,
        func_args_2_kwonly_mixed,
        func_args_3_flex_mandatory_optional_varkw,
        func_args_5_flex_mandatory_varpos_kwonly_varkw,
    )
    from beartype_test.a00_unit.data.func.data_pep570 import (
        func_args_2_posonly_mixed,
        func_args_10_all_except_flex_mandatory,
    )
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this iterator returns the empty generator for an argumentless
    # callable, explicitly coerced into a tuple to trivialize testing.
    assert len(tuple(iter_func_args(func_args_0))) == 0

    # Assert this iterator returns the expected generator for argumentative
    # callables accepting multiple kinds of parameters, explicitly coerced into
    # tuples to trivialize testing.
    assert tuple(iter_func_args(func_args_1_flex_mandatory)) == (
        (ArgKind.POSITIONAL_OR_KEYWORD, 'had_one_fair_daughter', ArgMandatory,),
    )
    assert tuple(iter_func_args(func_args_1_varpos)) == (
        (ArgKind.VAR_POSITIONAL, 'and_in_her_his_one_delight', ArgMandatory,),
    )
    assert tuple(iter_func_args(func_args_1_kwonly_mandatory)) == (
        (ArgKind.KEYWORD_ONLY, 'when_can_I_take_you_from_this_place', ArgMandatory,),
    )
    assert tuple(iter_func_args(func_args_2_flex_mandatory)) == (
        (ArgKind.POSITIONAL_OR_KEYWORD, 'thick_with_wet_woods', ArgMandatory,),
        (ArgKind.POSITIONAL_OR_KEYWORD, 'and_many_a_beast_therein', ArgMandatory,),
    )
    assert tuple(iter_func_args(func_args_2_kwonly_mixed)) == (
        (ArgKind.KEYWORD_ONLY, 'white_summer', 'So far I have gone to see you again.',),
        (ArgKind.KEYWORD_ONLY, 'hiding_your_face_in_the_palm_of_your_hands', ArgMandatory,),
    )
    assert tuple(iter_func_args(func_args_3_flex_mandatory_optional_varkw)) == (
        (ArgKind.POSITIONAL_OR_KEYWORD, 'and_the_wolf_tracks_her_there', ArgMandatory,),
        (ArgKind.POSITIONAL_OR_KEYWORD, 'how_hideously', "Its shapes are heap'd around!",),
        (ArgKind.VAR_KEYWORD, 'rude_bare_and_high', ArgMandatory,),
    )
    assert tuple(iter_func_args(func_args_5_flex_mandatory_varpos_kwonly_varkw)) == (
        (ArgKind.POSITIONAL_OR_KEYWORD, 'we_are_selfish_men', ArgMandatory,),
        (ArgKind.POSITIONAL_OR_KEYWORD, 'oh_raise_us_up', ArgMandatory,),
        (ArgKind.VAR_POSITIONAL, 'and_give_us', ArgMandatory,),
        (ArgKind.KEYWORD_ONLY, 'return_to_us_again', 'Of inward happiness.',),
        (ArgKind.VAR_KEYWORD, 'manners_virtue_freedom_power', ArgMandatory,),
    )

    # ....................{ PASS ~ positional-only         }....................
    # Assert this iterator returns the expected generator for argumentative
    # callables accepting multiple kinds of parameters -- including
    # positional-only parameters.
    assert tuple(iter_func_args(func_args_2_posonly_mixed)) == (
        (ArgKind.POSITIONAL_ONLY, 'before_spreading_his_black_wings', ArgMandatory,),
        (ArgKind.POSITIONAL_ONLY, 'reaching_for_the_skies', 'in this forest',),
    )
    assert tuple(iter_func_args(func_args_10_all_except_flex_mandatory)) == (
        (ArgKind.POSITIONAL_ONLY, 'in_solitude_i_wander', ArgMandatory,),
        (ArgKind.POSITIONAL_ONLY, 'through_the_vast_enchanted_forest', ArgMandatory,),
        (ArgKind.POSITIONAL_ONLY, 'the_surrounding_skies', 'are one',),
        (ArgKind.POSITIONAL_OR_KEYWORD, 'torn_apart_by', 'the phenomenon of lightning',),
        (ArgKind.POSITIONAL_OR_KEYWORD, 'rain_is_pouring_down', 'my now shivering shoulders',),
        (ArgKind.VAR_POSITIONAL, 'in_the_rain_my_tears_are_forever_lost', ArgMandatory,),
        (ArgKind.KEYWORD_ONLY, 'the_darkened_oaks_are_my_only_shelter', ArgMandatory,),
        (ArgKind.KEYWORD_ONLY, 'red_leaves_are_blown_by', 'the wind',),
        (ArgKind.KEYWORD_ONLY, 'an_ebony_raven_now_catches', 'my eye.',),
        (ArgKind.VAR_KEYWORD, 'sitting_in_calmness', ArgMandatory,),
    )

    # ....................{ FAIL                           }....................
    # Assert this iterator returns a generator raising the expected exception
    # when passed a C-based callable.
    with raises(_BeartypeUtilCallableException):
        next(iter_func_args(iter))
