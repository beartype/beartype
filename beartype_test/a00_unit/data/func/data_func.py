#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **sample callable** submodule.

This submodule predefines sample pure-Python callables exercising known edge
cases on behalf of higher-level unit test submodules.
'''

# ....................{ IMPORTS                            }....................
from beartype_test.a00_unit.data.data_type import decorator_isomorphic
from typing import Union

# ....................{ CALLABLES                          }....................
def func_args_0() -> str:
    '''
    Arbitrary callable accepting *no* parameters.
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


def func_args_2_flex_mandatory(
    thick_with_wet_woods: str, and_many_a_beast_therein: str) -> str:
    '''
    Arbitrary callable accepting two or more mandatory flexible parameters.
    '''

    return 'For here between the man and beast we die.'


def func_args_3_flex_mandatory_optional_varkw(
    and_the_wolf_tracks_her_there: str,
    how_hideously: str = "Its shapes are heap'd around!",
    **rude_bare_and_high
) -> str:
    '''
    Arbitrary callable accepting one mandatory flexible parameter, one optional
    flexible parameter, and one variadic keyword parameter.

    This test exercises a recent failure in our pre-0.10.0 release cycle:
        https://github.com/beartype/beartype/issues/78
    '''

    return "Ghastly, and scarr'd, and riven.—Is this the scene"


# ....................{ CALLABLES ~ pep 3102               }....................
# Keyword-only keywords require PEP 3102 compliance, which has thankfully been
# available since Python >= 3.0.

def func_args_1_kwonly_mandatory(
    *, when_can_I_take_you_from_this_place: str) -> str:
    '''
    Arbitrary callable accepting one mandatory keyword-only parameter.
    '''

    return 'When is the word but a sigh?'


def func_args_2_kwonly_mixed(
    *,
    white_summer: Union[dict, str] = 'So far I have gone to see you again.',
    hiding_your_face_in_the_palm_of_your_hands: Union[set, str],
) -> Union[tuple, str]:
    '''
    Arbitrary callable passed one optional keyword-only parameter and one
    mandatory keyword-only parameter (in that non-standard and quite
    counter-intuitive order), each annotated with PEP-compliant type hints.
    '''

    return white_summer + '\n' + hiding_your_face_in_the_palm_of_your_hands


def func_args_5_flex_mandatory_varpos_kwonly_varkw(
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

# ....................{ CALLABLES ~ wrapped                }....................
# Callables wrapped by a decorator wrapper reducing their signatures to the
# standard parameter-passing idiom for decorators trivially implemented as
# closures (i.e., *NOT* @beartype-style decorators):
#     def wrapper(*args, **kwargs): ...

func_args_0_wrapped = decorator_isomorphic(
    func_args_0)
func_args_1_flex_mandatory_wrapped = decorator_isomorphic(
    func_args_1_flex_mandatory)
func_args_1_varpos_wrapped = decorator_isomorphic(
    func_args_1_varpos)
func_args_2_flex_mandatory_wrapped = decorator_isomorphic(
    func_args_2_flex_mandatory)
func_args_3_flex_mandatory_optional_varkw_wrapped = decorator_isomorphic(
    func_args_3_flex_mandatory_optional_varkw)
