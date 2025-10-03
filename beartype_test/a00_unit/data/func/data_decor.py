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
class DecoratorHostileWrapper(object):
    '''
    **Decorator-hostile wrapper** (i.e., arbitrary uncallable type defining a
    non-standard :meth:`.invoke` method calling the decorated callable or type
    against which this wrapper was instantiated by the parent
    :func:`.decorator_hostile` decorator).

    Attributes
    ----------
    _wrappee : Callable
        **Wrappee** (i.e., callable or type originally decorated by the parent
        :func:`.decorator_hostile` decorator encapsulating that callable or type
        with this wrapper instance).
    '''

    def __init__(self, wrappee: Callable) -> None:
        '''
        Initialize this decorator-hostile wrapper with the passed decorated
        callable or type.
        '''

        # Classify the passed wrappee intelligently, such that...
        self._wrappee = (
            # If this wrappee is actually yet another instance of this same
            # decorator-hostile wrapper class, unwrap this wrapper to the
            # wrappee previously encapsulated by this wrapper.
            wrappee._wrappee
            if isinstance(wrappee, DecoratorHostileWrapper) else
            # Else, this wrappee is presumably a callable or type. In this case,
            # classify this wrappee as is.
            wrappee
        )


    def invoke(self, *args, **kwargs) -> object:
        '''
        Call the decorated callable or type wrapped by this decorator-hostile
        wrapper with all passed positional and keyword parameters.
        '''

        # Defer to the decorated callable or type.
        return self._wrappee(*args, **kwargs)


def decorator_hostile(func: Callable) -> DecoratorHostileWrapper:
    '''
    **Decorator-hostile decorator** (i.e., decorator that prevents other
    decorators from being applied after this decorator is applied to the
    decorated callable or type).

    This decorator returns an arbitrary uncallable object of an arbitrary type
    defining an ``invoke()`` method calling the decorated callable or type.
    This decorator thus "wraps" the decorated callable or type with a
    non-standard calling convention rather than the standard ``__wrapped__``
    dunder attribute defined by the standard :func:`functools.wraps` wrapper
    employed by standard decorators. Doing so prevents other decorators
    (including :func:`beartype.beartype` itself) from unwrapping the decorated
    callable or type from the uncallable object returned by this decorator,
    which then prevents those other decorators from introspecting the decorated
    signature. In short, this decorator is trivially decorator-hostile.

    This decorator intentionally mimics the action of real-world
    decorator-hostile decorators, including:

    * The third-party :func:`langchain_core.runnables.core` decorator function.
    * The third-party :func:`fastmcp.FastMCP.tool` decorator method.
    '''

    # Create and return a decorator-hostile wrapper wrapping this object.
    return DecoratorHostileWrapper(func)


class DecoratorHostileType(object):
    '''
    **Decorator-hostile type** (i.e., arbitrary class defining one or more
    decorator-hostile methods).
    '''

    def __init__(self) -> None:
        '''
        Initialize this decorator-hostile instance.
        '''

        pass


    def decorator_hostile_method(
        self, func: Callable) -> DecoratorHostileWrapper:
        '''
        **Decorator-hostile decorator method** (i.e., decorator implemented as a
        bound instance method preventing other decorators from being applied
        after this decorator is applied to the decorated callable or type).

        See Also
        --------
        :func:`.decorator_hostile`
            Further details.
        '''

        # Create and return a decorator-hostile wrapper wrapping this object.
        return DecoratorHostileWrapper(func)

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

