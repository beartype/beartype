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
def test_poetry(
    monkeypatch: 'pytest.MonkeyPatch', tmp_path: 'pathlib.Path') -> None:
    '''
    Integration test testing that the third-party Poetry packaging devtool
    successfully installs this package into a placeholder package defined by a
    minimal-length ``pyproject.toml`` file requiring this package as a mandatory
    dependency.

    Parameters
    ----------
    monkeypatch : MonkeyPatch
        :mod:`pytest` fixture allowing various state associated with the active
        Python process to be temporarily changed for the duration of this test.
    tmp_path : pathlib.Path
        Abstract path encapsulating a temporary directory unique to this test,
        created in the base temporary directory.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.path.utilpathcopy import copy_dir
    from beartype._util.py.utilpyinterpreter import (
        get_interpreter_command_words)
    from beartype_test._util.command.pytcmdrun import (
        run_command_forward_output)
    from beartype_test._util.path.pytpathmain import get_main_dir
    from beartype_test._util.path.pytpathtest import (
        get_test_func_data_external_poetry_dir)

    # ....................{ CONSTANTS                      }....................
    # Tuple of all shell words with which to run the external "poetry" command.
    POETRY_ARGS = get_interpreter_command_words() + (
        # Fully-qualified name of the "poetry" package to be run.
        '-m', 'poetry',

        # Instruct Poetry to run the "install" subcommand.
        'install',

        # Force Poetry to implicitly answer "Yes" to all interactive queries.
        '--no-interaction',

        # *ONLY* install beartype as a mandatory runtime dependency of this
        # Poetry project. Do *NOT* bother installing this Poetry project itself.
        '--no-root',

        # For safety, simplicity, and efficiency, only pretend to install this
        # Poetry project. Thankfully, pretending suffices to validate that
        # Poetry and @beartype play nice with one another.
        '--dry-run',
    )

    # ....................{ LOCALS                         }....................
    # Path object encapsulating the absolute dirname of the top-level directory
    # providing the entirety of beartype.
    beartype_dir_src = get_main_dir()

    # Path object encapsulating the absolute dirname of this same directory
    # symbolically linked into this temporary directory under the dirname
    # referenced by the "pyproject.toml" file for this Poetry project:
    #     # In that "pyproject.toml" file:
    #     beartype = {path = "../beartype", develop = true}
    beartype_dir_trg = tmp_path / 'beartype'

    # Path object encapsulating the absolute dirname of the test-specific data
    # directory containing an empty Poetry-managed project whose
    # "pyproject.toml" file requires "beartype" as a Poetry-specific mandatory
    # runtime dependency.
    project_dir_src = get_test_func_data_external_poetry_dir()

    # Path object encapsulating the absolute dirname of this same Poetry project
    # copied into this temporary directory. Although a symbolic link *MIGHT*
    # suffice as well, we lack faith in Poetry. In all likelihood, Poetry
    # expects to be able to safely modify the contents of this directory.
    project_dir_trg = tmp_path / 'poetry'

    # ....................{ PATHS                          }....................
    # Symbolically link the beartype directory into this temporary directory.
    beartype_dir_trg.symlink_to(beartype_dir_src, target_is_directory=True)

    # Recursively copy this Poetry project into this temporary directory.
    copy_dir(src_dirname=project_dir_src, trg_dirname=project_dir_trg)

    # Change the current working directory (CWD) to that of this Poetry project.
    monkeypatch.chdir(project_dir_trg)

    # ....................{ COMMANDS                       }....................
    # Run the "poetry" command in the current ${PATH} with these options and
    # arguments, raising an exception on subprocess failure while forwarding
    # all standard output and error output by this subprocess to the
    # standard output and error file handles of the active Python process.
    run_command_forward_output(command_words=POETRY_ARGS)
