#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Poetry integration tests.**

This submodule functionally tests that the third-party Poetry packaging devtool
successfully installs this project.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
@skip_unless_package('poetry')
def test_poetry(tmp_path: 'pathlib.Path') -> None:
    '''
    Integration test testing that the third-party Poetry packaging devtool
    successfully installs this package into a placeholder package defined by a
    minimal-length ``pyproject.toml`` file requiring this package as a mandatory
    dependency.

    Parameters
    ----------
    tmp_path : pathlib.Path
        Abstract path encapsulating a temporary directory unique to this test,
        created in the base temporary directory.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.py.utilpyinterpreter import (
        get_interpreter_command_words)
    from beartype_test._util.command.pytcmdrun import (
        run_command_forward_output,
        run_command_forward_stderr_return_stdout,
    )
    from beartype_test._util.os.pytosshell import shell_quote

    #FIXME: Uncomment once all of this machinery actually exists. *sigh*
    # from beartype_test._util.path.pytpathtest import (
    #     get_test_func_data_lib_poetry_file)
    #
    # # ....................{ COMMAND                        }....................
    # # # Tuple of all shell words with which to run the external "poetry" command.
    # POETRY_ARGS = get_interpreter_command_words() + (
    #     # Fully-qualified name of the "poetry" package to be run.
    #     '-m', 'poetry',
    #
    #     # Absolute or relative dirname of a test-specific temporary directory to
    #     # which "poetry" will generate ignorable compilation artifacts.
    #     f'--output-dir={shell_quote(str(tmp_path))}',
    #
    #     # Absolute filename of a minimal-length example (MLE) leveraging this
    #     # project to be compiled by "poetry".
    #     str(get_test_func_data_lib_poetry_file()),
    # )
    #
    # # Run the "poetry" command in the current ${PATH} with these options and
    # # arguments, raising an exception on subprocess failure while forwarding
    # # all standard output and error output by this subprocess to the
    # # standard output and error file handles of the active Python process.
    # run_command_forward_output(command_words=POETRY_ARGS)
