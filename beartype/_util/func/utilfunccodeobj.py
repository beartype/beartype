#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype callable code object utilities.**

This private submodule implements utility functions dynamically introspecting
**code objects** (i.e., instances of the :class:`CodeType` type)
underlying all pure-Python callables.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import _BeartypeUtilCallableException
from collections.abc import Callable
from types import CodeType, FunctionType, MethodType
from typing import Optional, Union

# ....................{ HINTS                             }....................
CallableOrCodeType = Union[Callable, CodeType]
'''
PEP-compliant type hint matching either a callable *or* code object.
'''

# ....................{ GETTERS                           }....................
def get_func_codeobj(
    # Mandatory parameters.
    func: CallableOrCodeType,

    # Optional parameters.
    exception_cls: type = _BeartypeUtilCallableException
) -> CodeType:
    '''
    **Code object** (i.e., instance of the :class:`CodeType` type) underlying
    the passed callable if this callable is pure-Python *or* raise an exception
    otherwise (e.g., if this callable is C-based or a class or object defining
    the ``__call__()`` dunder method).

    For convenience, this getter also accepts a code object, in which case that
    code object is simply returned as is.

    Code objects have a docstring under CPython resembling:

    .. _code-block:: python

       Code objects provide these attributes:
           co_argcount         number of arguments (not including *, ** args
                               or keyword only arguments)
           co_code             string of raw compiled bytecode
           co_cellvars         tuple of names of cell variables
           co_consts           tuple of constants used in the bytecode
           co_filename         name of file in which this code object was
                               created
           co_firstlineno      number of first line in Python source code
           co_flags            bitmap: 1=optimized | 2=newlocals | 4=*arg |
                               8=**arg | 16=nested | 32=generator | 64=nofree |
                               128=coroutine | 256=iterable_coroutine |
                               512=async_generator
           co_freevars         tuple of names of free variables
           co_posonlyargcount  number of positional only arguments
           co_kwonlyargcount   number of keyword only arguments (not including
                               ** arg)
           co_lnotab           encoded mapping of line numbers to bytecode
                               indices
           co_name             name with which this code object was defined
           co_names            tuple of names of local variables
           co_nlocals          number of local variables
           co_stacksize        virtual machine stack space required
           co_varnames         tuple of names of arguments and local variables

    Parameters
    ----------
    func : Union[Callable, CodeType]
        Callable or code object to be inspected.
    exception_cls : type
        Type of exception to be raised if this callable is neither a
        pure-Python function nor method. Defaults to
        :class:`_BeartypeUtilCallableException`.

    Returns
    ----------
    CodeType
        Code object underlying this callable.

    Raises
    ----------
    _BeartypeUtilCallableException
         If this callable has *no* code object and is thus *not* pure-Python.
    '''

    # If the passed object is already a code object, return this object as is.
    if isinstance(func, CodeType):
        return func
    # Else, this object is *NOT* already a code object.

    # Code object underlying this callable if this callable is pure-Python *OR*
    # "None" otherwise.
    func_codeobj = get_func_codeobj_or_none(func)

    # If this callable is *NOT* pure-Python, raise an exception.
    if func_codeobj is None:
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not class.')
        raise exception_cls(
            f'Callable {repr(func)} code object not found '
            f'(e.g., due to being either C-based or a class or object '
            f'defining the ``__call__()`` dunder method).'
        )
    # Else, this code object exists.

    # Return this code object.
    return func_codeobj


def get_func_codeobj_or_none(func: Callable) -> Optional[CodeType]:
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
