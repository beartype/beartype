#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :mod:`functools` utilities (i.e., low-level callables handling the
standard :mod:`functools` module).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Any,
    Tuple,
)
from beartype._cave._cavefast import (
    CallableFunctoolsLruCacheType,
    CallableFunctoolsPartialType,
)
from beartype._data.hint.datahintfactory import TypeGuard
from beartype._data.hint.datahinttyping import DictStrToAny
from collections.abc import (
    Callable,
    # Generator,
)

# ....................{ TESTERS                            }....................
def is_func_functools_lru_cache(func: Any) -> TypeGuard[Callable]:
    '''
    :data:`True` only if the passed object is a
    :func:`functools.lru_cache`-memoized **pseudo-callable** (i.e., low-level
    C-based callable object both created and returned by the standard
    :func:`functools.lru_cache` decorator).

    This tester enables callers to detect when a user-defined callable has been
    decorated by the :func:`functools.lru_cache` decorator, which creates
    low-level C-based callable objects requiring special handling elsewhere.

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a
        :func:`functools.lru_cache`-memoized callable.
    '''

    # Defer heavyweight tester-specific imports with potential side effects --
    # notably, increased costs to space and time complexity.

    # Return true only if the type of that callable is the low-level C-based
    # private type of all objects created and returned by the standard
    # @functools.lru_cache decorator.
    return isinstance(func, CallableFunctoolsLruCacheType)


def is_func_functools_partial(func: Any) -> TypeGuard[
    CallableFunctoolsPartialType]:
    '''
    :data:`True` only if the passed object is a **partial** (i.e., pure-Python
    callable :class:`functools.partial` object wrapping a possibly C-based
    callable).

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a
        :func:`functools.partial`-wrapped callable.
    '''

    # Return true only if the type of that callable is the high-level
    # pure-Python public type of all objects created and returned by the
    # standard functools.partial() factory.
    return isinstance(func, CallableFunctoolsPartialType)

# ....................{ GETTERS                            }....................
def get_func_functools_partial_args(
    func: CallableFunctoolsPartialType) -> Tuple[tuple, DictStrToAny]:
    '''
    2-tuple ``(args, kwargs)`` providing the positional and keyword parameters
    with which the passed **partial** (i.e., pure-Python callable
    :class:`functools.partial` object directly wrapping this possibly C-based
    callable) was originally partialized.

    Parameters
    ----------
    func : CallableFunctoolsPartialType
        Partial to be inspected.

    Returns
    -------
    Tuple[tuple, DictStrToAny]
        2-tuple ``(args, kwargs)`` such that:

        * ``args`` is the tuple of the zero or more positional parameters passed
          to the callable partialized by this partial.
        * ``kwargs`` is the dictionary mapping from the name to value of the
          zero or more keyword parameters passed to the callable partialized by
          this partial.
    '''
    assert isinstance(func, CallableFunctoolsPartialType), (
        f'{repr(func)} not "function.partial"-wrapped callable.')

    # Return a 2-tuple providing the positional and keyword parameters with
    # which this partial was originally partialized.
    return (func.args, func.keywords)

# ....................{ UNWRAPPERS                         }....................
def unwrap_func_functools_partial_once(
    func: CallableFunctoolsPartialType) -> Callable:
    '''
    Possibly C-based callable directly wrapped by the passed **partial** (i.e.,
    pure-Python callable :class:`functools.partial` object directly wrapping
    this possibly C-based callable).

    Parameters
    ----------
    func : CallableFunctoolsPartialType
        Partial to be unwrapped.

    Returns
    -------
    Callable
        Possibly C-based callable directly wrapped by this partial.
    '''
    assert isinstance(func, CallableFunctoolsPartialType), (
        f'{repr(func)} not "function.partial"-wrapped callable.')

    # Return the public "func" instance variable of this partial wrapper as is.
    return func.func
