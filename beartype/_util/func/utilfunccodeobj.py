#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype callable code object utilities.**

This private submodule implements utility functions dynamically introspecting
**code objects** (i.e., instances of the :class:`types.CodeType` type)
underlying all pure-Python callables.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import _BeartypeUtilCallableException
from types import FunctionType, MethodType

# ....................{ GETTERS                           }....................
def get_func_codeobj(func: 'Callable'):
    '''
    **Code object** (i.e., instance of the :class:`types.CodeType` type)
    underlying the passed pure-Python callable if this callable is pure-Python
    *or* raise an exception otherwise (i.e., if this callable is C-based).

    Parameters
    ----------
    func : Callable
        Callable to be inspected.

    Returns
    ----------
    types.CodeType
        **Code object** (i.e., instance of the :class:`types.CodeType` type)
        underlying this pure-Python callable.

    Raises
    ----------
    _BeartypeUtilCallableException
         If this callable has *no* code object and is thus C-based rather than
         pure-Python.
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

    # If this callable is *NOT* a pure-Python function, this callable is
    # neither a pure-Python method nor function, implying this callable to
    # *NOT* be pure-Python and thus have *NO* code object. In this case, raise
    # an exception.
    #
    # Note that this test intentionally leverages the stdlib
    # "types.FunctionType" class rather than our equivalent
    # "beartype.cave.FunctionType" class to avoid circular import issues.
    if not isinstance(func, FunctionType):
        raise _BeartypeUtilCallableException(
            f'C-based callable {repr(func)} has no code object.')
    # If this callable is a pure-Python function.

    # Return the code object underlying this function.
    return func.__code__
