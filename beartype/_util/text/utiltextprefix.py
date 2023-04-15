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
from beartype._data.datakind import HINT_NAME_RETURN
from beartype._data.datatyping import BeartypeableT
from beartype._util.text.utiltextlabel import (
    label_beartypeable_kind,
    label_callable,
)
from collections.abc import Callable

# ....................{ PREFIXERS ~ beartypeable           }....................
def prefix_beartypeable(
    obj: BeartypeableT,  # pyright: ignore[reportInvalidTypeVarUse]
    **kwargs,
) -> str:
    '''
    Human-readable label describing the passed **beartypeable** (i.e., object
    that is currently being or has already been decorated by the
    :func:`beartype.beartype` decorator) suffixed by delimiting whitespace.

    Parameters
    ----------
    obj : BeartypeableT
        Beartypeable to be labelled.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`.label_beartypeable_kind` function transitively called by this
    higher-level function.

    Returns
    ----------
    str
        Human-readable label describing this beartypeable.
    '''

    # Human-readable label describing the kind the passed beartypeable.
    beartypeable_kind = label_beartypeable_kind(obj, **kwargs)

    # Create and return this label.
    return f'{beartypeable_kind} {label_callable(obj)} '  # type: ignore[arg-type]

# ....................{ PREFIXERS ~ beartypeable : pith    }....................
def prefix_beartypeable_pith(func: Callable, pith_name: str, **kwargs) -> str:
    '''
    Human-readable label describing either the parameter with the passed name
    *or* return value if this name is ``return`` of the passed **beartypeable
    callable** (i.e., callable wrapped by the :func:`beartype.beartype`
    decorator with a wrapper function type-checking that callable) suffixed by
    delimiting whitespace.

    Parameters
    ----------
    func : Callable
        Decorated callable to be labelled.
    pith_name : str
        Name of the parameter or return value of this callable to be labelled.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`.label_beartypeable_kind` function transitively called by this
    higher-level function.

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
        prefix_beartypeable_return(func, **kwargs)
        if pith_name == HINT_NAME_RETURN else
        # Else, the parameter with this name of this callable.
        prefix_beartypeable_arg(func=func, arg_name=pith_name, **kwargs)
    )


def prefix_beartypeable_arg(func: Callable, arg_name: str, **kwargs) -> str:
    '''
    Human-readable label describing the parameter with the passed name of the
    passed **beartypeable callable** (i.e., callable wrapped by the
    :func:`beartype.beartype` decorator with a wrapper function type-checking
    that callable) suffixed by delimiting whitespace.

    Parameters
    ----------
    func : Callable
        Decorated callable to be labelled.
    arg_name : str
        Name of the parameter of this callable to be labelled.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`.label_beartypeable_kind` function transitively called by this
    higher-level function.

    Returns
    ----------
    str
        Human-readable label describing this parameter's name.
    '''
    assert isinstance(arg_name, str), f'{repr(arg_name)} not string.'

    # Create and return this label.
    return f'{prefix_beartypeable(func, **kwargs)}parameter "{arg_name}" '


def prefix_beartypeable_return(func: Callable, **kwargs) -> str:
    '''
    Human-readable label describing the return of the passed **decorated
    callable** (i.e., callable wrapped by the :func:`beartype.beartype`
    decorator with a wrapper function type-checking that callable) suffixed by
    delimiting whitespace.

    Parameters
    ----------
    func : Callable
        Decorated callable to be labelled.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`.label_beartypeable_kind` function transitively called by this
    higher-level function.

    Returns
    ----------
    str
        Human-readable label describing this return.
    '''

    # Create and return this label.
    return f'{prefix_beartypeable(func, **kwargs)}return '
