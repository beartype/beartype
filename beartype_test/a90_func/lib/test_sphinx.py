#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Project-wide functional Sphinx tests.**

This submodule functionally tests the this project's behaviour with respect to
the third-party :mod:`sphinx` package.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.mark.pytskip import (
    skip_if_python_version_greater_than_or_equal_to,
    skip_unless_package,
)

# ....................{ TESTS                             }....................
#FIXME: Remove the Python >= 3.10 skip *AFTER* Sphinx resolves this issue:
#    https://github.com/sphinx-doc/sphinx/issues/9820
@skip_if_python_version_greater_than_or_equal_to('3.10.0')
@skip_unless_package('sphinx')
def test_sphinx(tmp_path) -> None:
    '''
    Functional test testing this project's behaviour with respect to the
    third-party :mod:`sphinx` package by externally running that package
    against a minimal-length Sphinx document tree exercising all hopefully
    resolved edge cases.

    Parameters
    ----------
    tmp_path : pathlib.Path
        Abstract path encapsulating a temporary directory unique to this unit
        test, created in the base temporary directory.
    '''

    # Defer heavyweight imports.
    from beartype_test.util.os.command.pytcmdexit import is_success
    from beartype_test.util.path.pytpathtest import (
        get_test_func_data_lib_sphinx_dir)

    # Entry-point (i.e., pure-Python function accepting a list of zero or more
    # command-line arguments) underlying the external "sphinx-build" command.
    from sphinx.cmd.build import main as sphinx_build

    # List of all command-line options (i.e., "-"-prefixed strings) to be
    # effectively passed to the external "sphinx-build" command.
    #
    # Note this iterable *MUST* be defined as a list rather than tuple. If a
    # tuple, the function called below raises an exception. Hot garbage!
    SPHINX_OPTIONS = [
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
        #     WARNING: autodoc: failed to import module 'beartype_sphinx'; the following exception was raised:
        #     No module named 'beartype_sphinx'
        '-W',
    ]

    # List of all command-line arguments (i.e., non-options) to be effectively
    # passed to the external "sphinx-build" command.
    #
    # Note this iterable *MUST* be defined as a list rather than tuple. If a
    # tuple, the function called below raises an exception. Steaming trash!
    SPHINX_ARGUMENTS = [
        # Absolute or relative dirname of a test-specific subdirectory
        # containing a sample Sphinx structure exercising edge cases in the
        # @beartype decorator.
        str(get_test_func_data_lib_sphinx_dir()),
        # Absolute or relative dirname of a test-specific temporary directory
        # to which Sphinx will emit ignorable rendered documentation files.
        str(tmp_path),
    ]

    # Run "sphinx-build" to build documentation for this fake project.
    sphinx_build_exit_code = sphinx_build(SPHINX_OPTIONS + SPHINX_ARGUMENTS)

    # Assert that "sphinx-build" successfully builds documentation for this
    # fake project *WITHOUT* raising an exception.
    assert is_success(sphinx_build_exit_code), (
        f'"sphinx-build" exit code {sphinx_build_exit_code} != 0.')
