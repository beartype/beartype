#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`612` **data submodule.**

This submodule exercises :pep:`612` support implemented in the
:func:`beartype.beartype` decorator by declaring callables accepting both
variadic positional and keyword parameters annotated as the corresponding
instance variables of a :pep:`612`-compliant **parameter specification** (i.e.,
:class:`typing.ParamSpec` object).

Caveats
-------
**This submodule requires either** the standard :class:`typing.ParamSpec` class
*or* the third-party :class:`typing_extensions.ParamSpec` class to be importable
under the active Python interpreter. If this is *not* the case, importing this
submodule raises an :exc:`beartype.roar._BeartypeUtilModuleException` exception.
'''

# ....................{ IMPORTS                            }....................
from beartype._util.api.standard.utiltyping import import_typing_attr

ParamSpec = import_typing_attr('ParamSpec')
'''
PEP 612-compliant ``ParamSpec`` class imported from either the standard
:mod:`typing` or third-party :mod:`typing_extensions` modules if importable from
at least one of those modules *or* raise an exception otherwise.
'''

# ....................{ GLOBALS                            }....................
P = ParamSpec('P')
'''
Arbitrary parameter specification.
'''


S = ParamSpec('S')
'''
Arbitrary parameter specification.
'''

# ....................{ CALLABLES                          }....................
def func_args_paramspec_return_hinted(
    *to_the_loud_stream: P.args,
    **lo_where_the_pass_expands: P.kwargs,
) -> bytes:
    '''
    Arbitrary callable annotated by a return type hint accepting variadic
    positional and keyword parameters annotated as the corresponding instance
    variables of a :pep:`612`-compliant parameter specification.
    '''

    return b'To the loud stream. Lo! where the pass expands'


def func_args_flex_mandatory_paramspec_return_hinted(
    and_seems: int,
    with_its_accumulated_crags: bool,
    *its_stony_jaws: P.args,
    **the_abrupt_mountain_breaks: P.kwargs,
) -> str:
    '''
    Arbitrary callable annotated by a return type hint accepting one or more
    annotated mandatory flexible parameters *and* variadic positional and
    keyword parameters annotated as the corresponding instance variables of a
    :pep:`612`-compliant parameter specification.
    '''

    return 'Its stony jaws, the abrupt mountain breaks,'


def func_args_flex_mandatory_paramspec_varposonly_return_hinted(
    dim_tracts_and_vast: int,
    robed_in_the_lustrous_gloom: float,
    *of_leaden_coloured_even_and_fiery_hills: P.args,
) -> bytes:
    '''
    Arbitrary callable annotated by a return type hint accepting one or more
    annotated mandatory flexible parameters and a variadic positional parameter
    annotated as the corresponding instance variable of a :pep:`612`-compliant
    parameter specification with *no* variadic keyword parameter.
    '''

    return b'Of leaden-coloured even, and fiery hills'


def func_args_flex_mandatory_paramspec_varkwonly_return_hinted(
    mingling_their_flames: bool,
    with_twilight: bytes,
    **on_the_verge: P.kwargs,
) -> str:
    '''
    Arbitrary callable annotated by a return type hint accepting one or more
    annotated mandatory flexible parameters and a variadic keyword parameter
    annotated as the corresponding instance variable of a :pep:`612`-compliant
    parameter specification with *no* variadic positional parameter.
    '''

    return 'Mingling their flames with twilight, on the verge'


def func_args_flex_mandatory_paramspec_distinct_return_hinted(
    of_the_remote_horizon: float,
    the_near_scene: int,
    *in_naked: P.args,
    **and_severe_simplicity: S.kwargs,
) -> bytes:
    '''
    Arbitrary callable annotated by a return type hint accepting one or more
    annotated mandatory flexible parameters, a variadic positional parameter
    annotated as the corresponding instance variable of a :pep:`612`-compliant
    parameter specification, and a variadic keyword parameter annotated as the
    corresponding instance variable of a completely different
    :pep:`612`-compliant parameter specification.
    '''

    return b'In naked and severe simplicity,'


def func_args_flex_mandatory_kwonly_optional_paramspec_return_hinted(
    to_overhang_the_world: float,
    for_wide_expand: complex,
    *islanded_seas_blue_mountains: P.args,
    beneath_the_wan_stars: str = 'Beneath the wan stars and descending moon',
    **mighty_streams: P.kwargs,
) -> bytes:
    '''
    Arbitrary callable annotated by a return type hint accepting one or more
    annotated mandatory flexible parameters, an annotated optional keyword-only
    parameter, *and* variadic positional and keyword parameters annotated as the
    corresponding instance variables of a :pep:`612`-compliant parameter
    specification.
    '''

    return b'To overhang the world: for wide expand'
