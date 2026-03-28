#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **pyright** (i.e., Microsoft's official Python static type-checker,
underlying the popular `pylance` VSCode plugin) integration tests.

This submodule functionally tests the this project's compliance with
pyright-based static type-checking and hence :pep:`561`.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import (
    skip_if_ci,
    skip_if_python_version_less_than,
    skip_unless_pathable,
)

# ....................{ TESTS                              }....................
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
# Skip this test unless all of the following apply:
# * The "pyright" command is in the current "${PATH}".
# * Tests are *NOT* running remotely under GitHub Actions-based continuous
#   integration (CI). Since the only sane means of installing "pyright" under
#   GitHub Actions is via the third-party "jakebailey/pyright-action" action
#   (which implicitly exercises this package against "pyright"), explicitly
#   exercising this package against "pyright" yet again would only needlessly
#   complicate CI workflows and consume excess CI minutes for *NO* gain.
@skip_unless_pathable('pyright')
@skip_if_ci()
def test_pep561_pyright_self() -> None:
    '''
    Integration test testing this project's compliance with :pep:`561` by
    externally running ``pyright`` (i.e., the most popular third-party static
    type checker as of this test) against this project's top-level package.

    See Also
    --------
    :mod:`pytest_pyright`
        Third-party :mod:`pytest` plugin automating this integration. Since this
        integration is trivial *and* since :mod:`beartype` assiduously avoids
        *all* mandatory dependencies, we prefer performing this integration
        manually to depending on third-party plugins. Moreover, that plugin:

        * Internally violates privacy encapsulation in
          :mod:`pytest` by widely importing private :mod:`pytest` attributes.
        * Explicitly admonishes downstream dependencies *not* to depend upon
          this plugin:

            This project was created for internal use within another project of
            mine, support will be minimal.
    '''

    # Defer test-specific imports.
    from beartype.meta import PACKAGE_NAME
    from beartype_test._util.path.pytpathmain import get_main_dir

    # Statically type-check this package residing in the root directory of this
    # project against the "pyright" command residing in the current "${PATH}".
    _pyright_package(
        project_dirname=str(get_main_dir()), package_name=PACKAGE_NAME)


# Skip this test unless the "pyright" command is in the current "${PATH}".
@skip_unless_pathable('pyright')
@skip_if_python_version_less_than('3.12')
def test_pep561_pyright_others() -> None:
    '''
    Integration test testing this project's compliance with :pep:`561` by
    externally running ``pyright`` (i.e., the most popular third-party static
    type checker as of this test) against a sample test-specific project
    containing a sample test-specific Python package.

    This sample package is entirely fictional. To expose friction and avoid
    regressions in real-world downstream users attempting to type-check their
    own third-party packages with ``pyright``, this sample package attempts to
    reproduce a litany of resolved issues submitted to our issue tracker with
    various minimal reproducible examples (MREs).

    This sample package intentionally utilizes a variety of PEP-compliant type
    hints available only under recent Python versions, including:

    * :pep:`695`-compliant type aliases available only under Python >= 3.12.
    '''

    # Defer test-specific imports.
    from beartype_test._util.path.pytpathtest import (
        get_test_func_data_external_pyright_dir)

    # Statically type-check this sample package residing in this test data
    # directory against the "pyright" command residing in the current "${PATH}".
    _pyright_package(
        project_dirname=str(get_test_func_data_external_pyright_dir()),
        package_name='remnants_huge',  # <-- *lol* *facepalm* *sigh*
    )

# ....................{ PRIVATE ~ runners                  }....................
def _pyright_package(project_dirname: str, package_name: str) -> None:
    '''
    Statically type-check the Python package or module with the passed name
    directly residing in the external directory with the passed dirname against
    the third-party ``pyright`` command assumed to exist in the current
    ``${PATH}``.

    This runner forks ``pyright`` as a subprocess of the active ``pytest``
    process, raising an exception on subprocess failure while forwarding all
    standard output and error output by this subprocess to the standard output
    and error file handles of the active ``pytest`` process.

    Parameters
    ----------
    project_dirname : str
        Absolute dirname of the top-level directory containing the Python
        package or module to be run against `pyright`.
    package_name : str
        Unqualified basename of the Python package or module (excluding trailing
        ``.py`` filetype in the case of a module) directly residing in this
        top-level directory to be run against `pyright`.
    monkeypatch : MonkeyPatch
        :mod:`pytest` fixture allowing various state associated with the active
        Python process to be temporarily changed for the duration of this test.
    '''
    assert isinstance(project_dirname, str), (
        f'{repr(project_dirname)} not string.')
    assert isinstance(package_name, str), f'{repr(package_name)} not string.'

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.py.utilpyversion import get_python_version_major_minor
    from beartype_test._util.command.pytcmdrun import run_command_forward_output
    from pytest import MonkeyPatch

    # ....................{ LOCALS                         }....................
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
        package_name,
    )

    # ....................{ RUN                            }....................
    # Inside the equivalent of the "monkeypatch" fixture...
    with MonkeyPatch.context() as monkeypatch:
        # Temporarily change to the root directory for this project *BEFORE*
        # running the "pyright" command. Unlike the "mypy" command, "pyright"
        # fails to accept an option or argument specifying the target directory
        # containing the specified package. If this directory is *NOT* changed
        # to here, "pyright" fails with a fatal error under "tox" resembling:
        #      File or directory
        #      "/home/leycec/py/beartype/.tox/py311-coverage/tmp/beartype" does
        #      not exist.
        monkeypatch.chdir(project_dirname)

        # Run this command, raising an exception on subprocess failure while
        # forwarding all standard output and error output by this subprocess to
        # the standard output and error file handles of the active process.
        run_command_forward_output(command_words=PYRIGHT_ARGS)
