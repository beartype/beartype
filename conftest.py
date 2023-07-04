#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Root test configuration** (i.e., early-time configuration guaranteed to be
run by :mod:`pytest` *before* passed command-line arguments are parsed) for
this test suite.

Caveats
----------
For safety, this configuration should contain *only* early-time hooks
absolutely required by :mod:`pytest` design to be defined in this
configuration. Hooks for which this is the case (e.g.,
:func:`pytest_addoption`) are explicitly annotated as such in official
:mod:`pytest` documentation with a note resembling:

    Note

    This function should be implemented only in plugins or ``conftest.py``
    files situated at the tests root directory due to how pytest discovers
    plugins during startup.

This file is the aforementioned ``conftest.py`` file "...situated at the tests
root directory."
'''

# ....................{ IMPORTS                            }....................
from collections.abc import Callable
from pytest import Function
from typing import Optional

# ....................{ HOOKS ~ ini                        }....................
def pytest_configure(config) -> None:
    '''
    Hook programmatically configuring the top-level ``"pytest.ini"`` file.
    '''

    # Programmatically add our custom "run_in_subprocess" mark, enabling tests
    # to notify the pytest_pyfunc_call() hook that they require isolation to a
    # Python subprocess of the current Python process.
    config.addinivalue_line(
        'markers',
        f'{_MARK_NAME_SUBPROCESS}: mark test to run in an isolated subprocess',
    )

# ....................{ HOOKS ~ test : run                 }....................
def pytest_pyfunc_call(pyfuncitem: Function) -> Optional[bool]:
    '''
    Hook intercepting the call to run the passed :mod:`pytest` test function.

    Specifically, this test:

    * If this test has been decorated by our custom
      ``@pytest.mark.run_in_subprocess`` marker, runs this test in a Python
      subprocess of the current Python process isolated to this test.
    * Else, runs this test in the current Python process by deferring to the
      standard :mod:`pytest` logic for running this test.

    Parameters
    ----------
    pyfuncitem: Function
        :mod:`pytest`-specific object encapsulating the current test function
        being run.

    Returns
    ----------
    Optional[bool]
        Either:

        * If this hook ran this test, :data:`True`.
        * If this hook did *not* run this test, :data:`None`.

    See Also
    ----------
    https://github.com/ansible/pytest-mp/issues/15#issuecomment-1342682418
        GitHub comment by @pelson (Phil Elson) strongly inspiring this hook.
    '''

    # If this test has been decorated by our custom
    # @pytest.mark.run_in_subprocess marker...
    if _MARK_NAME_SUBPROCESS in pyfuncitem.keywords:
        # Defer hook-specific imports.
        from functools import partial
        from multiprocessing import Process
        from pytest import fail

        # Test function to be run.
        test_func = pyfuncitem.function

        # Partial object encapsulating the _run_test_in_subprocess() helper
        # bound to the current "pyfuncitem" object encapsulating this test.
        #
        # Note that this logic is robust under POSIX-compliant platforms (e.g.,
        # Linux, macOS) but *EXTREMELY* fragile under Windows, where the
        # "multiprocessing.Process" class sadly leverages the mostly unusable
        # "pickle" module rather than the mostly usable third-party "dill"
        # module. Notably, we intentionally:
        # * Leverage a "partial" object (which "pickle" silently supports)
        #   rather than a closure (which "pickle" rejects with
        #   non-human-readable exceptions).
        # * Pass the actual low-level test function being tested (which "pickle"
        #   silently supports) rather than the high-level "pyfuncitem" object
        #   encapsulating that function (which "pickle" rejects with
        #   non-human-readable exceptions).
        test_func_in_subprocess = partial(_test_func_in_subprocess, test_func)

        # Python subprocess tasked with running this test.
        test_subprocess = Process(target=test_func_in_subprocess)

        # Begin running this test in this subprocess.
        test_subprocess.start()

        # Block this parent Python process until this test completes.
        test_subprocess.join()

        # If this subprocess reports non-zero exit status, this test failed. In
        # this case...
        if test_subprocess.exitcode != 0:
            # Human-readable exception message to be raised.
            exception_message = (
                f'Test "{pyfuncitem.name}" failed in isolated subprocess with:')

            # Raise a pytest-compliant exception.
            raise fail(exception_message, pytrace=False)
        # Else, this subprocess reports zero exit status. In this case, this
        # test succeeded.

        # Notify pytest that this hook successfully ran this test.
        return True

    # Notify pytest that this hook avoided attempting to run this test, in which
    # case pytest will continue to look for a suitable runner for this test.
    return None

# ....................{ PRIVATE ~ globals                  }....................
_MARK_NAME_SUBPROCESS = 'run_in_subprocess'
'''
**Subprocess mark** (i.e., name of our custom :mod:`pytest` mark, enabling tests
to notify the :func:`.pytest_pyfunc_call` hook that they require isolation to a
Python subprocess of the current Python process).
'''

# ....................{ PRIVATE ~ classes                  }....................
class _UnbufferedOutputStream(object):
    '''
    **Unbuffered standard output stream** (i.e., proxy object encapsulating a
    buffered standard output stream by forcefully flushing that stream on all
    writes to that stream).

    See Also
    ----------
    https://github.com/ansible/pytest-mp/issues/15#issuecomment-1342682418
        GitHub comment by @pelson (Phil Elson) strongly inspiring this class.
    '''

    def __init__(self, stream) -> None:
        self.stream = stream

    def write(self, data) -> None:
        self.stream.write(data)
        self.stream.flush()

    def writelines(self, datas) -> None:
        self.stream.writelines(datas)
        self.stream.flush()

    def __getattr__(self, attr: str) -> object:
        return getattr(self.stream, attr)

# ....................{ PRIVATE ~ functions                }....................
def _test_func_in_subprocess(test_func: Callable) -> object:
    '''
    Run the passed :mod:`pytest` test function isolated to a Python subprocess
    of the current Python process.

    Parameters
    ----------
    test_func : Callable
        Test function to be run.

    Returns
    ----------
    object
        Arbitrary object returned by this test if any *or* :data:`None`.
    '''

    # Defer subpracess-specific imports.
    import sys

    # Monkey-patch the unbuffered standard error and output streams of this
    # subprocess with buffered equivalents, ensuring that pytest will reliably
    # capture *all* standard error and output emitted by running this test.
    sys.stderr = _UnbufferedOutputStream(sys.stderr)
    sys.stdout = _UnbufferedOutputStream(sys.stdout)

    # Run this test and return the result of doing so.
    return test_func()
