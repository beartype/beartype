#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :mod:`pyinstaller` integration tests.

This submodule functionally tests the third-party PyInstaller fromework
successfully generates executable binaries containing arbitrary modules
registering :mod:`beartype.claw` import hooks.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
@skip_unless_package('PyInstaller')
def test_pyinstaller(
    monkeypatch: 'pytest.MonkeyPatch', tmp_path: 'pathlib.Path') -> None:
    '''
    Integration test validating that the :mod:`beartype` package raises *no*
    unexpected exceptions when an arbitrary package bundled by the third-party
    PyInstaller framework into an exogenous executable binary registers a
    :mod:`beartype.claw` import hook, which conflicts with a competing
    PyInstaller-specific import hook required by PyInstaller to generate
    working binaries.

    Parameters
    ----------
    monkeypatch : MonkeyPatch
        :mod:`pytest` fixture allowing various state associated with the active
        Python process to be temporarily changed for the duration of this test.
    tmp_path : pathlib.Path
        Abstract path encapsulating a temporary directory unique to this test,
        created in the base temporary directory.

    See Also
    --------
    https://github.com/beartype/beartype/issues/599
        Non-trivial issue resolved by this test.
    https://github.com/zbowling/beartype-pyinstaller-repro
        Non-trivial minimal-length example strongly inspiring this test.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.path.utilpathcopy import copy_dir
    from beartype._util.py.utilpyinterpreter import (
        get_interpreter_command_words)
    from beartype_test._util.command.pytcmdrun import (
        run_command_forward_output,
        run_command_return_stdout_stderr,
    )
    from beartype_test._util.path.pytpathtest import (
        get_test_func_data_external_pyinstaller_dir)
    from pytest import raises
    from subprocess import CalledProcessError

    # ....................{ CONSTANTS ~ str                }....................
    # Unqualified rootname (i.e., basename excluding the suffixing filetype) of
    # the root Python script to be bundled by PyInstaller into a single
    # platform-specific binary file.
    SCRIPT_ROOTNAME = 'death_and_darkness'

    # Unqualified basename of the root Python script to be bundled by
    # PyInstaller into a single platform-specific binary file.
    SCRIPT_BASENAME = f'{SCRIPT_ROOTNAME}.py'

    # Arbitrary string that, when passed to this script as its only command-line
    # argument, instructs this script to print the same argument back as this
    # script's only standard output.
    SCRIPT_ARG_PRINT = 'The shady visions come to domineer,'

    # Arbitrary string that, when passed to this script as its only command-line
    # argument, instructs this script to fail with a @beartype-driven runtime
    # type-checking violation induced by a annotated variable assignment
    # assigned a value violating the type hint annotating that assignment.
    SCRIPT_ARG_FAIL = 'and_the_symmetry'

    # ....................{ CONSTANTS ~ tuple              }....................
    # Tuple of all shell words with which to run the external "pyinstaller"
    # command, building both this root Python script *AND* dependent package
    # imported by that script into a single platform-specific binary file.
    PYINSTALLER_ARGS = get_interpreter_command_words() + (
        # Fully-qualified name of the "pyinstaller" package to be run.
        '-m', 'PyInstaller',

        #FIXME: Simplicity is great and all... but this is *EXTREMELY* slow.
        #"--onedir" is likely to be faster. But is it faster enough to warrant
        #the associated headaches? No idea. For now, slow and simple it is! \o/
        # For simplicity, generate a single platform-specific binary file
        # independently runnable from *ANY* directory (rather than a file
        # dependently runnable *ONLY* from the directory that file resides in).
        '--onefile',

        # Unqualified basename of the root Python script to be bundled.
        SCRIPT_BASENAME,
    )

    # ....................{ LOCALS                         }....................
    # Path object encapsulating the absolute dirname of the test-specific data
    # directory containing a PyInstaller-managed project whose specification
    # configures PyInstaller to bundle this project into a working executable.
    project_dir_src = get_test_func_data_external_pyinstaller_dir()

    # Path object encapsulating the absolute dirname of this same PyInstaller
    # project copied into this temporary directory. Although a symbolic link
    # *MIGHT* suffice as well, we lack faith in PyInstaller. In all likelihood,
    # PyInstaller expects to be able to modify the contents of this directory.
    project_dir_trg = tmp_path / 'pyinstaller'

    # Path object encapsulating the absolute filename of the root Python script
    # to be bundled by PyInstaller into a single platform-specific binary file.
    project_script = project_dir_src / SCRIPT_BASENAME

    # ....................{ SCRIPT                         }....................
    # Validate that this script behaves as expected outside a
    # PyInstaller-bundled executable before validating this script as a
    # PyInstaller-bundled executable below.

    # Standard output and error output by running this root Python script as a
    # subprocess with a non-magic string argument while raising an exception on
    # subprocess failure.
    command_stdout, command_stderr = run_command_return_stdout_stderr(
        command_words=(get_interpreter_command_words() + (
            project_script, SCRIPT_ARG_PRINT,)))

    # Assert that doing so emitted back:
    # * This same non-magic string argument as standard output.
    # * *NO* standard error.
    assert command_stdout == SCRIPT_ARG_PRINT
    assert command_stderr == ''

    # Assert that running this root Python script as a subprocess *WITHOUT*
    # arguments fails with the expected exception while forwarding all standard
    # output and error output by this subprocess to the standard output and
    # error file handles of the active Python process.
    with raises(CalledProcessError):
        run_command_forward_output(command_words=(
            get_interpreter_command_words() + (project_script,)))

    # Assert that running this root Python script as a subprocess with a magic
    # string argument fails with the expected exception while forwarding all
    # standard output and error output by this subprocess to the standard output
    # and error file handles of the active Python process.
    with raises(CalledProcessError):
        run_command_forward_output(command_words=(
            get_interpreter_command_words() + (
                project_script, SCRIPT_ARG_FAIL,)))

    # ....................{ PATHS                          }....................
    # Recursively copy this PyInstaller project into this temporary directory.
    copy_dir(src_dirname=project_dir_src, trg_dirname=project_dir_trg)

    # Change the current working directory (CWD) to that of this PyInstaller
    # project.
    monkeypatch.chdir(project_dir_trg)

    # ....................{ PYINSTALLER                    }....................
    # Run the "pyinstaller" command in the current ${PATH} with these options
    # and arguments, raising an exception on subprocess failure while forwarding
    # all standard output and error output by this subprocess to the standard
    # output and error file handles of the active Python process.
    run_command_forward_output(command_words=PYINSTALLER_ARGS)

    # ....................{ PYINSTALLER ~ script           }....................
    #FIXME: Great! Now actually run the resulting "dist / SCRIPT_ROOTNAME"
    #executable. Note that this filename *MUST* be appended by ".exe" on
    #Windows. Grr! Let's define more magic constants above, please. *sigh*
