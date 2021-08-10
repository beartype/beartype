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
from beartype.roar._roarexc import _BeartypeUtilCallableException
from beartype._util.func.utilfunccodeobj import (
    CallableOrFrameOrCodeType,
    get_func_unwrapped_codeobj,
)
from enum import Enum as EnumMemberType
from inspect import (
    CO_VARARGS,
    CO_VARKEYWORDS,
    Parameter,
)
from typing import Any, Generator, Tuple, Type

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ VALIDATORS                        }....................
#FIXME: Uncomment as needed.
# def die_unless_func_argless(
#     # Mandatory parameters.
#     func: CallableOrFrameOrCodeType,
#
#     # Optional parameters.
#     func_label: str = 'Callable',
#     exception_cls: Type[Exception] = _BeartypeUtilCallableException,
# ) -> None:
#     '''
#     Raise an exception unless the passed pure-Python callable is
#     **argument-less** (i.e., accepts *no* arguments).
#
#     Parameters
#     ----------
#     func : CallableOrFrameOrCodeType
#         Pure-Python callable, frame, or code object to be inspected.
#     func_label : str, optional
#         Human-readable label describing this callable in exception messages
#         raised by this validator. Defaults to ``'Callable'``.
#     exception_cls : type, optional
#         Type of exception to be raised if this callable is neither a
#         pure-Python function nor method. Defaults to
#         :class:`_BeartypeUtilCallableException`.
#
#     Raises
#     ----------
#     exception_cls
#         If this callable either:
#
#         * Is *not* callable.
#         * Is callable but is *not* pure-Python.
#         * Is a pure-Python callable accepting one or more parameters.
#     '''
#
#     # If this callable accepts one or more arguments, raise an exception.
#     if is_func_argless(
#         func=func, func_label=func_label, exception_cls=exception_cls):
#         assert isinstance(func_label, str), f'{repr(func_label)} not string.'
#         assert isinstance(exception_cls, type), (
#             f'{repr(exception_cls)} not class.')
#
#         raise exception_cls(
#             f'{func_label} {repr(func)} not argument-less '
#             f'(i.e., accepts one or more arguments).'
#         )


def die_unless_func_args_len_flexible_equal(
    # Mandatory parameters.
    func: CallableOrFrameOrCodeType,
    func_args_len_flexible: int,

    # Optional parameters.
    func_label: str = 'Callable',
    exception_cls: Type[Exception] = _BeartypeUtilCallableException,
) -> None:
    '''
    Raise an exception unless the passed pure-Python callable accepts the
    passed number of **flexible parameters** (i.e., parameters passable as
    either positional or keyword arguments).

    Parameters
    ----------
    func : CallableOrFrameOrCodeType
        Pure-Python callable, frame, or code object to be inspected.
    func_args_len_flexible : int
        Number of flexible parameters to validate this callable as accepting.
    func_label : str, optional
        Human-readable label describing this callable in exception messages
        raised by this validator. Defaults to ``'Callable'``.
    exception_cls : type, optional
        Type of exception to be raised if this callable is neither a
        pure-Python function nor method. Defaults to
        :class:`_BeartypeUtilCallableException`.

    Raises
    ----------
    exception_cls
        If this callable either:

        * Is *not* callable.
        * Is callable but is *not* pure-Python.
        * Is a pure-Python callable accepting either more or less than this
          Number of flexible parameters.
    '''
    assert isinstance(func_args_len_flexible, int)

    # Number of flexible parameters accepted by this callable.
    func_args_len_flexible_actual = get_func_args_len_flexible(
        func=func, func_label=func_label, exception_cls=exception_cls)

    # If this callable accepts more or less than this number of flexible
    # parameters, raise an exception.
    if func_args_len_flexible_actual != func_args_len_flexible:
        assert isinstance(func_label, str), f'{repr(func_label)} not string.'
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not class.')

        raise exception_cls(
            f'{func_label} {repr(func)} flexible argument count '
            f'{func_args_len_flexible_actual} != {func_args_len_flexible}.'
        )

# ....................{ TESTERS ~ kind                    }....................
def is_func_argless(
    # Mandatory parameters.
    func: CallableOrFrameOrCodeType,

    # Optional parameters.
    func_label: str = 'Callable',
    exception_cls: Type[Exception] = _BeartypeUtilCallableException,
) -> bool:
    '''
    ``True`` only if the passed pure-Python callable is **argument-less**
    (i.e., accepts *no* arguments).

    Parameters
    ----------
    func : CallableOrFrameOrCodeType
        Pure-Python callable, frame, or code object to be inspected.
    func_label : str, optional
        Human-readable label describing this callable in exception messages
        raised by this tester. Defaults to ``'Callable'``.
    exception_cls : type, optional
        Type of exception to be raised in the event of fatal error. Defaults to
        :class:`_BeartypeUtilCallableException`.

    Returns
    ----------
    bool
        ``True`` only if the passed callable accepts *no* arguments.

    Raises
    ----------
    exception_cls
         If the passed callable is *not* pure-Python.
    '''

    # Code object underlying the passed pure-Python callable unwrapped.
    func_codeobj = get_func_unwrapped_codeobj(
        func=func, func_label=func_label, exception_cls=exception_cls)

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
def is_func_arg_variadic(func: CallableOrFrameOrCodeType) -> bool:
    '''
    ``True`` only if the passed pure-Python callable accepts any **variadic
    parameters** and thus either variadic positional arguments (e.g.,
    "*args") or variadic keyword arguments (e.g., "**kwargs").

    Parameters
    ----------
    func : Union[Callable, CodeType, FrameType]
        Pure-Python callable, frame, or code object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if the passed callable accepts either:

        * Variadic positional arguments (e.g., "*args").
        * Variadic keyword arguments (e.g., "**kwargs").

    Raises
    ----------
    _BeartypeUtilCallableException
         If the passed callable is *not* pure-Python.
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


def is_func_arg_variadic_positional(func: CallableOrFrameOrCodeType) -> bool:
    '''
    ``True`` only if the passed pure-Python callable accepts variadic
    positional arguments (e.g., "*args").

    Parameters
    ----------
    func : Union[Callable, CodeType, FrameType]
        Pure-Python callable, frame, or code object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if the passed callable accepts variadic positional
        arguments.

    Raises
    ----------
    _BeartypeUtilCallableException
         If the passed callable is *not* pure-Python.
    '''

    # Code object underlying the passed pure-Python callable unwrapped.
    func_codeobj = get_func_unwrapped_codeobj(func)

    # Return true only if this callable declares Variadic positional arguments.
    return func_codeobj.co_flags & CO_VARARGS != 0


def is_func_arg_variadic_keyword(func: CallableOrFrameOrCodeType) -> bool:
    '''
    ``True`` only if the passed pure-Python callable accepts variadic
    keyword arguments (e.g., "**kwargs").

    Parameters
    ----------
    func : Union[Callable, CodeType, FrameType]
        Pure-Python callable, frame, or code object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if the passed callable accepts variadic keyword
        arguments.

    Raises
    ----------
    _BeartypeUtilCallableException
         If the passed callable is *not* pure-Python.
    '''

    # Code object underlying the passed pure-Python callable unwrapped.
    func_codeobj = get_func_unwrapped_codeobj(func)

    # Return true only if this callable declares Variadic positional arguments.
    return func_codeobj.co_flags & CO_VARKEYWORDS != 0

# ....................{ TESTERS ~ name                    }....................
def is_func_arg_name(func: CallableOrFrameOrCodeType, arg_name: str) -> bool:
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
    func : Union[Callable, CodeType, FrameType]
        Pure-Python callable, frame, or code object to be inspected.
    arg_name : str
        Name of the argument to be searched for.

    Returns
    ----------
    bool
        ``True`` only if the passed callable accepts an argument with this
        name.

    Raises
    ----------
    _BeartypeUtilCallableException
         If the passed callable is *not* pure-Python.
    '''
    assert isinstance(arg_name, str), f'{arg_name} not string.'

    # For the name of each parameter accepted by this callable...
    for arg_name_curr, _, _ in iter_func_args(func):
        # If this is the passed name, return true.
        if arg_name_curr == arg_name:
            return True

    # Else, this callable accepts no such parameter. In this case, return
    # false.
    return False

# ....................{ GETTERS                           }....................
def get_func_args_len_flexible(
    # Mandatory parameters.
    func: CallableOrFrameOrCodeType,

    # Optional parameters.
    func_label: str = 'Callable',
    exception_cls: Type[Exception] = _BeartypeUtilCallableException,
) -> int:
    '''
    Number of **flexible parameters** (i.e., parameters passable as either
    positional or keyword arguments) accepted by the passed pure-Python
    callable.

    Parameters
    ----------
    func : CallableOrFrameOrCodeType
        Pure-Python callable, frame, or code object to be inspected.
    func_label : str, optional
        Human-readable label describing this callable in exception messages
        raised by this validator. Defaults to ``'Callable'``.
    exception_cls : type, optional
        Type of exception in the event of a fatal error. Defaults to
        :class:`_BeartypeUtilCallableException`.

    Returns
    ----------
    int
        Number of flexible parameters accepted by this callable.

    Raises
    ----------
    exception_cls
         If the passed callable is *not* pure-Python.
    '''

    # Code object underlying the passed pure-Python callable unwrapped.
    func_codeobj = get_func_unwrapped_codeobj(
        func=func, func_label=func_label, exception_cls=exception_cls)

    # Return the number of flexible parameters accepted by this callable.
    return func_codeobj.co_argcount

# ....................{ GENERATORS                        }....................
#FIXME: Unit test us up, please.
#FIXME: Replace all existing usage of inspect.signature() throughout the
#codebase with usage of this supremely fast generator instead.
def iter_func_args(func: CallableOrFrameOrCodeType) -> Generator[
    Tuple[str, EnumMemberType, Any], None, None]:
    '''
    Generator yielding one 3-tuple ``(arg_name, arg_kind, arg_default)`` for
    each parameter accepted by the passed pure-Python callable.

    Specifically, this function dynamically creates and returns a new one-shot
    generator yielding for each callable parameter one 3-tuple containing:

    #. ``arg_name``, the name of the currently iterated parameter.
    #. ``arg_kind``, the kind of the currently iterated parameter, guaranteed
       to be one of the following enumeration members:

       * :attr:`Parameter.POSITIONAL_OR_KEYWORD` for standard (i.e., positional
         or keyword) parameters.
       * :attr:`Parameter.POSITIONAL_ONLY` for positional-only parameters.
       * :attr:`Parameter.KEYWORD_ONLY` for keyword-only parameters.
       * :attr:`Parameter.VAR_POSITIONAL` for the variadic positional
         parameter.
       * :attr:`Parameter.VAR_KEYWORD` for the variadic keyword parameter.

    #. ``arg_default``, either:

       * If this parameter is mandatory, ``None``.
       * If this parameter is optional, the default value of this parameter.

    Caveats
    ----------
    **This highly optimized generator should always be called in lieu of the
    highly unoptimized** :func:`inspect.signature` **function,** which
    implements a similar introspection as this generator with significantly
    worse space and time consumption.

    Parameters
    ----------
    func : Union[Callable, CodeType, FrameType]
        Pure-Python callable, frame, or code object to be inspected.

    Returns
    ----------
    Generator[Tuple[str, EnumMemberType, Any], None, None]
        Generator yielding one 3-tuple ``(arg_name, arg_kind, arg_default)``
        for each parameter accepted by this callable.

    Raises
    ----------
    _BeartypeUtilCallableException
         If this callable is *not* pure-Python.
    '''

    # Code object underlying the passed pure-Python callable unwrapped.
    func_codeobj = get_func_unwrapped_codeobj(func)

    # Tuple of the names of all variables localized to this callable.
    #
    # Note that this tuple contains the names of both:
    # * All parameters accepted by this callable.
    # * All local variables internally declared in this callable's body.
    # * "func_codeobj.co_names" is incorrectly documented in the "inspect"
    #   module as "tuple of names of local variables." That's a lie, of course.
    #   That attribute is instead a largely useless tuple of the names of both
    #   globals and object attributes accessed in this callable's body. *shrug*
    #
    # Ergo, this tuple *CANNOT* be searched in full. Only the subset of this
    # tuple containing only argument names may be safely searched.
    args_name = func_codeobj.co_varnames

    # Tuple of the default values assigned to all optional standard (i.e.,
    # positional or keyword) parameters accepted by this callable if any *OR*
    # the empty tuple otherwise.
    args_defaults_std = getattr(func_codeobj, '__defaults__', ())

    # Dictionary mapping the name of each optional keyword-only parameter
    # accepted by this callable to the default value assigned to that parameter
    # if any *OR* the empty dictionary otherwise.
    args_defaults_kwonly = getattr(func_codeobj, '__kwdefaults__', {})

    # Number of standard parameters accepted by this callable.
    args_len_std = func_codeobj.co_argcount

    # Number of keyword-only parameters accepted by this callable.
    args_len_kwonly = func_codeobj.co_kwonlyargcount

    # Number of optional standard parameters accepted by this callable.
    args_len_std_optional = len(args_defaults_std)

    # Number of optional keyword-only parameters accepted by this callable.
    args_len_kwonly_optional = len(args_defaults_kwonly)

    # Number of mandatory standard parameters accepted by this callable.
    args_len_std_mandatory = args_len_std - args_len_std_optional

    # Number of mandatory keyword-only parameters accepted by this callable.
    args_len_kwonly_mandatory = args_len_kwonly - args_len_kwonly_optional

    # 0-based index of the first mandatory standard parameter accepted by this
    # callable in the "args_name" tuple.
    args_index_std_mandatory = 0

    # 0-based index of the first optional standard parameter accepted by this
    # callable in the "args_name" tuple.
    args_index_std_optional = args_len_std_mandatory

    # 0-based index of the first mandatory keyword-only parameter accepted by
    # this callable in the "args_name" tuple.
    args_index_kwonly_mandatory = (
        args_index_std_optional + args_len_std_optional)

    # 0-based index of the first optional keyword-only parameter accepted by
    # this callable in the "args_name" tuple.
    args_index_kwonly_optional = (
        args_index_kwonly_mandatory + args_len_kwonly_mandatory)

    # 0-based index of the variadic positional parameter accepted by this
    # callable in the "args_name" tuple if any *OR* a meaningless value
    # otherwise (i.e., if this callable accepts nu such parameter).
    args_index_var_pos = (
        args_index_kwonly_optional + args_len_kwonly_optional)

    # 0-based index of the variadic keyword parameter accepted by this
    # callable in the "args_name" tuple if any *OR* a meaningless value
    # otherwise (i.e., if this callable accepts nu such parameter).
    args_index_var_kw = args_index_var_pos + 1

    # For each mandatory standard parameter accepted by this callable, yield a
    # 3-tuple describing this parameter.
    for arg_std_mandatory in args_name[
        args_index_std_mandatory:args_index_std_optional]:
        yield (arg_std_mandatory, Parameter.POSITIONAL_OR_KEYWORD, None,)

    # For the 0-based index each optional standard parameter accepted by this
    # callable and that parameter, yield a 3-tuple describing this parameter.
    for arg_std_optional_index, arg_std_optional in enumerate(args_name[
        args_index_std_optional:args_index_kwonly_mandatory]):
        assert arg_std_optional_index < args_len_std_optional, (
            f'Optional standard parameter index {arg_std_optional_index} exceeds '
            f'optional standard parameter count {args_len_std_optional}.')

        yield (
            arg_std_optional,
            Parameter.POSITIONAL_OR_KEYWORD,
            args_defaults_std[arg_std_optional_index],
        )

    # For each mandatory keyword-only parameter accepted by this callable,
    # yield a 3-tuple describing this parameter.
    for arg_kwonly_mandatory in args_name[
        args_index_kwonly_mandatory:args_index_kwonly_optional]:
        yield (arg_kwonly_mandatory, Parameter.KEYWORD_ONLY, None,)

    # For the 0-based index each optional keyword-only parameter accepted by
    # this callable and that parameter, yield a 3-tuple describing this
    # parameter.
    for arg_kwonly_optional in args_name[
        args_index_kwonly_optional:args_index_var_pos]:
        yield (
            arg_kwonly_optional,
            Parameter.KEYWORD_ONLY,
            args_defaults_kwonly[arg_kwonly_optional],
        )

    # If this callable accepts a variadic positional parameter, yield a 3-tuple
    # describing this parameter.
    if is_func_arg_variadic_positional(func_codeobj):
        yield (
            args_name[args_index_var_pos],
            Parameter.VAR_POSITIONAL,
            None,
        )

    # If this callable accepts variadic keyword arguments, yield a 3-tuple
    # describing this parameter.
    if is_func_arg_variadic_keyword(func_codeobj):
        yield (
            args_name[args_index_var_kw],
            Parameter.VAR_KEYWORD,
            None,
        )
