#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2021 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Project-wide functional static type-checker tests.**

This submodule functionally tests the this project's compliance with
third-party static type-checkers and hence `PEP 561`_.

.. _PEP 561:
    https://www.python.org/dev/peps/pep-0561
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.mark.pytskip import skip_if_pypy, skip_unless_package

# ....................{ TESTS                             }....................
#FIXME: Consider submitting as a StackOverflow post. Dis iz l33t, yo!

# If the third-party "mypy" package satisfying this minimum version is
# unavailable, skip this test. Note that:
#
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

# If the active Python interpreter is PyPy, avoid this mypy-specific functional
# test. mypy is currently incompatible with PyPy for inscrutable reasons that
# should presumably be fixed at some future point. See also:
#     https://mypy.readthedocs.io/en/stable/faq.html#does-it-run-on-pypy
@skip_unless_package('mypy')
@skip_if_pypy()
def test_pep561_mypy() -> None:
    '''
    Functional test testing this project's compliance with `PEP 561`_ by
    externally running MyPy_, the most popular third-party static type checker
    as of this test, against this project's top-level package.

    .. _PEP 561:
        https://www.python.org/dev/peps/pep-0561
    '''

    # Defer heavyweight imports.
    from beartype_test.util.os.command.pytcmdexit import is_success
    from beartype_test.util.path.pytpathproject import get_project_package_dir
    from mypy import api

    # List of all command-line options (i.e., "-"-prefixed strings) to be
    # effectively passed to the external "mypy" command.
    #
    # Note this iterable *MUST* be defined as a list rather than type. If *NOT*
    # the case, the function called below raises an exception. Hot garbage!
    MYPY_OPTIONS = []

    # List of all command-line arguments (i.e., non-options) to be effectively
    # passed to the external "mypy" command.
    #
    # Note this iterable *MUST* be defined as a list rather than type. If *NOT*
    # the case, the function called below raises an exception. Hot garbage!
    MYPY_ARGUMENTS = [
        # Absolute dirname of this project's top-level package.
        str(get_project_package_dir()),
    ]

    # Tuple of all command-line options to be effectively passed to the
    # external "mypy" command.
    _, mypy_stderr, mypy_status = api.run(MYPY_OPTIONS + MYPY_ARGUMENTS)

    # Assert "mypy" to have emitted *NO* warnings or errors.
    assert not mypy_stderr

    # Assert "mypy" to have exited with success.
    assert is_success(mypy_status)
