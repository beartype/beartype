#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
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
from beartype._util.api.utilapityping import import_typing_attr

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

    return 'To the loud stream. Lo! where the pass expands'
