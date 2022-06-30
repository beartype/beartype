#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable parameter getter utilities** (i.e., callables
introspectively querying metadata on parameters accepted by arbitrary
callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilCallableException
from beartype._util.func.utilfunccodeobj import get_func_codeobj
from beartype._util.func.utilfuncwrap import unwrap_func
from beartype._data.datatyping import Codeobjable, TypeException

# ....................{ GETTERS                            }....................
def get_func_args_len_flexible(
    # Mandatory parameters.
    func: Codeobjable,

    # Optional parameters.
    is_unwrapping: bool = True,
    exception_cls: TypeException = _BeartypeUtilCallableException,
) -> int:
    '''
    Number of **flexible parameters** (i.e., parameters passable as either
    positional or keyword arguments) accepted by the passed pure-Python
    callable.

    Parameters
    ----------
    func : Codeobjable
        Pure-Python callable, frame, or code object to be inspected.
    is_unwrapping: bool, optional
        ``True`` only if this getter implicitly calls the :func:`unwrap_func`
        function to unwrap this possibly higher-level wrapper into its possibly
        lowest-level wrappee *before* returning the code object of that
        wrappee. Note that doing so incurs worst-case time complexity ``O(n)``
        for ``n`` the number of lower-level wrappees wrapped by this wrapper.
        Defaults to ``True`` for robustness. Why? Because this getter *must*
        always introspect lowest-level wrappees rather than higher-level
        wrappers. The latter typically do *not* accurately replicate the
        signatures of the former. In particular, decorator wrappers typically
        wrap decorated callables with variadic positional and keyword
        parameters (e.g., ``def _decorator_wrapper(*args, **kwargs)``). Since
        neither constitutes a flexible parameter, this getter raises an
        exception when passed such a wrapper with this boolean set to
        ``False``. For this reason, only set this boolean to ``False`` if you
        pretend to know what you're doing.
    exception_cls : type, optional
        Type of exception in the event of a fatal error. Defaults to
        :class:`_BeartypeUtilCallableException`.

    Returns
    ----------
    int
        Number of flexible parameters accepted by this callable.

    Raises
    ----------
    :exc:`exception_cls`
         If the passed callable is *not* pure-Python.
    '''

    # If unwrapping that callable, do so *BEFORE* querying that callable for
    # its code object to avoid desynchronization between the two.
    if is_unwrapping:
        func = unwrap_func(func)
    # Else, that callable is assumed to have already been unwrapped by the
    # caller. We should probably assert that, but doing so requires an
    # expensive call to hasattr(). What you gonna do?

    # Code object underlying the passed pure-Python callable unwrapped.
    func_codeobj = get_func_codeobj(func=func, exception_cls=exception_cls)

    # Return the number of flexible parameters accepted by this callable.
    return func_codeobj.co_argcount
