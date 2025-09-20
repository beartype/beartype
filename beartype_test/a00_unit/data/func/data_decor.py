#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **sample callable** submodule.

This submodule predefines sample pure-Python callables exercising known edge
cases on behalf of higher-level unit test submodules.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Callable
from functools import wraps

# ....................{ DECORATORS                         }....................
def decorator(func: Callable) -> Callable:
    '''
    **Identity decorator** (i.e., decorator returning the passed callable
    unmodified).

    This decorator enables logic elsewhere to exercise the
    :mod:`beartype.beartype` decorator with respect to nested callables
    decorated by both the :mod:`beartype.beartype` decorator and one or more
    decorators *not* the :mod:`beartype.beartype` decorator.
    '''

    return func

# ....................{ DECORATORS ~ hostile               }....................
def decorator_hostile(func: Callable) -> Callable:
    '''
    **Decorator-hostile decorator** (i.e., decorator that prevents other
    decorators from being applied after this decorator is applied to the
    decorated callable or type).

    This function returns an isomorphic decorator closure transparently
    preserving both the positions and types of all parameters passed to the
    passed callable. Since that's standard decorator practice, this function
    *would* be decorator-friendly -- except that this function then
    erroneously defines the ``__wraps__`` dunder attribute on this closure to be
    an invalid scalar value rather than the passed callable. Doing so prevents
    other decorators (e.g., :func:`beartype.beartype` itself) from unwrapping
    the passed callable from the passed callable, which then prevents those
    other decorators from introspecting the signature of the passed callable. In
    short, this function is trivially decorator-hostile.
    '''

    def _closure_isomorphic(*args, **kwargs):
        '''
        **Isomorphic decorator closure** (i.e., closure transparently
        preserving both the positions and types of all parameters and returns
        passed to the decorated callable).
        '''

        return func(*args, **kwargs)

    # Monkey-patch the "__wraps__" dunder attribute on this closure to be an
    # invalid scalar value (rather than the passed callable), degrading this
    # otherwise decorator-friendly decorator to be decorator-hostile.
    _closure_isomorphic.__wraps__ = (
        "Even now, while Saturn, rous'd from icy trance,")

    # Return this closure.
    return _closure_isomorphic

# ....................{ DECORATORS ~ (non)isomorphic       }....................
def decorator_isomorphic(func: Callable) -> Callable:
    '''
    **Isomorphic decorator** (i.e., function returning an isomorphic decorator
    closure transparently preserving both the positions and types of all
    parameters passed to the passed callable).
    '''

    @wraps(func)
    def _closure_isomorphic(*args, **kwargs):
        '''
        **Isomorphic decorator closure** (i.e., closure transparently
        preserving both the positions and types of all parameters and returns
        passed to the decorated callable).
        '''

        return func(*args, **kwargs)

    # Return this closure.
    return _closure_isomorphic


def decorator_nonisomorphic(func):
    '''
    **Non-isomorphic decorator** (i.e., function returning a non-isomorphic
    decorator closure destroying the positions and/or types of one or more
    parameters passed to the passed callable).
    '''

    @wraps(func)
    def _closure_nonisomorphic():
        '''
        **Non-isomorphic decorator closure** (i.e., closure destroying the
        positions and/or types of one or more parameters passed to the decorated
        callable).
        '''

        return func()

    # Return this closure.
    return _closure_nonisomorphic

