#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable parameter getter utilities** (i.e., callables
introspectively querying metadata on parameters accepted by arbitrary
callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilCallableException
from beartype.typing import Optional
from beartype._data.hint.datahinttyping import (
    Codeobjable,
    TypeException,
)
from beartype._util.func.arg.utilfuncargiter import (
    ARG_META_INDEX_NAME,
    iter_func_args,
)
from beartype._util.func.utilfunccodeobj import (
    get_func_codeobj_or_none,
    get_func_codeobj,
)
from collections.abc import Callable

# ....................{ GETTERS ~ arg                      }....................
#FIXME: Unit test us up, please.
def get_func_arg_first_name_or_none(
    # Mandatory parameters.
    func: Callable,

    # Optional parameters.
    is_unwrap: bool = True,
    exception_cls: TypeException = _BeartypeUtilCallableException,
) -> Optional[str]:
    '''
    Name of the first parameter listed in the signature of the passed
    pure-Python callable if any *or* :data:`None` otherwise (i.e., if that
    callable accepts *no* parameters and is thus parameter-less).

    Parameters
    ----------
    func : Codeobjable
        Pure-Python callable, frame, or code object to be inspected.
    is_unwrap: bool, optional
        :data:`True` only if this getter implicitly calls the
        :func:`beartype._util.func.utilfuncwrap.unwrap_func_all` function.
        Defaults to :data:`True` for safety. See :func:`.iter_func_args` for
        further commentary.
    exception_cls : type, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`._BeartypeUtilCallableException`.

    Returns
    -------
    Optional[str]
        Either:

        * If that callable accepts one or more parameters, the name of the first
          parameter listed in the signature of that callable.
        * Else, :data:`None`.

    Raises
    ------
    exception_cls
         If that callable is *not* pure-Python.
    '''

    # For metadata describing each parameter accepted by this callable...
    for arg_meta in iter_func_args(
        func=func,
        is_unwrap=is_unwrap,
        exception_cls=exception_cls,
    ):
        # Return the name of this parameter.
        return arg_meta[ARG_META_INDEX_NAME]  # type: ignore[return-value]
    # Else, the above "return" statement was *NOT* performed. In this case, this
    # callable accepts *NO* parameters.

    # Return "None".
    return None

# ....................{ GETTERS ~ args                     }....................
def get_func_args_flexible_len(
    # Mandatory parameters.
    func: Codeobjable,

    # Optional parameters.
    is_unwrap: bool = True,
    exception_cls: TypeException = _BeartypeUtilCallableException,
    exception_prefix: str = '',
) -> int:
    '''
    Number of **flexible parameters** (i.e., parameters passable as either
    positional or keyword arguments but *not* positional-only, keyword-only,
    variadic, or other more constrained kinds of parameters) accepted by the
    passed pure-Python callable.

    This getter transparently handles all of the following:

    * Conventional pure-Python callables.
    * If ``is_unwrap`` is :data:`True`:

      * Pure-Python **partials** (i.e., pure-Python callable
        :class:`functools.partial` objects directly wrapping pure-Python
        callables). If a partial is passed, this getter transparently returns
        the total number of flexible parameters accepted by the lower-level
        callable wrapped by this partial minus the number of flexible parameters
        partialized away by this partial.

    Parameters
    ----------
    func : Codeobjable
        Pure-Python callable, frame, or code object to be inspected.
    is_unwrap: bool, optional
        :data:`True` only if this getter implicitly calls the
        :func:`beartype._util.func.utilfuncwrap.unwrap_func_all` function.
        Defaults to :data:`True` for safety. See :func:`.get_func_codeobj` for
        further commentary.
    exception_cls : type, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`._BeartypeUtilCallableException`.
    exception_prefix : str, optional
        Human-readable label prefixing the message of any exception raised in
        the event of a fatal error. Defaults to the empty string.

    Returns
    -------
    int
        Number of flexible parameters accepted by this callable.

    Raises
    ------
    exception_cls
         If that callable is *not* pure-Python.
    '''

    # Avoid circular import dependencies.
    from beartype._util.api.utilapifunctools import (
        get_func_functools_partial_args,
        is_func_functools_partial,
        unwrap_func_functools_partial_once,
    )
    from beartype._util.func.utilfuncwrap import unwrap_func_boundmethod

    # Code object underlying the passed pure-Python callable unwrapped if any
    # *OR* "None" otherwise (i.e., that callable has *NO* code object).
    func_codeobj = get_func_codeobj_or_none(func=func, is_unwrap=is_unwrap)

    # If that callable has a code object, return the number of flexible
    # parameters accepted by this callable exposed by this code object.
    if func_codeobj:
        return func_codeobj.co_argcount
    # Else, that callable has *NO* code object.
    #
    # If unwrapping that callable *AND* that callable is a partial (i.e.,
    # "functools.partial" object wrapping a lower-level callable)...
    elif is_unwrap and is_func_functools_partial(func):
        # Pure-Python wrappee callable wrapped by that partial.
        wrappee = unwrap_func_functools_partial_once(func)

        # Positional and keyword parameters implicitly passed by this partial to
        # this wrappee.
        partial_args, partial_kwargs = get_func_functools_partial_args(func)

        # Number of flexible parameters accepted by this wrappee.
        #
        # Note that this recursive function call is guaranteed to immediately
        # bottom out and thus be safe. Why? Because a partial *CANNOT* wrap
        # itself, because a partial has yet to be defined when the
        # functools.partial.__init__() method defining that partial is called.
        # Technically, the caller *COULD* violate sanity by directly interfering
        # with the "func" instance variable of this partial after instantiation.
        # Pragmatically, a malicious edge case like that is unlikely in the
        # extreme. You are now reading this comment because this edge case just
        # blew up in your face, aren't you!?!? *UGH!*
        wrappee_args_flexible_len = get_func_args_flexible_len(
            func=wrappee,
            is_unwrap=is_unwrap,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )

        # Number of flexible parameters passed by this partial to this wrappee.
        partial_args_flexible_len = len(partial_args) + len(partial_kwargs)

        # Number of flexible parameters accepted by this wrappee minus the
        # number of flexible parameters passed by this partial to this wrappee.
        func_args_flexible_len = (
            wrappee_args_flexible_len - partial_args_flexible_len)

        # If this number is negative, the caller maliciously defined an invalid
        # partial passing more flexible parameters than this wrappee accepts. In
        # this case, raise an exception.
        if func_args_flexible_len < 0:
            raise exception_cls(
                f'{exception_prefix}{repr(func)} passes '
                f'{partial_args_flexible_len} parameter(s) to '
                f'{repr(wrappee)} accepting only '
                f'{wrappee_args_flexible_len} parameter(s) '
                f'(i.e., {partial_args_flexible_len} > '
                f'{wrappee_args_flexible_len}).'
            )
        # If this number is non-negative, implying the caller correctly defined
        # a valid partial passing no more flexible parameters than this wrappee
        # accepts.

        # Return this number.
        return func_args_flexible_len
    # Else, that callable is *NOT* a partial.
    #
    # By process of elimination, that callable *MUST* be an otherwise uncallable
    # object whose class has intentionally made that object callable by defining
    # the __call__() dunder method. Fallback to introspecting that method.

    # If that callable is *NOT* actually callable, raise an exception.
    if not callable(func):
        raise exception_cls(f'{exception_prefix}{repr(func)} uncallable.')
    # Else, that callable is callable.

    # "__call__" attribute of that callable if any *OR* "None" otherwise (i.e.,
    # if that callable is actually uncallable).
    func_call_attr = getattr(func, '__call__', None)

    # If that callable fails to define the "__call__" attribute, that callable
    # is actually uncallable. But the callable() builtin claimed that callable
    # to be callable above. In this case, raise an exception.
    #
    # Note that this should *NEVER* happen. Nonetheless, this just happened.
    if func_call_attr is None:  # pragma: no cover
        raise exception_cls(
            f'{exception_prefix}{repr(func)} uncallable '
            f'(i.e., defines no __call__() dunder method).'
        )
    # Else, that callable defines the __call__() dunder method.

    # Unbound pure-Python __call__() function encapsulated by this C-based bound
    # method descriptor bound to this callable object.
    func_call = unwrap_func_boundmethod(
        func=func_call_attr,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    # Number of flexible parameters accepted by this __call__() function.
    #
    # Note that this recursive function call is guaranteed to immediately bottom
    # out and thus be safe for similar reasons as given above.
    func_call_args_flexible_len = get_func_args_flexible_len(
        func=func_call,
        is_unwrap=is_unwrap,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    # If this number is zero, the caller maliciously defined an invalid
    # __call__() dunder method accepting *NO* parameters. Since this
    # paradoxically includes the mandatory first "self" parameter for a bound
    # method descriptor, it is probably infeasible for this edge case to occur.
    # Nonetheless, raise an exception.
    if not func_call_args_flexible_len:  # pragma: no cover
        raise exception_cls(
            f'{exception_prefix}{repr(func_call_attr)} accepts no '
            f'parameters despite being a bound instance method descriptor.'
        )
    # Else, this number is positive.

    # Return this number minus one to account for the fact that this bound
    # method descriptor implicitly passes the instance object to which this
    # method descriptor is bound as the first parameter to all calls of this
    # method descriptor.
    return func_call_args_flexible_len - 1


#FIXME: Unit test us up, please.
def get_func_args_nonvariadic_len(
    # Mandatory parameters.
    func: Codeobjable,

    # Optional parameters.
    is_unwrap: bool = True,
    exception_cls: TypeException = _BeartypeUtilCallableException,
) -> int:
    '''
    Number of **non-variadic parameters** (i.e., parameters passable as either
    positional, positional-only, keyword, or keyword-only arguments) accepted by
    the passed pure-Python callable.

    Parameters
    ----------
    func : Codeobjable
        Pure-Python callable, frame, or code object to be inspected.
    is_unwrap: bool, optional
        :data:`True` only if this getter implicitly calls the
        :func:`beartype._util.func.utilfuncwrap.unwrap_func_all` function.
        Defaults to :data:`True` for safety. See :func:`.get_func_codeobj` for
        further commentary.
    exception_cls : type, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`._BeartypeUtilCallableException`.

    Returns
    -------
    int
        Number of flexible parameters accepted by this callable.

    Raises
    ------
    exception_cls
         If that callable is *not* pure-Python.
    '''

    # Code object underlying the passed pure-Python callable unwrapped.
    func_codeobj = get_func_codeobj(
        func=func,
        is_unwrap=is_unwrap,
        exception_cls=exception_cls,
    )

    # Return the number of non-variadic parameters accepted by this callable.
    return func_codeobj.co_argcount + func_codeobj.co_kwonlyargcount
