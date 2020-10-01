#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype text label utilities** (i.e., callables generating human-readable
strings describing prominent objects or types, which are then typically
interpolated into exception messages).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.text.utiltextrepr import get_object_representation

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ LABELLERS                         }....................
def label_callable_decorated(func: 'CallableTypes') -> None:
    '''
    Human-readable label describing the passed **decorated callable** (i.e.,
    callable wrapped by the :func:`beartype.beartype` decorator with a wrapper
    function type-checking that callable).

    Parameters
    ----------
    func : CallableTypes
        Decorated callable to be labelled.

    Returns
    ----------
    str
        Human-readable label describing this decorated callable.
    '''
    assert callable(func), '{!r} uncallable.'.format(func)

    #FIXME: Refactor to leverage f-strings after dropping Python 3.5 support,
    #which are the optimal means of performing string formatting.

    # Create and return this label.
    return '@beartyped ' + func.__name__ + '()'


def label_callable_decorated_pith(
    func: 'CallableTypes', pith_name: str) -> None:
    '''
    Human-readable label describing either the parameter with the passed name
    *or* return value if this name is ``return`` of the passed **decorated
    callable** (i.e., callable wrapped by the :func:`beartype.beartype`
    decorator with a wrapper function type-checking that callable).

    Parameters
    ----------
    func : CallableTypes
        Decorated callable to be labelled.
    pith_name : str
        Name of the parameter or return value of this callable to be labelled.

    Returns
    ----------
    str
        Human-readable label describing either the name of this parameter *or*
        this return value.
    '''
    assert isinstance(pith_name, str), '{!r} not string.'.format(pith_name)

    # Return a human-readable label describing either...
    return (
        # If this name is "return", the return value of this callable.
        label_callable_decorated_return(func)
        if pith_name == 'return' else
        # Else, the parameter with this name of this callable.
        label_callable_decorated_param(func=func, param_name=pith_name)
    )

# ....................{ LABELLERS ~ param                 }....................
def label_callable_decorated_param(
    func: 'CallableTypes', param_name: str) -> None:
    '''
    Human-readable label describing the parameter with the passed name of the
    passed **decorated callable** (i.e., callable wrapped by the
    :func:`beartype.beartype` decorator with a wrapper function type-checking
    that callable).

    Parameters
    ----------
    func : CallableTypes
        Decorated callable to be labelled.
    param_name : str
        Name of the parameter of this callable to be labelled.

    Returns
    ----------
    str
        Human-readable label describing this parameter's name.
    '''
    assert isinstance(param_name, str), '{!r} not string.'.format(param_name)

    #FIXME: Refactor to leverage f-strings after dropping Python 3.5 support,
    #which are the optimal means of performing string formatting.

    # Create and return this label.
    return '{} parameter "{}"'.format(
        label_callable_decorated(func), param_name)


def label_callable_decorated_param_value(
    func: 'CallableTypes', param_name: str, param_value: object) -> None:
    '''
    Human-readable label describing the parameter with the passed name and
    trimmed value of the passed **decorated callable** (i.e., callable wrapped
    by the :func:`beartype.beartype` decorator with a wrapper function
    type-checking that callable).

    Parameters
    ----------
    func : CallableTypes
        Decorated callable to be labelled.
    param_name : str
        Name of the parameter of this callable to be labelled.
    param_value : object
        Value of the parameter of this callable to be labelled.

    Returns
    ----------
    str
        Human-readable label describing this parameter's name and value.
    '''
    assert isinstance(param_name, str), '{!r} not string.'.format(param_name)

    #FIXME: Refactor to leverage f-strings after dropping Python 3.5 support,
    #which are the optimal means of performing string formatting.

    # Create and return this label.
    return '{} parameter {}={}'.format(
        label_callable_decorated(func),
        param_name,
        get_object_representation(param_value),
    )

# ....................{ LABELLERS ~ return                }....................
def label_callable_decorated_return(func: 'CallableTypes') -> None:
    '''
    Human-readable label describing the return of the passed **decorated
    callable** (i.e., callable wrapped by the :func:`beartype.beartype`
    decorator with a wrapper function type-checking that callable).

    Parameters
    ----------
    func : CallableTypes
        Decorated callable to be labelled.

    Returns
    ----------
    str
        Human-readable label describing this return.
    '''

    # Create and return this label.
    return label_callable_decorated(func) + ' return value'


def label_callable_decorated_return_value(
    func: 'CallableTypes', return_value: object) -> None:
    '''
    Human-readable label describing the passed trimmed return value of the
    passed **decorated callable** (i.e., callable wrapped by the
    :func:`beartype.beartype` decorator with a wrapper function type-checking
    that callable).

    Parameters
    ----------
    func : CallableTypes
        Decorated callable to be labelled.
    return_value : object
        Value returned by this callable to be labelled.

    Returns
    ----------
    str
        Human-readable label describing this return value.
    '''

    #FIXME: Refactor to leverage f-strings after dropping Python 3.5 support,
    #which are the optimal means of performing string formatting.

    # Create and return this label.
    return '{} {}'.format(
        label_callable_decorated_return(func),
        get_object_representation(return_value))
