#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Zensical** integration tests.

This submodule functionally tests that the third-party Zensical documentation
generator builds the documentation for this project.
'''

# ....................{ TODO                               }....................
#FIXME: When time permits, please additionally restore:
#* "test_docreadme" back to our "beartype_test/a90_func/a80_doc/" subdirectory,
#  please: e.g.,
#    cp /tmp/test_docreadme.py beartype_test/a90_func/a80_doc/
#  We'll then need to lightly refactor that to test markdown validity,
#  probably. *shrug*
#* "sphinx" as a new "zensical" script, please: e.g.,
#    cp /tmp/sphinx zensical
#  Then, refactor that script for compliance with Zensical. Build instructions
#  reside in "docs/code.md", apparently? ...blegh!

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
    from beartype._util.path.utilpathcopy import copy_dir
    from beartype._util.py.utilpyinterpreter import (
        get_interpreter_command_words)
    from beartype_test._util.command.pytcmdrun import run_command_forward_output
    from beartype_test._util.path.pytpathmain import get_main_repo_dir
    from shutil import copy2

    # ..................{ CONSTANTS                          }..................
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

    # ..................{ LOCALS                             }..................
    # Path encapsulating the top-level directory of this project.
    main_repo_dir = get_main_repo_dir()

    # ..................{ PATHS                              }..................
    # Recursively copy all subdirectories that Zensical reads into this
    # temporary directory, corresponding to the "docs_dir" and "custom_dir"
    # settings defined by our top-level "zensical.toml" configuration file.
    for subdir_basename in ('docs', 'overrides'):
        copy_dir(
            src_dirname=main_repo_dir / subdir_basename,
            trg_dirname=tmp_path / subdir_basename,
        )

    #FIXME: shutil.copy2(), huh? Yeah. This some nonsense. Let's define a new
    #copy_file() function in our existing "utilpathcopy" submodule internally
    #deferring to shutil.copy2(). Pretty weird API, honestly. *shrug*
    # Copy the Zensical configuration file into the temporary directory.
    copy2(main_repo_dir / 'zensical.toml', tmp_path / 'zensical.toml')

    # ....................{ COMMANDS                       }....................
    # Run this command in the temporary directory, raising an exception on
    # subprocess failure while forwarding all standard output and error output
    # by this subprocess to the standard output and error file handles of the
    # active Python process.
    run_command_forward_output(
        command_words=ZENSICAL_ARGS, popen_kwargs={'cwd': str(tmp_path)})
