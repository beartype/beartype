#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
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
    skip,
    skip_unless_os_linux,
    skip_unless_package,
    skip_unless_pathable,
)

# ....................{ TESTS                              }....................
#FIXME: Temporarily disabled, as this test is *INSANELY* slow. What's odd about
#this is that running the following command manually from the CLI is
#considerably faster despite appearing to be semantically equivalent to the
#command we're running below:
#    $ python3 -m nuitka --onefile --output-dir=/tmp beartype_test/a90_func/data/lib/nuitka/beartype_nuitka.py
#
#Moreover, there are quite a few critical warnings that will result in test
#failures, unless we resolve them, which we are too tired to do: e.g.,
#    Nuitka-Plugins:WARNING: Use '--enable-plugin=numpy' for: Numpy may miss DLLs otherwise.
#
#For the moment, let's just manually test nuitka integration when users
#justifiably complain that @beartype just broke nuitka integration. :p

# Skip this "nuitka"-specific functional test unless all of the following apply:
# * The "nuitka" package is importable under the active Python interpreter.
# * The third-party GCC compiler is in the current ${PATH}.
# * The current platform is *NOT* a Linux distribution. Although "nuitka"
#   technically *CAN* be used under non-Linux platforms, doing so is typically
#   non-trivial and likely to unexpectedly explode with catastrophic errors.
@skip('Insanely slow. Like, seriously *INSANELY* Universe-destroying slow.')
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
    from beartype._util.py.utilpyinterpreter import get_interpreter_filename
    from beartype_test._util.cmd.pytcmdrun import run_command_forward_output
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
    NUITKA_ARGS = (
        # Absolute filename of the executable running the active Python process.
        get_interpreter_filename(),

        # Fully-qualified name of the "nuitka" package to be run.
        '-m', 'nuitka',

        # Do *NOT* attempt to cache the compilation of intermediate C artifacts
        # with the third-party "ccache" command, which may not even necessarily
        # be installed into the current ${PATH}.
        '--disable-ccache',

        # Enable nuitka's so-called "onefile" mode. Doing so implicitly enables
        # nuitka's so-called "standalone" mode, which itself enables various
        # nuitka options that significantly alter how "nuitka" compiles code
        # (e.g., "--follow-imports"). Although enabling "onefile" mode consumes
        # considerably more space and time during testing, *MOST* users will
        # compile beartype-driven apps via "onefile" mode. Ergo, testing under
        # any other "nuitka" mode would be effectively wasting everyone's time.
        '--onefile',

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
    #FIXME: Instead capture the output and verify that that output matches the
    #expected output, which is:
    #'''
    #TypeHint(<class 'int'>)
    #TypeHint(<class 'float'>)
    #'''
