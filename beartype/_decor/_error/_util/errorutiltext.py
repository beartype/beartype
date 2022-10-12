#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype error-handling string munging utilities** (i.e., functions returning
substrings intended to be embedded in strings explaining type hint violations).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._util.text.utiltextcolour import (
    colour_error,
    colour_repr,
)
from beartype._util.text.utiltextlabel import (
    label_type,
    prefix_callable_decorated,
    prefix_callable_decorated_return,
)
from beartype._util.text.utiltextrepr import represent_object
from collections.abc import Callable

# ....................{ PREFIXERS                          }....................
def prefix_callable_decorated_arg_value(
    func: Callable, arg_name: str, arg_value: object) -> str:
    '''
    Human-readable label describing the parameter with the passed name and
    trimmed value of the passed **decorated callable** (i.e., callable wrapped
    by the :func:`beartype.beartype` decorator with a wrapper function
    type-checking that callable) suffixed by delimiting whitespace.

    Parameters
    ----------
    func : Callable
        Decorated callable to be labelled.
    arg_name : str
        Name of the parameter of this callable to be labelled.
    arg_value : object
        Value of the parameter of this callable to be labelled.

    Returns
    ----------
    str
        Human-readable label describing this parameter's name and value.
    '''
    assert isinstance(arg_name, str), f'{repr(arg_name)} not string.'

    # Human-readable string depicting this parameter name and value.
    arg_name_value = colour_repr(f'{arg_name}={represent_object(arg_value)}')

    # Create and return this label.
    return f'{prefix_callable_decorated(func)}parameter {arg_name_value}'


def prefix_callable_decorated_return_value(
    func: Callable, return_value: object) -> str:
    '''
    Human-readable label describing the passed trimmed return value of the
    passed **decorated callable** (i.e., callable wrapped by the
    :func:`beartype.beartype` decorator with a wrapper function type-checking
    that callable) suffixed by delimiting whitespace.

    Parameters
    ----------
    func : Callable
        Decorated callable to be labelled.
    return_value : object
        Value returned by this callable to be labelled.

    Returns
    ----------
    str
        Human-readable label describing this return value.
    '''

    # Create and return this label.
    return (
        f'{prefix_callable_decorated_return(func)} '
        f'{colour_repr(represent_object(return_value))} '
    )

# ....................{ REPRESENTERS                       }....................
def represent_pith(pith: object) -> str:
    '''
    Human-readable description of the passed **pith** (i.e., arbitrary object
    violating the current type check) intended to be embedded in an exception
    message explaining this violation.

    Parameters
    ----------
    pith : object
        Arbitrary object violating the current type check.

    Returns
    ----------
    str
        Human-readable description of this object.
    '''

    return (
        f'{colour_error(label_type(type(pith)))} '
        f'{colour_repr(represent_object(pith))}'
    )
