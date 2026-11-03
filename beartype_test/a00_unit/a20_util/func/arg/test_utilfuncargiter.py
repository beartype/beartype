#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
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
    :func:`beartype._util.func.arg.utilfuncargiter.iter_func_args` generator.
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
    # Tuple of 2-tuples "(callable_input, iter_func_args_expect)", where:
    # * "callable_input" is the callable to be passed to the iter_func_args()
    #   generator factory.
    # * "iter_func_args_expect" is the tuple of metadata tuples expected to be
    #   returned by this generator factory when passed that callable.
    ITER_FUNC_ARGS_CASES = (
        # ..................{ ARGUMENTLESS                   }..................
        # This generator factory returns the empty generator when passed an
        # argumentless callable (i.e., callable accepting *NO* parameters).
        (func_args_0, ()),

        # ..................{ ARGUMENTATIVE                  }..................
        # This generator factory returns non-empty generators when passed
        # argumentative callables accepting multiple kinds of parameters.
        (func_args_1_flex_mandatory, (
            (ArgKind.POSITIONAL_OR_KEYWORD, 'had_one_fair_daughter', ArgMandatory,),
        )),
        (func_args_1_varpos, (
            (ArgKind.VARIADIC_POSITIONAL, 'and_in_her_his_one_delight', ArgMandatory,),
        )),
        (func_args_1_kwonly_mandatory, (
            (ArgKind.KEYWORD_ONLY, 'when_can_I_take_you_from_this_place', ArgMandatory,),
        )),
        (func_args_2_flex_mandatory, (
            (ArgKind.POSITIONAL_OR_KEYWORD, 'thick_with_wet_woods', ArgMandatory,),
            (ArgKind.POSITIONAL_OR_KEYWORD, 'and_many_a_beast_therein', ArgMandatory,),
        )),
        (func_args_2_kwonly_mixed, (
            (ArgKind.KEYWORD_ONLY, 'white_summer', 'So far I have gone to see you again.',),
            (ArgKind.KEYWORD_ONLY, 'hiding_your_face_in_the_palm_of_your_hands', ArgMandatory,),
        )),
        (func_args_3_flex_mandatory_optional_varkw, (
            (ArgKind.POSITIONAL_OR_KEYWORD, 'and_the_wolf_tracks_her_there', ArgMandatory,),
            (ArgKind.POSITIONAL_OR_KEYWORD, 'how_hideously', "Its shapes are heap'd around!",),
            (ArgKind.VARIADIC_KEYWORD, 'rude_bare_and_high', ArgMandatory,),
        )),
        (func_args_5_flex_mandatory_varpos_kwonly_varkw, (
            (ArgKind.POSITIONAL_OR_KEYWORD, 'we_are_selfish_men', ArgMandatory,),
            (ArgKind.POSITIONAL_OR_KEYWORD, 'oh_raise_us_up', ArgMandatory,),
            (ArgKind.VARIADIC_POSITIONAL, 'and_give_us', ArgMandatory,),
            (ArgKind.KEYWORD_ONLY, 'return_to_us_again', 'Of inward happiness.',),
            (ArgKind.VARIADIC_KEYWORD, 'manners_virtue_freedom_power', ArgMandatory,),
        )),

        # This generator factory returns a non-empty generator when passed an
        # argumentative bound method descriptor accepting multiple kinds of
        # parameters.
        #
        # Note that this generator intentionally omits the first "self"
        # parameter passed by this descriptor to the unbound method it
        # encapsulates.
        (object_of_methods.meth_args_6_flex_mandatory_varpos_kwonly_varkw, (
            (ArgKind.POSITIONAL_OR_KEYWORD, 'calm_and_rejoicing', ArgMandatory,),
            (ArgKind.POSITIONAL_OR_KEYWORD, 'in_the_fearful_war', ArgMandatory,),
            (ArgKind.VARIADIC_POSITIONAL, 'of_wave_ruining_on_wave', ArgMandatory,),
            (ArgKind.KEYWORD_ONLY, 'and_blast_on_blast', 'Descending,',),
            (ArgKind.VARIADIC_KEYWORD, 'and_black_flood', ArgMandatory,),
        )),

        # ..................{ ARGUMENTATIVE ~ positional-only}..................
        # This generator factory returns non-empty generators when passed
        # argumentative callables accepting multiple kinds of parameters --
        # including positional-only parameters.
        (func_args_2_posonly_mixed, (
            (ArgKind.POSITIONAL_ONLY, 'before_spreading_his_black_wings', ArgMandatory,),
            (ArgKind.POSITIONAL_ONLY, 'reaching_for_the_skies', 'in this forest',),
        )),
        (func_args_10_all_except_flex_mandatory, (
            (ArgKind.POSITIONAL_ONLY, 'in_solitude_i_wander', ArgMandatory,),
            (ArgKind.POSITIONAL_ONLY, 'through_the_vast_enchanted_forest', ArgMandatory,),
            (ArgKind.POSITIONAL_ONLY, 'the_surrounding_skies', 'are one',),
            (ArgKind.POSITIONAL_OR_KEYWORD, 'torn_apart_by', 'the phenomenon of lightning',),
            (ArgKind.POSITIONAL_OR_KEYWORD, 'rain_is_pouring_down', 'my now shivering shoulders',),
            (ArgKind.VARIADIC_POSITIONAL, 'in_the_rain_my_tears_are_forever_lost', ArgMandatory,),
            (ArgKind.KEYWORD_ONLY, 'the_darkened_oaks_are_my_only_shelter', ArgMandatory,),
            (ArgKind.KEYWORD_ONLY, 'red_leaves_are_blown_by', 'the wind',),
            (ArgKind.KEYWORD_ONLY, 'an_ebony_raven_now_catches', 'my eye.',),
            (ArgKind.VARIADIC_KEYWORD, 'sitting_in_calmness', ArgMandatory,),
        )),
    )

    # ....................{ PASS                           }....................
    # For each valid use case to validate the iter_func_args() generator factory
    # against...
    for iter_func_args_case in ITER_FUNC_ARGS_CASES:
        # Callable to be passed to this generator factory.
        callable_input = iter_func_args_case[0]

        # Tuple of metadata tuples expected to be returned by this generator
        # factory when passed that callable.
        iter_func_args_expect = iter_func_args_case[1]

        # Tuple of metadata tuples actually returned by this generator factory
        # when passed that callable.
        iter_func_args_actual = tuple(iter_func_args(callable_input))

        # Assert that this generator factory returns the expected tuple of
        # metadata tuples when passed that callable.
        assert iter_func_args_actual == iter_func_args_expect

    # ....................{ FAIL                           }....................
    # Assert this iterator returns a generator raising the expected exception
    # when passed a C-based callable.
    with raises(_BeartypeUtilCallableException):
        next(iter_func_args(iter))
