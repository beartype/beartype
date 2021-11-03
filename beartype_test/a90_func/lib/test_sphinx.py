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
    skip_if_python_version_less_than,
    skip_if_pypy,
    skip_unless_package,
)

# ....................{ TESTS                             }....................
#FIXME: Undocument once worky, please.
# @skip_unless_package('sphinx')
# def test_sphinx(tmp_path) -> None:
#     '''
#     Functional test testing this project's behaviour with respect to the
#     third-party :mod:`sphinx` package by externally running that package
#     against a minimal-length Sphinx document tree exercising all hopefully
#     resolved edge cases.
#
#     Parameters
#     ----------
#     tmp_path : pathlib.Path
#         Abstract path encapsulating a temporary directory unique to this unit
#         test, created in the base temporary directory.
#     '''
#
#     # Defer heavyweight imports.
#     from beartype_test.util.os.command.pytcmdexit import is_success
#     # from beartype_test.util.path.pytpathproject import (
#     #     get_project_mypy_config_file,
#     #     get_project_package_dir,
#     # )
#
#     # Entry-point (i.e., pure-Python function accepting a list of zero or more
#     # command-line arguments) underlying the external "sphinx-build" command.
#     from sphinx.cmd.build import main as sphinx_build
#
#     # List of all command-line options (i.e., "-"-prefixed strings) to be
#     # effectively passed to the external "sphinx-build" command.
#     #
#     # Note this iterable *MUST* be defined as a list rather than tuple. If a
#     # tuple, the function called below raises an exception. Hot garbage!
#     SPHINX_OPTIONS = [
#         # Enable the HTML mode, rendering HTML-specific documentation files.
#         # Although technically arbitrary, this is the typical default mode.
#         '-M', 'html',
#     ]
#
#     # List of all command-line arguments (i.e., non-options) to be effectively
#     # passed to the external "sphinx-build" command.
#     #
#     # Note this iterable *MUST* be defined as a list rather than tuple. If a
#     # tuple, the function called below raises an exception. Steaming trash!
#     SPHINX_ARGUMENTS = [
#         # Absolute dirname of this project's top-level package.
#         str(get_project_package_dir()),
#         # Absolute dirname of a test-specific temporary directory to which
#         # Sphinx will emit ignorable rendered documentation files.
#         str(tmp_path),
#     ]
#
#     # Assert that "sphinx-build" successfully builds documentation for this
#     # fake project *WITHOUT* raising an exception.
#     assert is_success(sphinx_build(SPHINX_OPTIONS + SPHINX_ARGUMENTS))
