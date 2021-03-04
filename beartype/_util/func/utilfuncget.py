#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Package-wide **callable utility getters** (i.e., callables dynamically
introspecting metadata attached to arbitrary callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import _BeartypeUtilCallableException
from collections.abc import Callable

# ....................{ GETTERS                           }....................
def get_func_wrappee(func: Callable) -> Callable:
    '''
    **Wrappee** (i.e., lower-level callable) originally wrapped by the passed
    **wrapper** (i.e., higher-level callable typically produced by the
    :mod:`functools.wraps` decorator) if this wrapper actually is a wrapper
    *or* raise an exception otherwise (i.e., if this wrapper is *not* actually
    a wrapper).

    Parameters
    ----------
    func : Callable
        Wrapper to be unwrapped.

    Returns
    ----------
    Callable
        Wrappee wrapped by this wrapper.

    Raises
    ----------
    _BeartypeUtilCallableException
         If this callable is *not* a wrapper.
    '''
    assert callable(func), f'{repr(func)} not callable.'

    # Wrappee wrapped by this wrapper if this wrapper actually is a wrapper
    # *OR* "None" otherwise.
    wrappee = getattr(func, '__wrapped__', None)

    # If this wrapper is *NOT* actually a wrapper, raise an exception.
    if wrappee is None:
        raise _BeartypeUtilCallableException(
            f'Callable {func} not wrapper '
            f'(i.e., "__wrapped__" attribute undefined).')
    # Else, this wrapper is a wrapper. In this case, this wrappee exists.

    # Return this wrappee.
    return wrappee
