#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :mod:`contextlib` utility unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.api.utilapicontextlib` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_is_func_contextlib_contextmanager() -> None:
    '''
    Test the
    :func:`beartype._util.api.utilapicontextlib.is_func_contextlib_contextmanager`
    tester.
    '''

    # Defer test-specific imports.
    from beartype._util.api.utilapicontextlib import (
        is_func_contextlib_contextmanager)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11
    from beartype_test.a00_unit.data.data_type import (
        context_manager_factory,
        decorator_isomorphic,
        decorator_nonisomorphic,
        function,
    )

    # Assert this tester either accepts or rejects isomorphic closures created
    # and returned by the @contextlib.contextmanager decorator conditionally
    # depending on whether the active Python interpreter targets Python >= 3.11
    # or not.
    assert is_func_contextlib_contextmanager(context_manager_factory) is (
        IS_PYTHON_AT_LEAST_3_11)

    # Assert this tester rejects isomorphic closures *NOT* created and returned
    # by the @contextlib.contextmanager decorator.
    assert is_func_contextlib_contextmanager(
        decorator_isomorphic(function)) is False

    # Assert this tester rejects non-isomorphic closures.
    assert is_func_contextlib_contextmanager(
        decorator_nonisomorphic(function)) is False

    # Assert this tester rejects non-closure callables.
    assert is_func_contextlib_contextmanager(function) is False

    # Assert this tester rejects non-callables.
    assert is_func_contextlib_contextmanager(
        'A lovely youth,—no mourning maiden decked') is False
