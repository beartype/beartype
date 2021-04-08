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
from beartype.roar import _BeartypeUtilCallableException
from beartype._util.func.utilfunccodeobj import get_func_codeobj_or_none
from collections.abc import Callable

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ VALIDATORS                        }....................
#FIXME: Unit test us up, please.
def die_unless_func_python(
    # Mandatory parameters.
    func: Callable,

    # Optional parameters.
    exception_cls: type = _BeartypeUtilCallableException,
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
#FIXME: Unit test us up, please.
def is_func_python(func: Callable) -> bool:
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
