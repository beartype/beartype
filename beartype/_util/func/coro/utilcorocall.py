#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **asynchronous callable calling utilities** (i.e., callables
calling asynchronous callables in various ways).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from asyncio import (
    get_event_loop_policy,
    new_event_loop,
    set_event_loop,
)
from beartype.roar._roarexc import _BeartypeUtilCallableException
from collections.abc import Callable

# ....................{ CALLERS                            }....................
def run_coro_from_factory_sync(func: Callable, *args, **kwargs) -> object:
    '''
    Synchronously call the asynchronous coroutine object created and returned by
    calling the passed **asynchronous coroutine factory** (i.e., awaitable
    callable containing *no* ``yield`` expression implicitly creating and
    returning an awaitable object (i.e., satisfying the
    :class:`collections.abc.Awaitable` protocol) by being declared via the
    ``async def`` syntax and thus callable *only* when preceded by comparable
    ``await`` syntax) with the passed positional and keyword arguments,
    returning the object returned by that call (if any) and raising any
    exception raised by that call up the call stack (if any).

    Parameters
    ----------
    func : Callable
        Asynchronous coroutine factory to be called.

    All remaining parameters are passed as is to the ``func`` callable.

    Returns
    ----------
    object
        Object returned by calling the coroutine created and returned by calling
        this factory (if any).

    Raises
    ----------
    _BeartypeUtilCallableException
        If this callable is either:

        * Uncallable.
        * Callable but *not* an asynchronous coroutine factory.
    Exception
        If calling this coroutine raises an exception.

    See Also
    ----------
    :func:`beartype_test.conftest.pytest_pyfunc_call`
        :mod:`beartype`-specific function strongly inspiring this function.
    '''

    # Avoid circular import dependencies.
    from beartype._util.func.utilfunctest import is_func_coro

    # If this callable is uncallable, raise an exception.
    if not callable(func):
        raise _BeartypeUtilCallableException(
            f'Callable {repr(func)} uncallable.')
    # Else, this callable is actually callable.
    #
    # If this callable is *NOT* a coroutine, raise an exception.
    elif not is_func_coro(func):
        raise _BeartypeUtilCallableException(
            f'Callable {repr(func)} not asynchronous coroutine factory.')
    # Else, this callable is a coroutine.

    # Current event loop for the current threading context if any *OR* create a
    # new event loop otherwise. Note that the higher-level
    # asyncio.get_event_loop() getter is intentionally *NOT* called here, as
    # Python 3.10 broke backward compatibility by refactoring that getter to be
    # an alias for the wildly different asyncio.get_running_loop() getter, which
    # *MUST* be called only from within either an asynchronous callable or
    # running event loop. In either case, asyncio.get_running_loop() and thus
    # asyncio.get_event_loop() is useless in this context. Instead, we call the
    # lower-level get_event_loop_policy().get_event_loop() getter -- which
    # asyncio.get_event_loop() used to wrap. *facepalm*
    #
    # This getter should ideally return "None" rather than creating a new event
    # loop without our permission if no loop has been set. This getter instead
    # does the latter, implying that this function will typically instantiate
    # two event loops per asynchronous coroutine call:
    # * The first useless event loop implicitly created by this
    #   get_event_loop() call.
    # * The second useful event loop explicitly created by the
    #   subsequent new_event_loop() call.
    #
    # Since there exists *NO* other means of querying the current event loop, we
    # reluctantly bite the bullet and pay the drunken piper.
    event_loop_old = get_event_loop_policy().get_event_loop()

    # Close this loop, regardless of whether the prior get_event_loop() call
    # just implicitly created this loop, because the "asyncio" API offers *NO*
    # means of differentiating these two cases.
    event_loop_old.close()

    # New event loop isolated to this coroutine.
    #
    # Note that this event loop has yet to be set as the current event loop for
    # the current threading context. Explicit is better than implicit.
    event_loop = new_event_loop()

    # Set this as the current event loop for this threading context.
    set_event_loop(event_loop)

    # Coroutine object produced by this asynchronous callable. Technically,
    # coroutine functions are *NOT* actually coroutines; they're just syntactic
    # sugar implemented as standard synchronous functions dynamically creating
    # and returning asynchronous coroutine objects on each call.
    func_coroutine = func(*args, **kwargs)

    # Synchronously run a new asynchronous task implicitly scheduled to run this
    # coroutine, preserving the value returned by this coroutine (if any) while
    # reraising any exception raised by this coroutine up the call stack.
    func_return = event_loop.run_until_complete(func_coroutine)

    # Close this event loop.
    event_loop.close()

    # Return the value returned by this coroutine (if any).
    return func_return
