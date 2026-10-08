#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Zensical** integration tests.

This submodule functionally tests that the third-party Zensical documentation
generator builds the documentation for this project.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
@skip_unless_package('zensical')
def test_zensical_docs(tmp_path) -> None:
    '''
    Functional test validating that the third-party :mod:`zensical` package
    builds the documentation for this project in the top-level ``docs/``
    subdirectory with no warnings.

    To do so, this test copies all files that Zensical reads into a temporary
    directory and then runs the ``zensical build --strict`` command in that
    directory. The ``zensical build`` command has no option to set its output
    directory. It always writes into the ``site/`` subdirectory of the
    directory containing its configuration file. Copying prevents this test
    from writing into the working tree of this project.

    Parameters
    ----------
    tmp_path : pathlib.Path
        Abstract path encapsulating a temporary directory unique to this unit
        test, created in the base temporary directory.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype._util.py.utilpyinterpreter import (
        get_interpreter_command_words)
    from beartype_test._util.command.pytcmdrun import run_command_forward_output
    from beartype_test._util.path.pytpathmain import get_main_repo_dir
    from shutil import (
        copy2,
        copytree,
    )

    # ..................{ COPY                               }..................
    # Path encapsulating the top-level directory of this project.
    main_repo_dir = get_main_repo_dir()

    # Copy all subdirectories that Zensical reads into the temporary directory.
    # These are the "docs_dir" and "custom_dir" settings in "zensical.toml".
    for subdir_basename in ('docs', 'overrides'):
        copytree(main_repo_dir / subdir_basename, tmp_path / subdir_basename)

    # Copy the Zensical configuration file into the temporary directory.
    copy2(main_repo_dir / 'zensical.toml', tmp_path / 'zensical.toml')

    # ..................{ ZENSICAL-BUILD                     }..................
    # Tuple of all shell words with which to run the "zensical build" command.
    ZENSICAL_ARGS = get_interpreter_command_words() + (
        # Fully-qualified name of the Zensical package to be run. Running this
        # package as a script is equivalent to running the "zensical" command,
        # but runs under the same version of Python as the active interpreter.
        '-m', 'zensical',

        # Build the documentation.
        'build',

        # Treat non-fatal warnings (e.g., broken links) as fatal errors.
        '--strict',
    )

    # Run this command in the temporary directory, raising an exception on
    # subprocess failure while forwarding all standard output and error output
    # by this subprocess to the standard output and error file handles of the
    # active Python process.
    run_command_forward_output(
        command_words=ZENSICAL_ARGS, popen_kwargs={'cwd': str(tmp_path)})
