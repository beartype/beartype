#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable parameter** utilities.

This private submodule implements utility functions dynamically introspecting
parameters (arguments) accepted by arbitrary callables.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.func.utilfunccodeobj import get_func_codeobj
from collections.abc import Callable
from inspect import CO_VARARGS, CO_VARKEYWORDS
from types import CodeType
from typing import Union

# ....................{ HINTS                             }....................
CallableOrCodeType = Union[Callable, CodeType]
'''
PEP-compliant type hint matching either a callable *or* code object.
'''

# ....................{ TESTERS ~ kind                    }....................
def is_func_argless(func: CallableOrCodeType) -> bool:
    '''
    ``True`` only if the passed pure-Python callable is **argument-less**
    (i.e., accepts *no* arguments.)

    Parameters
    ----------
    func : Union[Callable, CodeType]
        Callable or code object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this callable accepts *no* arguments.

    Raises
    ----------
    _BeartypeUtilCallableException
         If this callable is *not* pure-Python.
    '''

    # Code object underlying this pure-Python callable.
    func_codeobj = get_func_codeobj(func)

    # Return true only if this callable accepts neither...
    return not (
        # One or more non-variadic arguments that are either standard or
        # keyword-only *NOR*...
        #
        # Note that both of the argument counts tested here ignore the
        # existence of variadic arguments, which is mildly frustrating... but
        # that's the backward-compatible hodgepodge that is the modern code
        # object for you.
        (func_codeobj.co_argcount + func_codeobj.co_kwonlyargcount > 0) or
        # One or more variadic arguments.
        is_func_arg_variadic(func_codeobj)
    )

# ....................{ TESTERS ~ kind : variadic         }....................
def is_func_arg_variadic(func: CallableOrCodeType) -> bool:
    '''
    ``True`` only if the passed pure-Python callable accepts any **variadic
    parameters** and thus either variadic positional arguments (e.g.,
    "*args") or variadic keyword arguments (e.g., "**kwargs").

    Parameters
    ----------
    func : Union[Callable, CodeType]
        Callable or code object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this callable accepts either:

        * Variadic positional arguments (e.g., "*args").
        * Variadic keyword arguments (e.g., "**kwargs").

    Raises
    ----------
    _BeartypeUtilCallableException
         If this callable is *not* pure-Python.
    '''

    # Return true only if this callable declares either...
    #
    # We can't believe it's this simple, either. But it is.
    return (
        # Variadic positional arguments *OR*...
        is_func_arg_variadic_positional(func) or
        # Variadic keyword arguments.
        is_func_arg_variadic_keyword(func)
    )


def is_func_arg_variadic_positional(func: CallableOrCodeType) -> bool:
    '''
    ``True`` only if the passed pure-Python callable accepts variadic
    positional arguments (e.g., "*args").

    Parameters
    ----------
    func : Union[Callable, CodeType]
        Callable or code object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this callable accepts variadic positional arguments.

    Raises
    ----------
    _BeartypeUtilCallableException
         If this callable is *not* pure-Python.
    '''

    # Code object underlying this pure-Python callable.
    func_codeobj = get_func_codeobj(func)

    # Return true only if this callable declares Variadic positional arguments.
    return func_codeobj.co_flags & CO_VARARGS != 0


def is_func_arg_variadic_keyword(func: CallableOrCodeType) -> bool:
    '''
    ``True`` only if the passed pure-Python callable accepts variadic
    keyword arguments (e.g., "**kwargs").

    Parameters
    ----------
    func : Union[Callable, CodeType]
        Callable or code object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this callable accepts variadic keyword arguments.

    Raises
    ----------
    _BeartypeUtilCallableException
         If this callable is *not* pure-Python.
    '''

    # Code object underlying this pure-Python callable.
    func_codeobj = get_func_codeobj(func)

    # Return true only if this callable declares Variadic positional arguments.
    return func_codeobj.co_flags & CO_VARKEYWORDS != 0

# ....................{ TESTERS ~ name                    }....................
def is_func_arg_name(func: CallableOrCodeType, arg_name: str) -> bool:
    '''
    ``True`` only if the passed pure-Python callable accepts an argument with
    the passed name.

    Caveats
    ----------
    **This tester is** ``O(n)`` **for** ``n`` **the total number of arguments
    accepted by this callable,** due to unavoidably performing a linear search
    for an argument with this name is this callable's argument list. This
    tester should thus be called sparingly and certainly *not* repeatedly for
    the same callable.

    Parameters
    ----------
    func : Union[Callable, CodeType]
        Callable or code object to be inspected.
    arg_name : str
        Name of the argument to be searched for.

    Returns
    ----------
    bool
        ``True`` only if this callable accepts an argument with this name.

    Raises
    ----------
    _BeartypeUtilCallableException
         If this callable is *not* pure-Python.
    '''
    assert isinstance(arg_name, str), f'{arg_name} not string.'

    # Code object underlying this pure-Python callable.
    func_codeobj = get_func_codeobj(func)

    #FIXME: Consider generalizing this useful logic into either a new
    #get_func_args_len() *OR* get_func_args_name() getter function as needed.

    # Number of arguments accepted by this callable.
    func_args_len = func_codeobj.co_argcount + func_codeobj.co_kwonlyargcount

    # If this callable accepts variadic positional arguments, increment the
    # number of arguments.
    if is_func_arg_variadic_positional(func):
        func_args_len += 1

    # If this callable accepts variadic keyword arguments, increment the
    # number of arguments.
    if is_func_arg_variadic_keyword(func):
        func_args_len += 1

    # Return true only if this callable accepts an argument with this name.
    #
    # Note that the "co_varnames" tuple contains the names of both:
    # * All arguments accepted by this callable.
    # * All local variables internally declared in this callable's body.
    # * The "func_codeobj.co_names" is incorrectly documented in the "inspect"
    #   module as "tuple of names of local variables." That's a lie, of course.
    #   That attribute is instead a largely useless tuple of the names of
    #   globals and object attributes accessed in this callable's body. *shrug*
    #
    # Ergo, this tuple *CANNOT* be searched in full. Only the subset of this
    # tuple containing only argument names may be safely searched.
    return arg_name in func_codeobj.co_varnames[:func_args_len]
