#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable code object** utilities.

This private submodule implements utility functions dynamically introspecting
**code objects** (i.e., instances of the :class:`CodeType` type)
underlying all pure-Python callables.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar._roarexc import _BeartypeUtilCallableException
from beartype._util.func.utilfuncwrap import unwrap_func
from collections.abc import Callable
from types import CodeType, FrameType, FunctionType, MethodType
from typing import Optional, Type, Union

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ HINTS                             }....................
CallableOrFrameOrCodeType = Union[Callable, CodeType, FrameType]
'''
PEP-compliant type hint matching either a callable *or* code object.
'''

# ....................{ GETTERS ~ unwrap                  }....................
def get_func_unwrapped_codeobj(
    # Mandatory parameters.
    func: CallableOrFrameOrCodeType,

    # Optional parameters.
    func_label: str = 'Callable',
    exception_cls: Type[Exception] = _BeartypeUtilCallableException,
) -> CodeType:
    '''
    **Code object** (i.e., instance of the :class:`CodeType` type) underlying
    the **wrappee** (i.e., callable proxied by the passed callable by either
    the :func:`functools.wrap` decorator or :func:`functools.update_wrapper`
    function) wrapped by the passed callable if the latter is a pure-Python
    wrapper or underlying the passed callable if the latter is pure-Python but
    not a wrapper *or* raise an exception otherwise (e.g., if that callable is
    C-based or a class or object defining the ``__call__()`` dunder method).

    Specifically, if the passed object is a:

    * Pure-Python wrapper wrapping a pure-Python wrappee, this getter returns
      the code object of that wrappee.
    * Pure-Python non-wrapper callable, this getter returns the code object of
      that callable.
    * Pure-Python call stack frame, this getter returns the code object of the
      pure-Python callable encapsulated by that frame.
    * Code object, this getter returns that code object.
    * Any other object, this getter raises an exception.

    Parameters
    ----------
    func : Union[Callable, CodeType, FrameType]
        Callable or frame or code object to be inspected.
    func_label : str, optional
        Human-readable label describing this callable in exception messages
        raised by this validator. Defaults to ``'Callable'``.
    exception_cls : type, optional
        Type of exception in the event of a fatal error. Defaults to
        :class:`_BeartypeUtilCallableException`.

    Returns
    ----------
    CodeType
        Code object underlying the passed callable unwrapped.

    Raises
    ----------
    exception_cls
         If passed callable unwrapped has *no* code object and is thus *not*
         pure-Python.

    See Also
    ----------
    :func:`get_func_codeobj`
        Further details.
    '''

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize changes with get_func_codeobj().
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Code object underlying this unwrapped callable if this unwrapped callable
    # is pure-Python *OR* "None" otherwise.
    func_codeobj = get_func_unwrapped_codeobj_or_none(func)

    # If this unwrapped callable is *NOT* pure-Python...
    if func_codeobj is None:
        # Avoid circular import dependencies.
        from beartype._util.func.utilfunctest import die_unless_func_python

        # Raise an exception.
        die_unless_func_python(
            func=func, func_label=func_label, exception_cls=exception_cls)
    # Else, this unwrapped callable is pure-Python and this code object exists.

    # Return this code object.
    return func_codeobj  # type: ignore[return-value]


def get_func_unwrapped_codeobj_or_none(
    func: CallableOrFrameOrCodeType) -> Optional[CodeType]:
    '''
    **Code object** (i.e., instance of the :class:`CodeType` type) underlying
    the **wrappee** (i.e., callable proxied by the passed callable by either
    the :func:`functools.wrap` decorator or :func:`functools.update_wrapper`
    function) wrapped by the passed callable if the latter is a pure-Python
    wrapper or underlying the passed callable if the latter is pure-Python but
    not a wrapper *or* ``None`` otherwise (e.g., if that callable is C-based or
    a class or object defining the ``__call__()`` dunder method).

    Parameters
    ----------
    func : CallableOrFrameOrCodeType
        Callable or frame or code object to be inspected.

    Returns
    ----------
    Optional[CodeType]
        Either:

        * If passed callable unwrapped is pure-Python, that callable's code
          object.
        * Else, ``None``.

    See Also
    ----------
    :func:`get_func_unwrapped_codeobj`
        Further details.
    '''

    # Return the code object underlying lowest-level wrappee callable wrapped
    # by the passed  wrapper callable if that wrappee is pure-Python *OR*
    # "None" otherwise.
    return get_func_codeobj_or_none(unwrap_func(func))

# ....................{ GETTERS                           }....................
def get_func_codeobj(
    # Mandatory parameters.
    func: CallableOrFrameOrCodeType,

    # Optional parameters.
    exception_cls: Type[Exception] = _BeartypeUtilCallableException,
) -> CodeType:
    '''
    **Code object** (i.e., instance of the :class:`CodeType` type) underlying
    the passed callable if that callable is pure-Python *or* raise an exception
    otherwise (e.g., if that callable is C-based or a class or object defining
    the ``__call__()`` dunder method).

    For convenience, this getter also accepts a code object, in which case that
    code object is simply returned as is.

    Code objects have a docstring under CPython resembling:

    .. code-block:: python

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

    Caveats
    ----------
    **The higher-level** :func:`get_func_unwrapped_codeobj` **getter should
    typically be called in lieu of this lower-level getter.** Given a
    **wrappee** (e.g., callable proxied by another callable by either the
    :func:`functools.wrap` decorator or :func:`functools.update_wrapper`
    function):

    * The :func:`get_func_unwrapped_codeobj` getter correctly returns the
      underlying code object of the proxied wrappee.
    * This getter incorrectly returns the code object of the proxying wrapper.

    Parameters
    ----------
    func : Union[Callable, CodeType, FrameType]
        Callable or frame or code object to be inspected.
    exception_cls : type, optional
        Type of exception in the event of a fatal error. Defaults to
        :class:`_BeartypeUtilCallableException`.

    Returns
    ----------
    CodeType
        Code object underlying this callable.

    Raises
    ----------
    exception_cls
         If this callable has *no* code object and is thus *not* pure-Python.

    See Also
    ----------
    :func:`get_func_unwrapped_codeobj`
        Higher-level and thus safer alternative.
    '''

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize changes with get_func_unwrapped_codeobj().
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Code object underlying this callable if this callable is pure-Python *OR*
    # "None" otherwise.
    func_codeobj = get_func_codeobj_or_none(func)

    # If this callable is *NOT* pure-Python...
    if func_codeobj is None:
        # Avoid circular import dependencies.
        from beartype._util.func.utilfunctest import die_unless_func_python

        # Raise an exception.
        die_unless_func_python(func=func, exception_cls=exception_cls)
    # Else, this callable is pure-Python and this code object exists.

    # Return this code object.
    return func_codeobj  # type: ignore[return-value]


def get_func_codeobj_or_none(
    func: CallableOrFrameOrCodeType) -> Optional[CodeType]:
    '''
    **Code object** (i.e., instance of the :class:`CodeType` type) underlying
    the passed callable if this callable is pure-Python *or* ``None`` otherwise
    (e.g., if this callable is C-based or a class or object defining the
    ``__call__()`` dunder method).

    Caveats
    ----------
    **The higher-level** :func:`get_func_unwrapped_codeobj_or_none` **getter
    should typically be called in lieu of this lower-level getter.**

    Parameters
    ----------
    func : CallableOrFrameOrCodeType
        Callable or frame or code object to be inspected.

    Returns
    ----------
    Optional[CodeType]
        Either:

        * If the passed callable is pure-Python, that callable's code object.
        * Else, ``None``.

    See Also
    ----------
    :func:`get_func_codeobj`
        Further details.
    :func:`get_func_unwrapped_codeobj_or_none`
        Higher-level and thus safer alternative.
    '''

    # If the passed object is already a code object, return this object as is.
    if isinstance(func, CodeType):
        return func
    # Else, this object is *NOT* already a code object.
    #
    # If this object is a call stack frame, return this frame's code object.
    elif isinstance(func, FrameType):
        return func.f_code
    # Else, this object is *NOT* a call stack frame and is thus a callable.
    #
    # If this callable is a pure-Python bound method, reduce this callable to
    # the pure-Python unbound function encapsulated by this method.
    #
    # Note this test intentionally tests the "types.MethodType" class rather
    # than our equivalent "beartype.cave.MethodBoundInstanceOrClassType" class
    # to avoid circular import issues.
    elif isinstance(func, MethodType):
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
