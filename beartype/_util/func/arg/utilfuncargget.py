#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable parameter getter utilities** (i.e., callables
introspectively querying metadata on parameters accepted by arbitrary
callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar._roarexc import _BeartypeUtilCallableException
from beartype._util.func.utilfunccodeobj import get_func_unwrapped_codeobj
from beartype._util.utiltyping import CallableCodeObjable, TypeException

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

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
