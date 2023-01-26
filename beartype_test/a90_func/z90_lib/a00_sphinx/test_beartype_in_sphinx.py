#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Project-wide functional beartype-in-Sphinx tests.**

This submodule functionally tests the :func:`beartype.beartype` decorator to
conditionally reduce to a noop when the active Python interpreter is building
documentation for the third-party :mod:`sphinx` package.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
@skip_unless_package('sphinx')
def test_beartype_in_sphinx(tmp_path) -> None:
    '''
    Functional test validating that the :func:`beartype.beartype` decorator
    conditionally reduces to a noop when the active Python interpreter is
    building documentation for the third-party :mod:`sphinx` package.

    To do so, this test externally runs the ``sphinx-build`` command against a
    minimal-length Sphinx document tree exercising all known edge cases.

    Parameters
    ----------
    tmp_path : pathlib.Path
        Abstract path encapsulating a temporary directory unique to this unit
        test, created in the base temporary directory.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype._util.mod.lib.utilsphinx import (
        _SPHINX_AUTODOC_SUBPACKAGE_NAME)
    from beartype._util.py.utilpyinterpreter import get_interpreter_filename
    from beartype_test._util.cmd.pytcmdrun import run_command_forward_output
    from beartype_test._util.path.pytpathtest import (
        get_test_func_data_lib_sphinx_dir)

    # ..................{ SPHINX-BUILD                       }..................
    # Tuple of all shell words with which to run the external "mypy" command.
    SPHINX_ARGS = (
        # Absolute filename of the executable running the active Python process.
        get_interpreter_filename(),

        # Fully-qualified name of the Sphinx package to be run. Interestingly,
        # running this package as a script is semantically equivalent to running
        # the "sphinx-build" command (with the added bonus of running under the
        # same version of Python as the active Python interpreter).
        '-m', 'sphinx',

        # Avoid caching data into a "{OUTPUTDIR}/.doctrees/" subdirectory.
        # Although typically advisable, "{OUTPUTDIR}" is an ignorable temporary
        # test-specific directory deleted immediately after completion of this
        # test. Caching data would only needlessly consume time and space.
        '-E',

        # Enable the HTML mode, rendering HTML-specific documentation files.
        # Although technically arbitrary, this is the typical default mode.
        '-b', 'html',

        # Treat non-fatal warnings as fatal errors. This is *CRITICAL.* By
        # default, Sphinx insanely emits non-fatal warnings for fatal "autodoc"
        # errors resembling:
        #     WARNING: autodoc: failed to import module 'beartype_sphinx'; the
        #     following exception was raised:
        #     No module named 'beartype_sphinx'
        '-W',

        # Absolute or relative dirname of a test-specific subdirectory
        # containing a sample Sphinx structure exercising edge cases in the
        # @beartype decorator.
        str(get_test_func_data_lib_sphinx_dir()),

        # Absolute or relative dirname of a test-specific temporary directory to
        # which Sphinx will emit ignorable rendered documentation files.
        str(tmp_path),
    )

    # Run this command, raising an exception on subprocess failure while
    # forwarding all standard output and error output by this subprocess to the
    # standard output and error file handles of the active Python process.
    run_command_forward_output(command_words=SPHINX_ARGS)
