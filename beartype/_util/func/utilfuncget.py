#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable getters** (i.e., utility functions dynamically
querying and retrieving various properties of passed callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilCallableException
from beartype.typing import (
    Any,
    Callable,
)
from beartype._data.hint.datahinttyping import TypeException

# ....................{ GETTERS ~ descriptor               }....................
def get_func_classmethod_wrappee(
    # Mandatory parameters.
    func: Any,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableException,
    exception_prefix: str = '',
) -> Callable:
    '''
    Pure-Python unbound function wrapped by the passed **C-based unbound class
    method descriptor** (i.e., method decorated by the builtin
    :class:`classmethod` decorator, yielding a non-callable instance of that
    :class:`classmethod` decorator class implemented in low-level C and
    accessible via the low-level :attr:`object.__dict__` dictionary rather than
    as class or instance attributes).

    Parameters
    ----------
    func : object
        Object to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised. Defaults to
        :static:`_BeartypeUtilCallableException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    ----------
    Callable
        Pure-Python unbound function wrapped by this class method descriptor.

    Raises
    ----------
    :exc:`exception_cls`
         If the passed object is *not* a class method descriptor.

    See Also
    ----------
    :func:`beartype._util.func.utilfunctest.is_func_classmethod`
        Further details.
    '''

    # Avoid circular import dependencies.
    from beartype._util.func.utilfunctest import die_unless_func_classmethod

    # If this object is *NOT* a class method descriptor, raise an exception.
    die_unless_func_classmethod(
        func=func,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # Else, this object is a class method descriptor.

    # Return the pure-Python function wrapped by this descriptor. Just do it!
    return func.__func__


def get_func_staticmethod_wrappee(
    # Mandatory parameters.
    func: Any,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableException,
    exception_prefix: str = '',
) -> Callable:
    '''
    Pure-Python unbound function wrapped by the passed **C-based unbound static
    method descriptor** (i.e., method decorated by the builtin
    :class:`staticmethod` decorator, yielding a non-callable instance of that
    :class:`staticmethod` decorator class implemented in low-level C and
    accessible via the low-level :attr:`object.__dict__` dictionary rather than
    as class or instance attributes).

    Parameters
    ----------
    func : object
        Object to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised. Defaults to
        :static:`_BeartypeUtilCallableException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    ----------
    Callable
        Pure-Python unbound function wrapped by this static method descriptor.

    Raises
    ----------
    :exc:`exception_cls`
         If the passed object is *not* a static method descriptor.

    See Also
    ----------
    :func:`beartype._util.func.utilfunctest.is_func_staticmethod`
        Further details.
    '''

    # Avoid circular import dependencies.
    from beartype._util.func.utilfunctest import die_unless_func_staticmethod

    # If this object is *NOT* a static method descriptor, raise an exception.
    die_unless_func_staticmethod(
        func=func,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # Else, this object is a static method descriptor.

    # Return the pure-Python function wrapped by this descriptor. Just do it!
    return func.__func__
