#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Project-wide functional static type-checker tests.**

This submodule functionally tests the this project's compliance with
third-party static type-checkers and hence :pep:`561`.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import (
    skip_if_ci,
    skip_if_pypy,
    skip_unless_package,
    skip_unless_pathable,
)

# ....................{ TESTS ~ mypy                       }....................
#FIXME: Consider submitting as a StackOverflow post. Dis iz l33t, yo!
#FIXME: Sadly, diz iz no longer l33t. Mypy broke its runtime API. This test now
#spuriously fails under CI with a non-human-readable exception message
#resembling:
#       TypeError: 'mypy' is not a package
#
#The solution? Refactor this test ala the existing test_pep561_pyright() test,
#which thankfully already does everything we want here. Rejoice!

# If the third-party "mypy" package is unavailable, skip this test. Note that:
# * "mypy" is the reference standard for static type-checking in Python.
# * Unbelievably, "mypy" violates PEP 8 versioning standards by failing to
#   define the "mypy.__init__.__version__" attribute, which means that passing
#   the optional "minimum_version" parameter to the skip_unless_package()
#   decorator fails on failing to find that attribute. While we *COULD* instead
#   explicitly test the "mypy.version.__version__" attribute, doing so would
#   require defining a new and *MUCH* less trivial
#   @skip_unless_module_attribute decorator. For sanity, we instead currently
#   accept the importability of the "mypy" package as sufficient, which it
#   absolutely isn't, but what you gonna do, right?
#
# Skip this "mypy"-specific functional test unless all of the following apply:
# * The "mypy" package is importable under the active Python interpreter.
# * The active Python interpreter is *NOT* PyPy. mypy is currently incompatible
#   with PyPy for inscrutable reasons that should presumably be fixed at some
#   future point. See also:
#     https://mypy.readthedocs.io/en/stable/faq.html#does-it-run-on-pypy
@skip_unless_package('mypy')
@skip_if_pypy()
def test_pep561_mypy() -> None:
    '''
    Functional test testing this project's compliance with :pep:`561` by
    externally running :mod:`mypy` (i.e., the most popular third-party static
    type checker as of this test) against this project's top-level package.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.py.utilpyinterpreter import (
        get_interpreter_command_words)
    from beartype_test._util.command.pytcmdrun import (
        run_command_return_stdout_stderr)
    from beartype_test._util.path.pytpathmain import (
        get_main_mypy_config_file,
        get_main_package_dir,
    )

    # ....................{ COMMAND                        }....................
    # Tuple of all shell words with which to run the external "mypy" command.
    MYPY_ARGS = get_interpreter_command_words() + (
        # Fully-qualified name of the "mypy" package to be run.
        '-m', 'mypy',

        # Absolute dirname of this project's top-level mypy configuration. Since
        # our "tox" configuration isolates testing to a temporary directory,
        # mypy is unable to find its configuration without assistance.
        '--config-file', str(get_main_mypy_config_file()),

        # Absolute dirname of this project's top-level package.
        str(get_main_package_dir()),
    )

    # Run this command, raising an exception on subprocess failure while
    # forwarding all standard output and error output by this subprocess to the
    # standard output and error file handles of the active Python process.
    #
    # Note that we intentionally do *NOT* assert that call to have exited with
    # a successful exit code. Although mypy does exit with success on local
    # developer machines, it inexplicably does *NOT* under remote GitHub
    # Actions-based continuous integration despite "mypy_stderr" being empty.
    # Ergo, we conveniently ignore the former in favour of the latter.
    mypy_stdout, mypy_stderr = run_command_return_stdout_stderr(
        command_words=MYPY_ARGS)

    # ....................{ ASSERT                         }....................
    # If "mypy" emitted *NO* warnings or errors to either standard
    # output or error.
    #
    # Note that "mypy" predominantly emits both warnings and errors to "stdout"
    # rather than "stderr", despite this contravening sane POSIX semantics.
    # They did this because some guy complained about not being able to
    # trivially grep "mypy" output, regardless of the fact that redirecting
    # stderr to stdout is a trivial shell fragment (e.g., "2>&1"), but let's
    # break everything just because some guy can't shell. See also:
    #     https://github.com/python/mypy/issues/1051
    #
    # Assert "mypy" to have emitted *NO* warnings or errors to "stdout".
    # Unfortunately, doing so is complicated by the failure of "mypy" to
    # conform to sane POSIX semantics. Specifically:
    # * If "mypy" succeeds, "mypy" emits to "stdout" a single line resembling:
    #       Success: no issues found in 83 source files
    # * If "mypy" fails, "mypy" emits to "stdout" *ANY* other line(s).
    #
    # Ergo, asserting this string to start with "Success:" suffices. Note this
    # assertion depends on "mypy" internals and is thus fragile, but that we
    # have *NO* sane alternative. Specifically, if either...
    if (
        # Mypy emitted one or more characters to standard error *OR*...
        mypy_stderr or
        # Mypy emitted standard output that does *NOT* contain this substring...
        'Success: no issues found' not in mypy_stdout
    ):
        # Print this string to standard output for debuggability, which pytest
        # then captures and reprints on this subsequent assertion failure.
        print(mypy_stdout)

        # Force an unconditional assertion failure.
        assert False
    # Else, "mypy" emitted *NO* warnings or errors to either standard output or
    # error. In this case, encourage this test to succeed by reducing to a noop.

# ....................{ TESTS ~ pyright                    }....................
# If the external third-party "pyright" command is *NOT* pathable (i.e., an
# executable command residing in the ${PATH} of the local filesystem), skip this
# test. Note that:
# * "pyright" is the most popular static type-checker for Python, mostly due to
#   "pylance" (i.e., the most popular Python language plugin for VSCode, itself
#   the most popular integrated development environment (IDE)) both bundling
#   *AND* enabling "pyright" by default.
# * "pyright" is implemented in pure-TypeScript (i.e., JavaScript augmented with
#   type hints transpiling down to pure-JavaScript at compilation time).
# * There exists a largely unrelated "pyright" Python package shim unofficially
#   published at:
#    https://github.com/RobertCraigie/pyright-python
#   Sadly, that package does fundamentally unsafe things like:
#   * Violating privacy encapsulation of "pytest", repeatedly.
#   * Performing online "npm"-based auto-installation of the "pyright"
#     JavaScript package if currently not installed. Currently, there exists
#     *NO* means of disabling that dubious behavior.
#   Ergo, we resoundingly ignore that high-level package in favour of the
#   low-level "pyright" command. Such is quality assurance. It always hurts.
#
# Skip this "pyright"-specific functional test unless all of the following
# apply:
# * The "pyright" command is in the current "${PATH}".
# * Tests are *NOT* running remotely under GitHub Actions-based continuous
#   integration (CI). Since the only sane means of installing "pyright" under
#   GitHub Actions is via the third-party "jakebailey/pyright-action" action
#   (which implicitly exercises this package against "pyright"), explicitly
#   exercising this package against "pyright" yet again would only needlessly
#   complicate CI workflows and consume excess CI minutes for *NO* gain.
@skip_unless_pathable('pyright')
@skip_if_ci()
def test_pep561_pyright() -> None:
    '''
    Functional test testing this project's compliance with :pep:`561` by
    externally running :mod:`pyright` (i.e., the most popular third-party static
    type checker as of this test) against this project's top-level package.

    See Also
    ----------
    :mod:`pytest_pyright`
        Third-party :mod:`pytest` plugin automating this integration. Since this
        integration is trivial *and* since :mod:`beartype` assiduously avoids
        *all* mandatory dependencies, we perform this integration manually.
        Moreover, this plugin:

        * Internally violates privacy encapsulation in
          :mod:`pytest` by widely importing private :mod:`pytest` attributes.
        * Explicitly admonishes downstream dependencies *not* to depend upon
          this plugin:

            This project was created for internal use within another project of
            mine, support will be minimal.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.meta import PACKAGE_NAME
    from beartype._util.py.utilpyversion import get_python_version_major_minor
    from beartype_test._util.command.pytcmdrun import run_command_forward_output

    # ....................{ COMMAND                        }....................
    # Tuple of all shell words with which to run the external "pyright" command.
    PYRIGHT_ARGS = (
        # Basename of the external "pyright" command to be run.
        'pyright',

        #FIXME: Note that we *COULD* additionally pass the "--verifytypes"
        #option, which exposes further "pyright" complaints. Let's avoid doing
        #so until someone explicitly requests we do so, please. This has dragged
        #on long enough, people!

        # Major and minor version of the active Python interpreter, ignoring the
        # patch version of this interpreter.
        '--pythonversion', get_python_version_major_minor(),

        # Relative basename of this project's top-level package. Ideally, the
        # absolute dirname of this package would instead be passed as:
        #     str(get_main_package_dir())
        #
        # Doing so succeeds when manually running tests via our top-level
        # "pytest" script but fails when automatically running tests via the
        # "tox" command, presumably due to "pyright" failing to recognize that
        # that dirname encapsulates a Python package. *sigh*
        PACKAGE_NAME,
    )

    # Run this command, raising an exception on subprocess failure while
    # forwarding all standard output and error output by this subprocess to the
    # standard output and error file handles of the active Python process.
    run_command_forward_output(command_words=PYRIGHT_ARGS)
