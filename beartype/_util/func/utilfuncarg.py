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
from beartype._util.func.utilfunccodeobj import get_func_unwrapped_codeobj
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
from beartype._util.utiltyping import (
    CallableCodeObjable,
    TypeException,
)
from enum import Enum as EnumMemberType
from inspect import (
    CO_VARARGS,
    CO_VARKEYWORDS,
    Parameter,
)
from typing import Any, Dict, Iterable, Tuple

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ PRIVATE                           }....................
_ARGS_DEFAULTS_KWONLY_EMPTY: Dict[str, object] = {}
'''
Empty dictionary suitable for use as the default dictionary mapping the name of
each optional keyword-only parameter accepted by a callable to the default
value assigned to that parameter.
'''

# ....................{ VALIDATORS                        }....................
#FIXME: Uncomment as needed.
# def die_unless_func_argless(
#     # Mandatory parameters.
#     func: CallableCodeObjable,
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
#     func : CallableCodeObjable
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
    func: CallableCodeObjable,
    func_args_len_flexible: int,

    # Optional parameters.
    func_label: str = 'Callable',
    exception_cls: TypeException = _BeartypeUtilCallableException,
) -> None:
    '''
    Raise an exception unless the passed pure-Python callable accepts the
    passed number of **flexible parameters** (i.e., parameters passable as
    either positional or keyword arguments).

    Parameters
    ----------
    func : CallableCodeObjable
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
    func: CallableCodeObjable,

    # Optional parameters.
    func_label: str = 'Callable',
    exception_cls: TypeException = _BeartypeUtilCallableException,
) -> bool:
    '''
    ``True`` only if the passed pure-Python callable is **argument-less**
    (i.e., accepts *no* arguments).

    Parameters
    ----------
    func : CallableCodeObjable
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
def is_func_arg_variadic(func: CallableCodeObjable) -> bool:
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


def is_func_arg_variadic_positional(func: CallableCodeObjable) -> bool:
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


def is_func_arg_variadic_keyword(func: CallableCodeObjable) -> bool:
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
def is_func_arg_name(func: CallableCodeObjable, arg_name: str) -> bool:
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
        ``True`` only if that callable accepts an argument with this name.

    Raises
    ----------
    _BeartypeUtilCallableException
         If the passed callable is *not* pure-Python.
    '''
    assert isinstance(arg_name, str), f'{arg_name} not string.'

    # Return true only if...
    return any(
        # This is the passed name...
        arg_name_curr == arg_name
        # For the name of any parameter accepted by this callable.
        for arg_name_curr, _, _ in iter_func_args(func)
    )

# ....................{ GETTERS                           }....................
def get_func_args_len_flexible(
    # Mandatory parameters.
    func: CallableCodeObjable,

    # Optional parameters.
    func_label: str = 'Callable',
    exception_cls: TypeException = _BeartypeUtilCallableException,
) -> int:
    '''
    Number of **flexible parameters** (i.e., parameters passable as either
    positional or keyword arguments) accepted by the passed pure-Python
    callable.

    Parameters
    ----------
    func : CallableCodeObjable
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
def iter_func_args(func: CallableCodeObjable) -> Iterable[
    Tuple[str, EnumMemberType, Any]]:
    '''
    Generator yielding one 3-tuple ``(arg_name, arg_kind, arg_default)`` for
    each parameter accepted by the passed pure-Python callable.

    Specifically, this function dynamically creates and returns a new one-shot
    generator yielding for each callable parameter one 3-tuple containing:

    #. ``arg_name``, the name of the currently iterated parameter.
    #. ``arg_kind``, the kind of the currently iterated parameter, guaranteed
       to be one of the following enumeration members:

       * :attr:`Parameter.POSITIONAL_ONLY` for positional-only parameters.
       * :attr:`Parameter.POSITIONAL_OR_KEYWORD` for **flexible parameters**
         (i.e., parameters that may be passed as either positional or keyword
         arguments).
       * :attr:`Parameter.VAR_POSITIONAL` for the variadic positional
         parameter.
       * :attr:`Parameter.KEYWORD_ONLY` for keyword-only parameters.
       * :attr:`Parameter.VAR_KEYWORD` for the variadic keyword parameter.

    #. ``arg_default``, either:

       * If this parameter is mandatory, ``None``.
       * If this parameter is optional, the default value of this parameter.

    For consistency with the official grammar for callable signatures
    standardized by :pep:`570`, this generator is guaranteed to yield 3-tuples
    whose ``arg_kind`` and ``arg_default`` items are ordered as follows:

    * **Mandatory positional-only parameters** (i.e., 3-tuples satisfying
      ``(arg_name, Parameter.POSITIONAL_ONLY, None)``).
    * **Optional positional-only parameters** (i.e., 3-tuples satisfying
      ``(arg_name, Parameter.POSITIONAL_ONLY, arg_default)``).
    * **Mandatory flexible parameters** (i.e., 3-tuples satisfying
      ``(arg_name, Parameter.POSITIONAL_OR_KEYWORD, None)``).
    * **Optional flexible parameters** (i.e., 3-tuples satisfying
      ``(arg_name, Parameter.POSITIONAL_OR_KEYWORD, arg_default)``).
    * **Variadic positional parameters** (i.e., 3-tuples satisfying
      ``(arg_name, Parameter.VAR_POSITIONAL, None)``).
    * **Mandatory keyword-only parameters** (i.e., 3-tuples satisfying
      ``(arg_name, Parameter.KEYWORD_ONLY, None)``).
    * **Optional keyword-only parameters** (i.e., 3-tuples satisfying
      ``(arg_name, Parameter.KEYWORD_ONLY, arg_default)``).
    * **Variadic keyword parameters** (i.e., 3-tuples satisfying
      ``(arg_name, Parameter.VAR_KEYWORD, None)``).

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

    # Tuple of the names of all variables localized to that callable.
    #
    # Note that this tuple contains the names of both:
    # * All parameters accepted by that callable.
    # * All local variables internally declared in that callable's body.
    #
    # Ergo, this tuple *CANNOT* be searched in full. Only the subset of this
    # tuple containing argument names is relevant and may be safely searched.
    #
    # Lastly, note the "func_codeobj.co_names" attribute is incorrectly
    # documented in the "inspect" module as the "tuple of names of local
    # variables." That's a lie. That attribute is instead a mostly useless
    # tuple of the names of both globals and object attributes accessed in the
    # body of that callable. *shrug*
    args_name = func_codeobj.co_varnames

    # Tuple of the default values assigned to all optional non-keyword-only
    # parameters (i.e., all optional positional-only *AND* optional flexible
    # (i.e., positional or keyword) parameters) accepted by that callable if
    # any *OR* the empty tuple otherwise.
    args_defaults_posonly_or_flex = getattr(func_codeobj, '__defaults__', ())

    # Dictionary mapping the name of each optional keyword-only parameter
    # accepted by that callable to the default value assigned to that parameter
    # if any *OR* the empty dictionary otherwise.
    #
    # For both space and time efficiency, the empty dictionary is intentionally
    # *NOT* accessed here as "{}". Whereas each instantiation of the empty
    # tuple efficiently reduces to the same empty tuple, each instantiation of
    # the empty dictionary inefficiently creates a new empty dictionary: e.g.,
    #     >>> () is ()
    #     True
    #     >>> {} is {}
    #     False
    args_defaults_kwonly = getattr(
        func_codeobj, '__kwdefaults__', _ARGS_DEFAULTS_KWONLY_EMPTY)

    # Number of both optional and mandatory positional-only parameters accepted
    # by that callable, specified as either...
    args_len_posonly = (
        # If the active Python interpreter targets Python >= 3.8 and thus
        # supports PEP 570 standardizing positional-only parameters, the number
        # of these parameters;
        func_codeobj.co_posonlyargcount  # type: ignore[attr-defined]
        if IS_PYTHON_AT_LEAST_3_8 else
        # Else, this interpreter targets Python < 3.8 and thus fails to
        # support PEP 570. In this case, there are *NO* such parameters.
        0
    )

    # Number of both optional and mandatory flexible parameters accepted by
    # that callable.
    args_len_flex = func_codeobj.co_argcount

    # Number of both optional and mandatory keyword-only parameters accepted by
    # that callable.
    args_len_kwonly = func_codeobj.co_kwonlyargcount

    # Number of optional non-keyword-only parameters accepted by that callable.
    args_len_posonly_or_flex_optional = len(args_defaults_posonly_or_flex)

    # Number of optional flexible parameters accepted by that callable, defined
    # as the number of optional non-keyword-only parameters capped to the total
    # number of flexible parameters. Why? Because optional flexible parameters
    # preferentially consume non-keyword-only default values first; optional
    # positional-only parameters consume all remaining non-keyword-only default
    # values. Why? Because:
    # * Default values are *ALWAYS* assigned to positional parameters from
    #   right-to-left.
    # * Flexible parameters reside to the right of positional-only parameters.
    #
    # Specifically, this number is defined as...
    args_len_flex_optional = (
        # If the number of optional non-keyword-only parameters exceeds the
        # total number of flexible parameters, the total number of flexible
        # parameters. For obvious reasons, the number of optional flexible
        # parameters *CANNOT* exceed the total number of flexible parameters;
        args_len_flex
        if args_len_posonly_or_flex_optional >= args_len_flex else
        # Else, the total number of flexible parameters is strictly greater
        # than the number of optional non-keyword-only parameters, implying
        # optional flexible parameters consume all non-keyword-only default
        # values. In this case, the number of optional flexible parameters is
        # the number of optional non-keyword-only parameters.
        args_len_posonly_or_flex_optional
    )

    # Number of optional positional-only parameters accepted by that callable,
    # defined as all remaining optional non-keyword-only parameters *NOT*
    # already consumed by positional parameters. Note that this number is
    # guaranteed to be non-negative. Why? Because, it is the case that either:
    # * "args_len_posonly_or_flex_optional >= args_len_flex", in which case
    #   "args_len_flex_optional == args_len_flex", in which case
    #   "args_len_posonly_or_flex_optional >= args_len_flex_optional".
    # * "args_len_posonly_or_flex_optional < args_len_flex", in which case
    #   "args_len_flex_optional == args_len_posonly_or_flex_optional", in which
    #   case "args_len_posonly_or_flex_optional == args_len_flex_optional".
    #
    # Just roll with it, folks. It's best not to question the unfathomable.
    args_len_posonly_optional = (
        args_len_posonly_or_flex_optional - args_len_flex_optional)

    # Number of optional keyword-only parameters accepted by that callable.
    args_len_kwonly_optional = len(args_defaults_kwonly)

    # Number of mandatory positional-only parameters accepted by that callable.
    args_len_posonly_mandatory = args_len_posonly - args_len_posonly_optional

    # Number of mandatory flexible parameters accepted by that callable.
    args_len_flex_mandatory = args_len_flex - args_len_flex_optional

    # Number of mandatory keyword-only parameters accepted by that callable.
    args_len_kwonly_mandatory = args_len_kwonly - args_len_kwonly_optional

    # 0-based index of the first mandatory positional-only parameter accepted
    # by that callable in the "args_name" tuple.
    args_index_posonly_mandatory = 0

    # 0-based index of the first optional positional-only parameter accepted by
    # that callable in the "args_name" tuple.
    args_index_posonly_optional = args_len_posonly_mandatory

    # 0-based index of the first mandatory flexible parameter accepted by that
    # callable in the "args_name" tuple.
    args_index_flex_mandatory = (
        args_index_posonly_optional + args_len_posonly_optional)

    # 0-based index of the first optional flexible parameter accepted by that
    # callable in the "args_name" tuple.
    args_index_flex_optional = (
        args_index_flex_mandatory + args_len_flex_mandatory)

    # 0-based index of the first mandatory keyword-only parameter accepted by
    # that callable in the "args_name" tuple.
    args_index_kwonly_mandatory = (
        args_index_flex_optional + args_len_flex_optional)

    # 0-based index of the first optional keyword-only parameter accepted by
    # that callable in the "args_name" tuple.
    args_index_kwonly_optional = (
        args_index_kwonly_mandatory + args_len_kwonly_mandatory)

    # 0-based index of the variadic positional parameter accepted by that
    # callable in the "args_name" tuple if any *OR* a meaningless value
    # otherwise (i.e., if that callable accepts no such parameter).
    args_index_var_pos = (
        args_index_kwonly_optional + args_len_kwonly_optional)

    # 0-based index of the variadic keyword parameter accepted by that
    # callable in the "args_name" tuple if any *OR* a meaningless value
    # otherwise (i.e., if that callable accepts no such parameter).
    args_index_var_kw = args_index_var_pos + 1

    #FIXME: This can be trivially optimized even further. How? By avoiding
    #the "Parameter.POSITIONAL_ONLY"-style dictionary lookups here and
    #elsewhere. Indeed, accessing "Parameter" attributes is fragile, because
    #various attributes aren't even portably defined under older Python
    #versions (notably, "Parameter.POSITIONAL_ONLY"). Instead:
    #* Define a new public "ParameterKind" enumeration at the top of this
    #  submodule declaring members with the same names.
    #* Refactor all references to "Parameter" attributes to reference these
    #  enumeration members instead.
    #FIXME: This can be significantly optimized even further. How? By
    #compacting *ALL* of the following "for" loops into a single "for" loop.
    #Each "for" loop incurs significant overhead thanks to the "StopException"
    #implicitly raised at the end of each such loop.

    # For each mandatory positional-only parameter accepted by that callable,
    # yield a 3-tuple describing this parameter.
    for arg_posonly_mandatory in args_name[
        args_index_posonly_mandatory:args_index_posonly_optional]:
        yield (arg_posonly_mandatory, Parameter.POSITIONAL_ONLY, None,)

    # For the 0-based index of each optional flexible parameter accepted by
    # this callable and that parameter, yield a 3-tuple describing this
    # parameter.
    for arg_posonly_optional_index, arg_posonly_optional in enumerate(
        args_name[args_index_posonly_optional:args_index_flex_mandatory]):
        assert arg_posonly_optional_index < args_len_posonly_optional, (
            f'Optional positional-only parameter index {arg_posonly_optional_index} >= '
            f'optional positional-only parameter count {args_len_posonly_optional}.')
        yield (
            arg_posonly_optional,
            Parameter.POSITIONAL_ONLY,
            args_defaults_posonly_or_flex[arg_posonly_optional_index],
        )

    # For each mandatory flexible parameter accepted by that callable, yield a
    # 3-tuple describing this parameter.
    for arg_flex_mandatory in args_name[
        args_index_flex_mandatory:args_index_flex_optional]:
        yield (arg_flex_mandatory, Parameter.POSITIONAL_OR_KEYWORD, None,)

    # For the 0-based index of each optional flexible parameter accepted by
    # this callable and that parameter, yield a 3-tuple describing this
    # parameter.
    for arg_flex_optional_index, arg_flex_optional in enumerate(
        args_name[args_index_flex_optional:args_index_kwonly_mandatory]):
        assert arg_flex_optional_index < args_len_flex_optional, (
            f'Optional flexible parameter index {arg_flex_optional_index} >= '
            f'optional flexible parameter count {args_len_flex_optional}.')
        yield (
            arg_flex_optional,
            Parameter.POSITIONAL_OR_KEYWORD,
            args_defaults_posonly_or_flex[
                args_len_posonly_optional + arg_flex_optional_index],
        )

    # If that callable accepts a variadic positional parameter, yield a 3-tuple
    # describing this parameter *BEFORE* yielding keyword-only parameters.
    if is_func_arg_variadic_positional(func_codeobj):
        yield (args_name[args_index_var_pos], Parameter.VAR_POSITIONAL, None,)

    # For each mandatory keyword-only parameter accepted by that callable,
    # yield a 3-tuple describing this parameter.
    for arg_kwonly_mandatory in args_name[
        args_index_kwonly_mandatory:args_index_kwonly_optional]:
        yield (arg_kwonly_mandatory, Parameter.KEYWORD_ONLY, None,)

    # For the 0-based index each optional keyword-only parameter accepted by
    # that callable and that parameter, yield a 3-tuple describing this
    # parameter.
    for arg_kwonly_optional in args_name[
        args_index_kwonly_optional:args_index_var_pos]:
        yield (
            arg_kwonly_optional,
            Parameter.KEYWORD_ONLY,
            args_defaults_kwonly[arg_kwonly_optional],
        )

    # If that callable accepts a variadic keyword parameter, yield a 3-tuple
    # describing this parameter.
    if is_func_arg_variadic_keyword(func_codeobj):
        yield (args_name[args_index_var_kw], Parameter.VAR_KEYWORD, None,)
