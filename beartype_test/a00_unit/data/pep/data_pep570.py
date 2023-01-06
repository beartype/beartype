#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`570` **data submodule.**

This submodule exercises :pep:`570` support for positional-only parameters
implemented in the :func:`beartype.beartype` decorator by declaring callables
accepting one or more positional-only parameters. For safety, these callables
are intentionally isolated from the main codebase.

Caveats
----------
**This submodule requires the active Python interpreter to target at least
Python 3.8.0.** If this is *not* the case, importing this submodule raises an
:class:`SyntaxError` exception.
'''

# ....................{ IMPORTS                           }....................
from typing import Union

# ....................{ CALLABLES                         }....................
def pep570_posonly(
    now_take_away_that_flesh: Union[bytearray, str],
    take_away_the_teeth: Union[bool, str] = ('and the tongue'),
    /,
) -> Union[list, str]:
    '''
    Arbitrary :pep:`570`-compliant callable passed a mandatory and optional
    positional-only parameter, all annotated with PEP-compliant type hints.
    '''

    return now_take_away_that_flesh + '\n' + take_away_the_teeth


def pep570_posonly_flex_varpos_kwonly(
    all_of_your_nightmares: Union[bytearray, str],
    for_a_time_obscured: Union[bool, str] = (
        'As by a shining brainless beacon'),
    /,
    or_a_blinding_eclipse: Union[bytes, str] = (
        'Or a blinding eclipse of the many terrible shapes of this world,'),
    *you_are_calm_and_joyful: Union[float, str],
    your_special_plan: Union[int, str],
) -> Union[list, str]:
    '''
    Arbitrary :pep:`570`-compliant callable passed a mandatory positional-only
    parameter, optional positional-only parameter, flexible parameter, variadic
    positional parameter, and keyword-only parameter, all annotated with
    PEP-compliant type hints.
    '''

    return (
        all_of_your_nightmares + '\n' +
        for_a_time_obscured + '\n' +
        or_a_blinding_eclipse + '\n' +
        '\n'.join(you_are_calm_and_joyful) + '\n' +
        your_special_plan
    )
