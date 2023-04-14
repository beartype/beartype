#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **text prefix utilities** (i.e., low-level callables creating and
returning human-readable strings describing prominent objects or types and
*always* suffixed by exactly one space character, intended to prefix
human-readable error messages).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._util.text.utiltextlabel import label_callable
from collections.abc import Callable

# ....................{ PREFIXERS ~ callable               }....................
def prefix_callable(func: Callable) -> str:
    '''
    Human-readable label describing the passed **callable** (e.g., function,
    method, property) suffixed by delimiting whitespace.

    Parameters
    ----------
    func : Callable
        Callable to be labelled.

    Returns
    ----------
    str
        Human-readable label describing this callable.
    '''

    # Testify, beartype!
    return f'{label_callable(func)} '


def prefix_callable_decorated(func: Callable) -> str:
    '''
    Human-readable label describing the passed **decorated callable** (i.e.,
    callable wrapped by the :func:`beartype.beartype` decorator with a wrapper
    function type-checking that callable) suffixed by delimiting whitespace.

    Parameters
    ----------
    func : Callable
        Decorated callable to be labelled.

    Returns
    ----------
    str
        Human-readable label describing this decorated callable.
    '''

    # Create and return this label.
    return f'@beartyped {prefix_callable(func)}'


def prefix_callable_decorated_pith(
    func: Callable, pith_name: str) -> str:
    '''
    Human-readable label describing either the parameter with the passed name
    *or* return value if this name is ``return`` of the passed **decorated
    callable** (i.e., callable wrapped by the :func:`beartype.beartype`
    decorator with a wrapper function type-checking that callable) suffixed by
    delimiting whitespace.

    Parameters
    ----------
    func : Callable
        Decorated callable to be labelled.
    pith_name : str
        Name of the parameter or return value of this callable to be labelled.

    Returns
    ----------
    str
        Human-readable label describing either the name of this parameter *or*
        this return value.
    '''
    assert isinstance(pith_name, str), f'{repr(pith_name)} not string.'

    # Return a human-readable label describing either...
    return (
        # If this name is "return", the return value of this callable.
        prefix_callable_decorated_return(func)
        if pith_name == 'return' else
        # Else, the parameter with this name of this callable.
        prefix_callable_decorated_arg(func=func, arg_name=pith_name)
    )

# ....................{ PREFIXERS ~ callable : param       }....................
def prefix_callable_decorated_arg(
    func: Callable, arg_name: str) -> str:
    '''
    Human-readable label describing the parameter with the passed name of the
    passed **decorated callable** (i.e., callable wrapped by the
    :func:`beartype.beartype` decorator with a wrapper function type-checking
    that callable) suffixed by delimiting whitespace.

    Parameters
    ----------
    func : Callable
        Decorated callable to be labelled.
    arg_name : str
        Name of the parameter of this callable to be labelled.

    Returns
    ----------
    str
        Human-readable label describing this parameter's name.
    '''
    assert isinstance(arg_name, str), f'{repr(arg_name)} not string.'

    # Create and return this label.
    return f'{prefix_callable_decorated(func)}parameter "{arg_name}" '

# ....................{ PREFIXERS ~ callable : return      }....................
def prefix_callable_decorated_return(func: Callable) -> str:
    '''
    Human-readable label describing the return of the passed **decorated
    callable** (i.e., callable wrapped by the :func:`beartype.beartype`
    decorator with a wrapper function type-checking that callable) suffixed by
    delimiting whitespace.

    Parameters
    ----------
    func : Callable
        Decorated callable to be labelled.

    Returns
    ----------
    str
        Human-readable label describing this return.
    '''

    # Create and return this label.
    return f'{prefix_callable_decorated(func)}return '
