#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator parameter PEP-noncompliant type checking.**

This private submodule dynamically generates pure-Python code type-checking all
parameters annotated with **PEP-noncompliant type hints** (e.g., tuple unions,
fully-qualified forward references) of the callable currently being decorated
by the :func:`beartype.beartype` decorator.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorParamNameException
from beartype._decor._code import _codehint
from beartype._decor._code._codehint import HINTS_IGNORABLE
from beartype._decor._code._snippet import (
    CODE_PARAM_VARIADIC_POSITIONAL,
    CODE_PARAM_KEYWORD_ONLY,
    CODE_PARAM_POSITIONAL_OR_KEYWORD,
    CODE_PARAM_HINT,
)
from beartype._decor._data import BeartypeData
from inspect import Parameter, Signature

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CODERS                            }....................
def nonpep_code_check_param(data: BeartypeData) -> str:
    '''
    Python code snippet type-checking all parameters annotated with
    **PEP-noncompliant type hints** (e.g., tuple unions, fully-qualified
    forward references) of the decorated callable if any *or* the empty string
    otherwise (i.e., if these parameters are unannotated).

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be type-checked.

    Returns
    ----------
    str
        Python code snippet type-checking all annotated parameters declared by
        the decorated callable if any *or* the empty string otherwise.

    Raises
    ----------
    BeartypeDecorParamNameException
        If the name of any parameter declared on this callable is prefixed by
        the reserved substring ``__beartype_``.
    BeartypeDecorHintTupleItemException
        If any item of any **type-hinted tuple** (i.e., tuple applied as a
        parameter or return value annotation) is of an unsupported type.
        Supported types include:

        * :class:`type` (i.e., classes).
        * :class:`str` (i.e., strings).
    '''
    assert isinstance(data, BeartypeData), (
        '{!r} not @beartype data.'.format(data))

    # Python code snippet to be returned.
    func_code = ''

