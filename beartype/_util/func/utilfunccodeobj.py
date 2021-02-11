#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype callable code object utilities.**

This private submodule implements utility functions dynamically introspecting
**code objects** (i.e., instances of the :class:`CodeType` type)
underlying all pure-Python callables.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import _BeartypeUtilCallableException
from collections.abc import Callable
from types import CodeType, FunctionType, MethodType

# ....................{ GETTERS                           }....................
def get_func_codeobj(func: Callable) -> CodeType:
    '''
    **Code object** (i.e., instance of the :class:`CodeType` type) underlying
    the passed callable if this callable is pure-Python *or* raise an exception
    otherwise (e.g., if this callable is C-based or a class or object defining
    the ``__call__()`` dunder method).

    Parameters
    ----------
    func : Callable
        Callable to be inspected.

    Returns
    ----------
    CodeType
        Code object underlying this pure-Python callable.

    Raises
    ----------
    _BeartypeUtilCallableException
         If this callable has *no* code object and is thus *not* pure-Python.
    '''

    # Code object underlying this callable if this callable is pure-Python *OR*
    # "None" otherwise.
    func_codeobj = get_func_codeobj_or_none(func)

    # If this callable is *NOT* pure-Python, raise an exception.
    if func_codeobj is None:
        raise _BeartypeUtilCallableException(
            f'Callable {repr(func)} code object not found '
            f'(e.g., due to being either C-based or a class or object '
            f'defining the ``__call__()`` dunder method).'
        )
    # Else, this code object exists.

    # Return this code object.
    return func_codeobj


def get_func_codeobj_or_none(func: Callable) -> 'Optional[CodeType]':
    '''
    **Code object** (i.e., instance of the :class:`CodeType` type) underlying
    the passed callable if this callable is pure-Python *or* ``None`` otherwise
    (e.g., if this callable is C-based or a class or object defining the
    ``__call__()`` dunder method).

    Parameters
    ----------
    func : Callable
        Callable to be inspected.

    Returns
    ----------
    Optional[CodeType]
        Either:

        * If this callable is pure-Python, this callable's code object.
        * Else, ``None``.
    '''
    assert callable(func), f'{repr(func)} not callable.'

    # If this callable is a pure-Python bound method, reduce this callable to
    # the pure-Python unbound function encapsulated by this method.
    #
    # Note that this test intentionally leverages the stdlib
    # "types.MethodType" class rather than our equivalent
    # "beartype.cave.MethodBoundInstanceOrClassType" class to avoid circular
    # import issues.
    if isinstance(func, MethodType):
        func = func.__func__
    # Else, this callable is *NOT* a pure-Python bound method.
    #
    # In either case, this callable is now a pure-Python unbound function.

    # Return either...
    #
    # Note that the equivalent could also technically be written as
    # "getattr(func, '__code__', None)", but that doing so would both be less
    # efficient *AND* render this getter less robust. Why? Because the
    # getattr() builtin internally calls the __getattr__() and
    # __getattribute__() dunder methods, either of which could raise arbitrary
    # exceptions, and is thus considerably less safe.
    #
    # Note that this test intentionally leverages the stdlib
    # "types.FunctionType" class rather than our equivalent
    # "beartype.cave.FunctionType" class to avoid circular import issues.
    return (
        # If this function is pure-Python, this function's code object.
        func.__code__ if isinstance(func, FunctionType) else
        # Else, "None".
        None
    )
