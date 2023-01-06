#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
:mod:`pytest` **global test configuration** (i.e., early-time configuration
guaranteed to be run by :mod:`pytest` *after* passed command-line arguments are
parsed).

:mod:`pytest` implicitly imports *all* functionality defined by this module
into *all* submodules of this subpackage.

See Also
----------
https://github.com/pytest-dev/pytest-asyncio/blob/master/pytest_asyncio/plugin.py
    :mod:`pytest` plugin strongly inspiring this implementation. Despite its
    popularity,, pytest-asyncio is mostly unmaintained, poorly commented and
    documented, overly obfuscatory, has an extreme number of unresolved issues
    and unmerged pull requests, and just generally exhibits code smells.
'''

# ....................{ TODO                               }....................
#FIXME: Consider refactoring the pytest_pyfunc_call() hook defined below into:
#* A pull request against pytest itself. Pytest absolutely requires support for
#  asynchronous test functions. This is 2021, people.
#* A new competing "pytest-async" plugin. This is substantially easier but less
#  ideal, as pytest *REALLY* both wants and needs this functionality.

# ....................{ IMPORTS                            }....................
from asyncio import (
    get_event_loop_policy,
    new_event_loop,
    set_event_loop,
)
from functools import wraps
from inspect import iscoroutinefunction
from pytest import hookimpl
from warnings import (
    catch_warnings,
    simplefilter,
)

# ....................{ HOOKS ~ configure                  }....................
@hookimpl(hookwrapper=True, tryfirst=True)
def pytest_pyfunc_call(pyfuncitem: 'Function') -> None:
    '''
    Hook wrapper called immediately *before* calling the passed test function.

    Specifically, this hook wrapper:

    * If this test function is synchronous (i.e., declared with ``def``),
      preserves this test function as is.
    * If this test function is asynchronous (i.e., declared with ``async
      def``), wraps this test function in a synchronous wrapper function
      synchronously running this test function under an event loop uniquely
      isolated to this test function. For safety, each asynchronous test
      function is run under a new event loop.

    This wrapper wraps all non-wrapper ``pytest_pyfunc_call()`` hooks and is
    hopefully called *before* all wrapper ``pytest_pyfunc_call()`` hooks. See
    also `the official pytest hook wrapper documentation <hook wrapper_>`__.

    Parameters
    ----------
    pyfuncitem : Function
        :mod:`pytest` object encapsulating the test function to be run.

    .. _hook wrapper:
       https://docs.pytest.org/en/6.2.x/writing_plugins.html#hookwrapper-executing-around-other-hooks
    '''

    # Test function to be called by this hook.
    test_func = pyfuncitem.obj

    # If this test function is an asynchronous coroutine function (i.e.,
    # callable declared with "async def" containing *NO* "yield"
    # expressions)...
    #
    # Note that we intentionally prefer calling this well-tested tester of the
    # well-tested "inspect" module rather than our comparable
    # beartype._util.func.utilfunctest.is_func_coro() tester, which
    # is hopefully but *NOT* necessarily known to be working here.
    if iscoroutinefunction(test_func):
        @wraps(test_func)
        def test_func_synchronous(*args, **kwargs):
            '''
            Closure synchronously calling the current asynchronous test
            coroutine function under a new event loop uniquely isolated to this
            coroutine.
            '''

            # With a warning context manager...
            with catch_warnings():
                # Ignore *ALL* deprecating warnings emitted by the
                # get_event_loop() function called below. For unknown reasons,
                # CPython 3.11 devs thought that emitting a "There is no current
                # event loop" warning (erroneously classified as a
                # "deprecation") was a wonderful idea. "asyncio" is arduous
                # enough to portably support as it is. Work with me here, guys!
                simplefilter('ignore', DeprecationWarning)

                # Current event loop for the current threading context if any
                # *OR* create a new event loop otherwise. Note that the
                # higher-level asyncio.get_event_loop() getter is intentionally
                # *NOT* called here, as Python 3.10 broke backward compatibility
                # by refactoring that getter to be an alias for the wildly
                # different asyncio.get_running_loop() getter, which *MUST* be
                # called only from within either an asynchronous callable or
                # running event loop. In either case, asyncio.get_running_loop()
                # and thus asyncio.get_event_loop() is useless in this context.
                # Instead, we call the lower-level
                # get_event_loop_policy().get_event_loop() getter -- which
                # asyncio.get_event_loop() used to wrap. *facepalm*
                #
                # This getter should ideally return "None" rather than creating
                # a new event loop without our permission if no loop has been
                # set. This getter instead does the latter, implying that this
                # closure will typically instantiate two event loops per
                # asynchronous coroutine test function:
                # * The first useless event loop implicitly created by this
                #   get_event_loop() call.
                # * The second useful event loop explicitly created by the
                #   subsequent new_event_loop() call.
                #
                # Since there exists *NO* other means of querying the current
                # event loop, we reluctantly bite the bullet and pay the piper.
                event_loop_old = get_event_loop_policy().get_event_loop()

                # Close this loop, regardless of whether the prior
                # get_event_loop() call just implicitly created this loop,
                # because the "asyncio" API offers *NO* means of differentiating
                # these two common edge cases. *double facepalm*
                event_loop_old.close()

            # New event loop isolated to this coroutine.
            #
            # Note that this event loop has yet to be set as the current event
            # loop for the current threading context. Explicit is better than
            # implicit.
            event_loop = new_event_loop()

            # Set this as the current event loop for this threading context.
            set_event_loop(event_loop)

            # Coroutine object produced by this asynchronous coroutine test
            # function. Technically, coroutine functions are *NOT* actually
            # coroutines; they're just syntactic sugar implemented as standard
            # synchronous functions dynamically creating and returning
            # asynchronous coroutine objects on each call.
            test_func_coroutine = test_func(*args, **kwargs)

            # Synchronously run a new asynchronous task implicitly scheduled to
            # run this coroutine, ignoring the value returned by this coroutine
            # (if any) while reraising any exception raised by this coroutine
            # up the call stack to pytest.
            event_loop.run_until_complete(test_func_coroutine)

            # Close this event loop.
            event_loop.close()

        # Replace this asynchronous coroutine test function with this
        # synchronous closure wrapping this test function.
        pyfuncitem.obj = test_func_synchronous

    # Perform this test by calling this test function.
    yield
