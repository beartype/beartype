#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`570` **data submodule.**

This submodule exercises :pep:`570` support implemented in the
:func:`beartype.beartype` decorator by declaring callables accepting one or
more **positional-only parameters** (i.e., parameters that *must* be passed
positionally, syntactically followed in the signatures of their callables by
the :pep:`570`-compliant ``/,`` pseudo-parameter).
'''

# ....................{ IMPORTS                            }....................
from typing import Union

# ....................{ CALLABLES                          }....................
def func_args_2_posonly_mixed(
    before_spreading_his_black_wings: Union[bytearray, str],
    reaching_for_the_skies: Union[bool, str] = 'in this forest',
    /,
) -> Union[list, str]:
    '''
    Arbitrary :pep:`570`-compliant callable passed a mandatory and optional
    positional-only parameter, all annotated with PEP-compliant type hints.
    '''

    return (
        before_spreading_his_black_wings + '\n' + reaching_for_the_skies)


def func_args_10_all_except_flex_mandatory(
    in_solitude_i_wander,
    through_the_vast_enchanted_forest,
    the_surrounding_skies='are one',
    /,
    torn_apart_by='the phenomenon of lightning',
    rain_is_pouring_down='my now shivering shoulders',
    *in_the_rain_my_tears_are_forever_lost,
    the_darkened_oaks_are_my_only_shelter,
    red_leaves_are_blown_by='the wind',
    an_ebony_raven_now_catches='my eye.',
    **sitting_in_calmness,
) -> str:
    '''
    Arbitrary :pep:`570`-compliant callable accepting all possible kinds of
    parameters, including both mandatory and optional variants of these kinds
    except mandatory flexible parameters.

    Since callables cannot by definition accept both optional positional-only
    parameters *and* mandatory flexible parameters, this callable necessarily
    omits the latter in favour of the former.
    '''

    # Arbitrary local variable declared in the body of this callable.
    before_spreading_his_black_wings = 'Reaching for the skies.'
    return before_spreading_his_black_wings
