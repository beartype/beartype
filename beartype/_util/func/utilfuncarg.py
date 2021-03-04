#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype callable parameter utilities.**

This private submodule implements utility functions dynamically introspecting
parameters (arguments) accepted by arbitrary callables.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from collections.abc import Callable
from inspect import CO_VARARGS, CO_VARKEYWORDS

# ....................{ TESTERS                           }....................
def is_func_arg_variadic(func: Callable) -> bool:
    '''
    ``True`` only if the passed pure-Python callable accepts any **variadic
    parameters** and thus either variadic positional arguments (e.g.,
    "*args") or variadic keyword arguments (e.g., "**kwargs").

    Parameters
    ----------
    func : Callable
        Callable to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this callable accepts either:

        * Variadic positional arguments (e.g., "*args").
        * Variadic keyword arguments (e.g., "**kwargs").

    Raises
    ----------
    _BeartypeUtilCallableException
         If this callable has *no* code object and is thus C-based rather than
         pure-Python.
    '''
    assert callable(func), f'{repr(func)} not callable.'

    # Avoid circular import dependencies.
    from beartype._util.func.utilfunccodeobj import get_func_codeobj

    # Code object underlying this pure-Python callable.
    func_codeobj = get_func_codeobj(func)

    # Return true only if this callable declares either...
    #
    # We can't believe it's this simple, either. But it is.
    return (
        # Variadic positional arguments *OR*...
        (func_codeobj.co_flags & CO_VARARGS != 0) or
        # Variadic keyword arguments.
        (func_codeobj.co_flags & CO_VARKEYWORDS != 0)
    )
