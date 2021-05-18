#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable tester** (i.e., callable testing various properties of
passed callables) utilities.

This private submodule implements utility functions dynamically introspecting
various high-level properties of arbitrary callables.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar._roarexc import _BeartypeUtilCallableException
from beartype._util.func.utilfunccodeobj import get_func_codeobj_or_none
from collections.abc import Callable
from typing import Any, Type

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
FUNC_NAME_LAMBDA = '<lambda>'
'''
Default name of all **pure-Python lambda functions** (i.e., function declared
as a ``lambda`` expression embedded in a larger statement rather than as a
full-blown ``def`` statement).

Python initializes the names of *all* lambda functions to this lambda-specific
placeholder string on lambda definition.

Caveats
----------
**Usage of this placeholder to differentiate lambda from non-lambda callables
invites false positives in unlikely edge cases.** Technically, malicious third
parties may externally change the name of any lambda function *after* defining
that function. Pragmatically, no one sane should ever do such a horrible thing.
While predictably absurd, this is also the only efficient (and thus sane) means
of differentiating lambda from non-lambda callables. Alternatives require
AST-based parsing, which comes with its own substantial caveats, concerns,
edge cases, and false positives. If you must pick your poison, pick this one.
'''

# ....................{ VALIDATORS                        }....................
#FIXME: Uncomment when needed.
# def die_unless_func_lambda(
#     # Mandatory parameters.
#     func: Any,
#
#     # Optional parameters.
#     exception_cls: Type[Exception] = _BeartypeUtilCallableException,
# ) -> None:
#     '''
#     Raise an exception unless the passed callable is a **pure-Python lambda
#     function** (i.e., function declared as a `lambda` expression embedded in a
#     larger statement rather than as a full-blown `def` statement).
#
#     Parameters
#     ----------
#     func : Callable
#         Callable to be inspected.
#     exception_cls : type, optional
#         Type of exception to be raised if this callable is *not* a pure-Python
#         lambda function. Defaults to :class:`_BeartypeUtilCallableException`.
#
#     Raises
#     ----------
#     exception_cls
#          If this callable is *not* a pure-Python lambda function.
#
#     See Also
#     ----------
#     :func:`is_func_lambda`
#         Further details.
#     '''
#
#     # If this callable is *NOT* a lambda function, raise an exception.
#     if not is_func_lambda(func):
#         assert isinstance(exception_cls, type), (
#             f'{repr(exception_cls)} not class.')
#         raise exception_cls(f'Callable {repr(func)} not lambda function.')


def die_unless_func_python(
    # Mandatory parameters.
    func: Any,

    # Optional parameters.
    exception_cls: Type[Exception] = _BeartypeUtilCallableException,
) -> None:
    '''
    Raise an exception if the passed callable is **C-based** (i.e., implemented
    in C as either a builtin bundled with the active Python interpreter *or*
    third-party C extension function).

    Equivalently, this validator raises an exception unless the passed function
    is **pure-Python** (i.e., implemented in Python as either a function or
    method).

    Parameters
    ----------
    func : Callable
        Callable to be inspected.
    exception_cls : type, optional
        Type of exception to be raised if this callable is neither a
        pure-Python function nor method. Defaults to
        :class:`_BeartypeUtilCallableException`.

    Raises
    ----------
    exception_cls
         If this callable has *no* code object and is thus *not* pure-Python.

    See Also
    ----------
    :func:`is_func_python`
        Further details.
    '''

    # If this callable is *NOT* pure-Python, raise an exception.
    if not is_func_python(func):
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not class.')
        raise exception_cls(
            f'Callable {repr(func)} code object not found '
            f'(e.g., due to being either C-based or a class or object '
            f'defining the ``__call__()`` dunder method).'
        )

# ....................{ TESTERS                           }....................
def is_func_lambda(func: Callable) -> bool:
    '''
    ``True`` only if the passed callable is a **pure-Python lambda function**
    (i.e., function declared as a ``lambda`` expression embedded in a larger
    statement rather than as a full-blown ``def`` statement).

    Parameters
    ----------
    func : Callable
        Callable to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this callable is a pure-Python lambda function.
    '''
    assert callable(func), f'{repr(func)} not callable.'

    # Return true only if this both...
    return (
        # This callable is pure-Python *AND*...
        is_func_python(func) and
        # This callable's name is the lambda-specific placeholder name
        # initially given by Python to *ALL* lambda functions. Technically,
        # this name may be externally changed by malicious third parties after
        # the declaration of this lambda. Pragmatically, no one sane would
        # ever do such a horrible thing.
        #
        # While predictably absurd, this is also the only efficient (and thus
        # sane) means of differentiating lambda from non-lambda callables.
        # Alternatives require AST-based parsing, which comes with its own
        # substantial caveats, concerns, and edge cases.
        func.__name__ == FUNC_NAME_LAMBDA
    )


def is_func_python(func: Any) -> bool:
    '''
    ``True`` only if the passed callable is **C-based** (i.e., implemented in
    Python as either a function or method rather than in C as either a builtin
    bundled with the active Python interpreter *or* third-party C extension
    function).

    Parameters
    ----------
    func : Callable
        Callable to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this callable is C-based.
    '''

    # Return true only if a code object underlies this callable. C-based
    # callables have *NO* such object.
    return get_func_codeobj_or_none(func) is not None
