#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable parameter getter utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.func.arg.utilfuncargget` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ metadata                   }....................
def test_get_func_arg_name_to_kind_default() -> None:
    '''
    Test the
    :func:`beartype._util.func.arg.utilfuncargget.get_func_arg_name_to_kind_default`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.arg.utilfuncargget import (
        get_func_arg_name_to_kind_default)
    from beartype._util.func.arg.utilfuncargiter import (
        ArgKind,
        ArgMandatory,
    )
    from beartype_test.a00_unit.data.func.data_func import (
        ClassOfMethods,
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

    # ....................{ LOCALS                         }....................
    # Instance of an arbitrary class defining various kinds of methods, which
    # due to this instantiation have now been implicitly coerced into bound
    # method descriptors, which this iterator explicitly supports.
    object_of_methods = ClassOfMethods()

    # ..................{ CASES                              }..................
    # Tuple of 2-tuples "(callable_input, getter_expect)", where:
    # * "callable_input" is the callable to be passed to the
    #   get_func_arg_name_to_kind_default() getter.
    # * "getter_expect" is the dictionary expected to be returned by this getter
    #   when passed that callable.
    GETTER_CASES = (
        # ..................{ ARGUMENTLESS                   }..................
        # This getter returns the empty dictionary when passed an argumentless
        # callable (i.e., callable accepting *NO* parameters).
        (func_args_0, {}),

        # ..................{ ARGUMENTATIVE                  }..................
        # This getter returns non-empty dictionaries when passed argumentative
        # callables accepting multiple kinds of parameters.
        (func_args_1_flex_mandatory, {
            'had_one_fair_daughter': (ArgKind.POSITIONAL_OR_KEYWORD, ArgMandatory,),
        }),
        (func_args_1_varpos, {
            'and_in_her_his_one_delight': (ArgKind.VARIADIC_POSITIONAL, ArgMandatory,),
        }),
        (func_args_1_kwonly_mandatory, {
            'when_can_I_take_you_from_this_place': (ArgKind.KEYWORD_ONLY, ArgMandatory,),
        }),
        (func_args_2_flex_mandatory, {
            'thick_with_wet_woods': (ArgKind.POSITIONAL_OR_KEYWORD, ArgMandatory,),
            'and_many_a_beast_therein': (ArgKind.POSITIONAL_OR_KEYWORD, ArgMandatory,),
        }),
        (func_args_2_kwonly_mixed, {
            'white_summer': (ArgKind.KEYWORD_ONLY, 'So far I have gone to see you again.',),
            'hiding_your_face_in_the_palm_of_your_hands': (ArgKind.KEYWORD_ONLY, ArgMandatory,),
        }),
        (func_args_3_flex_mandatory_optional_varkw, {
            'and_the_wolf_tracks_her_there': (ArgKind.POSITIONAL_OR_KEYWORD, ArgMandatory,),
            'how_hideously': (ArgKind.POSITIONAL_OR_KEYWORD, "Its shapes are heap'd around!",),
            'rude_bare_and_high': (ArgKind.VARIADIC_KEYWORD, ArgMandatory,),
        }),
        (func_args_5_flex_mandatory_varpos_kwonly_varkw, {
            'we_are_selfish_men': (ArgKind.POSITIONAL_OR_KEYWORD, ArgMandatory,),
            'oh_raise_us_up': (ArgKind.POSITIONAL_OR_KEYWORD, ArgMandatory,),
            'and_give_us': (ArgKind.VARIADIC_POSITIONAL, ArgMandatory,),
            'return_to_us_again': (ArgKind.KEYWORD_ONLY, 'Of inward happiness.',),
            'manners_virtue_freedom_power': (ArgKind.VARIADIC_KEYWORD, ArgMandatory,),
        }),

        # This getter returns a non-empty dictionary when passed an
        # argumentative bound method descriptor accepting multiple kinds of
        # parameters.
        #
        # Note that this getter intentionally omits the first "self" parameter
        # passed by this descriptor to the unbound method it encapsulates.
        (object_of_methods.meth_args_6_flex_mandatory_varpos_kwonly_varkw, {
            'calm_and_rejoicing': (ArgKind.POSITIONAL_OR_KEYWORD, ArgMandatory,),
            'in_the_fearful_war': (ArgKind.POSITIONAL_OR_KEYWORD, ArgMandatory,),
            'of_wave_ruining_on_wave': (ArgKind.VARIADIC_POSITIONAL, ArgMandatory,),
            'and_blast_on_blast': (ArgKind.KEYWORD_ONLY, 'Descending,',),
            'and_black_flood': (ArgKind.VARIADIC_KEYWORD, ArgMandatory,),
        }),

        # ..................{ ARGUMENTATIVE ~ positional-only}..................
        # This getter returns non-empty dictionaries when passed argumentative
        # callables accepting multiple kinds of parameters -- including
        # positional-only parameters.
        (func_args_2_posonly_mixed, {
            'before_spreading_his_black_wings': (ArgKind.POSITIONAL_ONLY, ArgMandatory,),
            'reaching_for_the_skies': (ArgKind.POSITIONAL_ONLY, 'in this forest',),
        }),
        (func_args_10_all_except_flex_mandatory, {
            'in_solitude_i_wander': (ArgKind.POSITIONAL_ONLY, ArgMandatory,),
            'through_the_vast_enchanted_forest': (ArgKind.POSITIONAL_ONLY, ArgMandatory,),
            'the_surrounding_skies': (ArgKind.POSITIONAL_ONLY, 'are one',),
            'torn_apart_by': (ArgKind.POSITIONAL_OR_KEYWORD, 'the phenomenon of lightning',),
            'rain_is_pouring_down': (ArgKind.POSITIONAL_OR_KEYWORD, 'my now shivering shoulders',),
            'in_the_rain_my_tears_are_forever_lost': (ArgKind.VARIADIC_POSITIONAL, ArgMandatory,),
            'the_darkened_oaks_are_my_only_shelter': (ArgKind.KEYWORD_ONLY, ArgMandatory,),
            'red_leaves_are_blown_by': (ArgKind.KEYWORD_ONLY, 'the wind',),
            'an_ebony_raven_now_catches': (ArgKind.KEYWORD_ONLY, 'my eye.',),
            'sitting_in_calmness': (ArgKind.VARIADIC_KEYWORD, ArgMandatory,),
        }),
    )

    # ....................{ PASS                           }....................
    # For each valid use case to validate the iter_func_args() generator factory
    # against...
    for getter_case in GETTER_CASES:
        # Callable to be passed to this getter.
        callable_input = getter_case[0]

        # Dictionary expected to be returned by this getter when passed that
        # callable.
        getter_expect = getter_case[1]

        # Dictionary actually returned by this getter when passed that
        # callable.
        getter_actual = get_func_arg_name_to_kind_default(callable_input)

        # Assert that this getter returns the expected dictionary when passed
        # that callable.
        assert getter_actual == getter_expect

    # ....................{ FAIL                           }....................
    # Assert that this getter raises the expected exception when passed a
    # C-based callable.
    with raises(_BeartypeUtilCallableException):
        get_func_arg_name_to_kind_default(iter)

# ....................{ TESTS ~ name                       }....................
def test_get_func_arg_name_first_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.func.arg.utilfuncargget.get_func_arg_name_first_or_none`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.arg.utilfuncargget import (
        get_func_arg_name_first_or_none)
    from beartype_test.a00_unit.data.func.data_func import (
        func_args_0_wrapped,
        func_args_1_varpos_wrapped,
        func_args_3_flex_mandatory_optional_varkw_wrapped,
    )
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this getter returns "None" for argumentless callables.
    assert get_func_arg_name_first_or_none(func_args_0_wrapped) is None

    # Assert this getter returns the expected names of the first parameters
    # accepted by argumentative callables.
    assert get_func_arg_name_first_or_none(func_args_1_varpos_wrapped) == (
        'and_in_her_his_one_delight')
    assert get_func_arg_name_first_or_none(
        func_args_3_flex_mandatory_optional_varkw_wrapped) == (
        'and_the_wolf_tracks_her_there')

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed a C-based
    # callable.
    with raises(_BeartypeUtilCallableException):
        get_func_arg_name_first_or_none(iter)


def test_get_func_arg_names() -> None:
    '''
    Test the
    :func:`beartype._util.func.arg.utilfuncargget.get_func_arg_names`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.arg.utilfuncargget import get_func_arg_names
    from beartype_test.a00_unit.data.func.data_func import (
        func_args_0_wrapped,
        func_args_1_varpos_wrapped,
        func_args_3_flex_mandatory_optional_varkw_wrapped,
        func_args_5_flex_mandatory_varpos_kwonly_varkw_wrapped,
    )
    from beartype_test.a00_unit.data.func.data_pep570 import (
        func_args_10_all_except_flex_mandatory)
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this getter when passed an argumentless callable returns the empty
    # list.
    assert get_func_arg_names(func_args_0_wrapped) == ()

    # Assert this getter when passed argumentative callables returns the
    # expected lists of the names of the parameters accepted by these callables.
    assert get_func_arg_names(func_args_1_varpos_wrapped) == (
        'and_in_her_his_one_delight',)
    assert get_func_arg_names(
        func_args_3_flex_mandatory_optional_varkw_wrapped) == (
        'and_the_wolf_tracks_her_there',
        'how_hideously',
        'rude_bare_and_high',
    )
    assert get_func_arg_names(
        func_args_5_flex_mandatory_varpos_kwonly_varkw_wrapped) == (
        'we_are_selfish_men',
        'oh_raise_us_up',
        'return_to_us_again',
        'and_give_us',
        'manners_virtue_freedom_power',
    )

    assert get_func_arg_names(
        func_args_10_all_except_flex_mandatory) == (
        'in_solitude_i_wander',
        'through_the_vast_enchanted_forest',
        'the_surrounding_skies',
        'torn_apart_by',
        'rain_is_pouring_down',
        'the_darkened_oaks_are_my_only_shelter',
        'red_leaves_are_blown_by',
        'an_ebony_raven_now_catches',
        'in_the_rain_my_tears_are_forever_lost',
        'sitting_in_calmness',
    )

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed a C-based
    # callable.
    with raises(_BeartypeUtilCallableException):
        get_func_arg_names(iter)
