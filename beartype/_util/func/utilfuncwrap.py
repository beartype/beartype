#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable wrapper** utilities.

This private submodule implements utility functions dynamically introspecting
callables wrapped by other callables.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from collections.abc import Callable

# ....................{ UNWRAPPERS                        }....................
#FIXME: Unit test us up, please.
def unwrap_func(func: Callable) -> Callable:
    '''
    Lowest-level **wrappee** (i.e., callable wrapped by the passed wrapper
    callable) of the passed higher-level **wrapper** (i.e., callable wrapping
    the wrappee callable to be returned) if the passed callable is a wrapper
    *or* this callable as is otherwise (i.e., if this callable is *not* a
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
          callable wrapped by this wrapper.
        * Else, the passed callable as is.
    '''
    assert callable(func), f'{repr(func)} not callable.'

    # While this callable still wraps another callable, unwrap one layer of
    # wrapping by reducing this wrapper to its next wrappee.
    while hasattr(func, '__wrapped__'):
        func = func.__wrapped__  # type: ignore[attr-defined]

    # Return this lowest-level wrappee, which is now guaranteed to *NOT* itself
    # by a wrapper.
    return func
