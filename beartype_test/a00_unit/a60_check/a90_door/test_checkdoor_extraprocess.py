#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **extraprocess Decidedly Object-Oriented Runtime-checking (DOOR)
type-checking unit tests** (i.e., unit tests exercising :mod:`beartype.door`
functionality within a Python subprocess forked from the active Python process).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ raisers                    }....................
def test_door_extraprocess_multiprocessing(monkeypatch: 'MonkeyPatch') -> None:
    '''
    Test the :class:`beartype.door.die_if_unbearable` raiser function with
    respect to Python subprocesses forked by the standard :mod:`multiprocessing`
    submodule.

    Parameters
    ----------
    monkeypatch : MonkeyPatch
        :mod:`pytest` fixture allowing various state associated with the active
        Python process to be temporarily changed for the duration of this test.

    See Also
    --------
    https://github.com/python/cpython/issues/44791
        Beartype issue exercised by this unit test.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.py.utilpyinterpreter import (
        get_interpreter_command_words)
    from beartype_test._util.command.pytcmdrun import (
        run_command_forward_output,
        run_command_forward_stderr_return_stdout,
    )
    from beartype_test._util.path.pytpathtest import (
        get_test_unit_data_door_extraprocess_dir)

    # ....................{ ASSERTS                        }....................
    # Temporarily change the current working directory (CWD) to the
    # test-specific root directory containing the data package tested below.
    monkeypatch.chdir(get_test_unit_data_door_extraprocess_dir())

    # Tuple of all shell words with which to run a data submodule in this test
    # suite as a script within a Python subprocess forked from the active Python
    # process via the standard command-line option "-m".
    PYTHON_ARGS = get_interpreter_command_words() + (
        # Fully-qualified name of this data submodule with respect to the root
        # directory containing the package containing this submodule.
        '-m', 'data_door_multiprocessing',
    )

    # Attempt to...
    try:
        # Standard output emitted by running this this module as a script,
        # raising an exception on subprocess failure while forwarding all
        # standard error emitted by this subprocess to the standard error file
        # handle of this parent Python process.
        PYTHON_STDOUT = run_command_forward_stderr_return_stdout(
            command_words=PYTHON_ARGS)

        # Assert this output to be the expected output printed by this module.
        assert PYTHON_STDOUT == 'And faster still, beyond all human speed,'
    # If doing so raised *ANY* exception whatsoever...
    except:
        # Re-run the same module as a script except forward both all standard
        # output *AND* error emitted by this subprocess to the standard output
        # and error file handles of this parent Python process. Doing so
        # significantly improves debuggability in the event of a fatal error.
        run_command_forward_output(command_words=PYTHON_ARGS)

        # Re-raise this exception.
        raise
