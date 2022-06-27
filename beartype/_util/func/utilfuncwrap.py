#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable wrapper** (i.e., higher-level callable, typically
implemented as a decorator, wrapping a lower-level callable) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Any
from collections.abc import Callable

# ....................{ UNWRAPPERS                         }....................
def unwrap_func(func: Any) -> Callable:
    '''
    Lowest-level **wrappee** (i.e., callable wrapped by the passed wrapper
    callable) of the passed higher-level **wrapper** (i.e., callable wrapping
    the wrappee callable to be returned) if the passed callable is a wrapper
    *or* that callable as is otherwise (i.e., if that callable is *not* a
    wrapper).

    Specifically, this getter iteratively undoes the work performed by:

    * One or more consecutive uses of the :func:`functools.wrap` decorator on
      the wrappee callable to be returned.
    * One or more consecutive calls to the :func:`functools.update_wrapper`
      function on the wrappee callable to be returned.

    Parameters
    ----------
    func : Callable
        Wrapper callable to be inspected.

    Returns
    ----------
    Callable
        Either:

        * If the passed callable is a wrapper, the lowest-level wrappee
          callable wrapped by that wrapper.
        * Else, the passed callable as is.
    '''

    # While this callable still wraps another callable, unwrap one layer of
    # wrapping by reducing this wrapper to its next wrappee.
    while hasattr(func, '__wrapped__'):
        func = func.__wrapped__  # type: ignore[attr-defined]

    # Return this wrappee, which is now guaranteed to *NOT* be a wrapper.
    return func
