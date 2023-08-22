#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Project-wide functional Sphinx tests.**

This submodule functionally tests the :func:`beartype.beartype` decorator with
respect to the third-party Sphinx documentation build toolchain.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
@skip_unless_package('sphinx')
def test_sphinx_docs_other(tmp_path) -> None:
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
    # from beartype._util.module.lib.utilsphinx import (
    #     _SPHINX_AUTODOC_SUBPACKAGE_NAME)
    from beartype._util.py.utilpyinterpreter import (
        get_interpreter_command_words)
    from beartype_test._util.command.pytcmdrun import run_command_forward_output
    from beartype_test._util.path.pytpathtest import (
        get_test_func_data_lib_sphinx_dir)

    # ..................{ SPHINX-BUILD                       }..................
    # Tuple of all shell words with which to run the "sphinx-build" command.
    SPHINX_ARGS = get_interpreter_command_words() + (
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

        # Suffix raised exceptions with tracebacks. This is *CRITICAL.* By
        # default, Sphinx insanely emits *ONLY* useless exception messages for
        # fatal "autodoc" errors resembling:
        #     WARNING: autodoc: failed to import module 'beartype_sphinx'; the
        #     following exception was raised:
        #     cannot import name 'BeartypeConf' from partially initialized
        #     module 'beartype' (most likely due to a circular import)
        '-T',

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


#FIXME: For the benefit of the community, externally document how to do this
#for others at this open issue:
#    https://github.com/sphinx-doc/sphinx/issues/7008
#Note the trivial "conftest" submodule in this directory. Since this is all
#surprisingly easy, a simple comment describing this should easily suffice.
@skip_unless_package('sphinx')
def test_sphinx_docs_these(make_app, tmp_path) -> None:
    '''
    Functional test validating that the third-party :mod:`sphinx` package
    successfully builds ReadTheDocs (RTD)-hosted documentation for this project
    residing in the top-level ``doc/`` subdirectory.

    To do so, this test *effectively* externally runs the ``sphinx-build``
    command against our ``doc/src/` Sphinx document tree.

    Parameters
    ----------
    make_app : sphinx.testing.util.SphinxTestApp
        Factory fixture creating and returning a :mod:`pytest`-friendly Sphinx
        object encapsulating the process of running the ``sphinx-build``
        command with the passed parameters.
    tmp_path : pathlib.Path
        Abstract path encapsulating a temporary directory unique to this unit
        test, created in the base temporary directory.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype_test._util.command.pytcmdrun import run_command_forward_output
    from beartype_test._util.path.pytpathmain import get_main_sphinx_source_dir
    from beartype._util.py.utilpyinterpreter import (
        get_interpreter_command_words)

    # ..................{ SPHINX-BUILD                       }..................
    # Tuple of all shell words with which to run the "sphinx-build" command.
    SPHINX_ARGS = get_interpreter_command_words() + (
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

        #FIXME: Reenable once working. Sadly, Sphinx is currently emitting
        #warnings we have *NO* idea how to reasonably resolve. *sigh*
        # # Treat non-fatal warnings as fatal errors. This is *CRITICAL.* By
        # # default, Sphinx insanely emits non-fatal warnings for fatal "autodoc"
        # # errors resembling:
        # #     WARNING: autodoc: failed to import module 'beartype_sphinx'; the
        # #     following exception was raised:
        # #     No module named 'beartype_sphinx'
        # '-W',

        # Absolute or relative dirname of a test-specific subdirectory
        # containing a sample Sphinx structure exercising edge cases in the
        # @beartype decorator.
        str(get_main_sphinx_source_dir()),

        # Absolute or relative dirname of a test-specific temporary directory to
        # which Sphinx will emit ignorable rendered documentation files.
        str(tmp_path),
    )

    # Run this command, raising an exception on subprocess failure while
    # forwarding all standard output and error output by this subprocess to the
    # standard output and error file handles of the active Python process.
    run_command_forward_output(command_words=SPHINX_ARGS)
