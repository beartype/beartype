#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Project-wide nuitka integration tests.**

This submodule functionally tests that the third-party ``nuitka`` compiler
successfully compiles this pure-Python project.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import (
    skip_unless_os_linux,
    skip_unless_package,
    skip_unless_pathable,
)

# ....................{ TESTS                              }....................
# Skip this "nuitka"-specific functional test unless all of the following apply:
# * The "nuitka" package is importable under the active Python interpreter.
# * The third-party GCC compiler is in the current ${PATH}.
# * The current platform is *NOT* a Linux distribution. Although "nuitka"
#   technically *CAN* be used under non-Linux platforms, doing so is typically
#   non-trivial and likely to unexpectedly explode with catastrophic errors.
@skip_unless_os_linux()
@skip_unless_package('nuitka')
@skip_unless_pathable('gcc')
def test_nuitka(capsys, tmp_path) -> None:
    '''
    Functional test testing that the third-party ``nuitka`` compiler
    successfully compiles a minimal-length example (MLE) extensively leveraging
    this project.

    Parameters
    ----------
    capsys
        :mod:`pytest`-specific systems capability fixture.
    tmp_path : pathlib.Path
        Abstract path encapsulating a temporary directory unique to this unit
        test, created in the base temporary directory.
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
    from beartype_test._util.path.pytpathtest import (
        get_test_func_data_lib_nuitka_file)

    # ....................{ COMMAND                        }....................
    #FIXME: "nuitka" occasionally attempts to download external third-party
    #tooling. By default, it interactively prompts the user before doing so.
    #This is obviously bad for automated testing. Thankfully, "nuitka" avoids
    #doing so when it detects that stdin has been redirected to "/dev/null".
    #Ergo, improve the run_command_forward_output() function called below to
    #*ALWAYS* redirect stdin to "/dev/null". We *ALWAYS* want that everywhere.

    # Tuple of all shell words with which to run the external "nuitka" command.
    NUITKA_ARGS = get_interpreter_command_words() + (
        # Fully-qualified name of the "nuitka" package to be run.
        '-m', 'nuitka',

        # Do *NOT* attempt to cache the compilation of intermediate C artifacts
        # with the third-party "ccache" command, which may not even necessarily
        # be installed into the current ${PATH}.
        '--disable-ccache',

        #FIXME: Currently disabled as enabling even just this incurs *FAR* too
        #much time and space. Sadness ensues.
        # # Instruct "nuitka" to additionally compile the entirety of the
        # # "beartype" package. By default, "nuitka" only compiles the script
        # # (specified below).
        # '--follow-import-to=beartype',
 
        # Absolute or relative dirname of a test-specific temporary directory to
        # which "nuitka" will generate ignorable compilation artifacts.
        f'--output-dir={shell_quote(str(tmp_path))}',

        # Absolute filename of a minimal-length example (MLE) leveraging this
        # project to be compiled by "nuitka".
        str(get_test_func_data_lib_nuitka_file()),
    )

    # With pytest's default capturing of standard output and error temporarily
    # disabled...
    #
    # Technically, this is optional. Pragmatically, "nuitka" is sufficiently
    # slow that failing to do this renders this test silent for several tens of
    # seconds to minutes, which is significantly worse than printing progress.
    with capsys.disabled():
        # Run the "nuitka" command in the current ${PATH} with these options and
        # arguments, raising an exception on subprocess failure while forwarding
        # all standard output and error output by this subprocess to the
        # standard output and error file handles of the active Python process.
        run_command_forward_output(command_words=NUITKA_ARGS)

    # ....................{ ASSERT                         }....................
    # Absolute or relative filename of the executable binary generated by
    # "nuitka" after running the above command.
    COMPILED_FILENAME = str(tmp_path / 'beartype_nuitka.bin')

    # Standard output emitted by running this executable binary.
    COMPILED_STDOUT = run_command_forward_stderr_return_stdout(
        COMPILED_FILENAME)

    # Assert that this is the expected output.
    assert COMPILED_STDOUT == (
'''ClassTypeHint(<class 'int'>)
ClassTypeHint(<class 'float'>)''')
