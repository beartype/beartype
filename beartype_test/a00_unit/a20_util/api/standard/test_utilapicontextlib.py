#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :mod:`contextlib` utility unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.api.standard.utilcontextlib` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ getter                     }....................
def test_get_func_contextlib_contextmanager_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.api.standard.utilcontextlib.get_func_contextlib_contextmanager_or_none`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.api.standard.utilcontextlib import (
        get_func_contextlib_contextmanager_or_none)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11
    from beartype_test.a00_unit.data.data_type import (
        async_context_manager_factory,
        context_manager_factory,
        decorator_isomorphic,
        decorator_nonisomorphic,
        function,
    )
    from contextlib import (
        asynccontextmanager,
        contextmanager,
    )

    # ....................{ PASS                           }....................
    # Assert this getter either accepts or rejects isomorphic closures created
    # and returned by @contextlib decorators conditionally depending on whether
    # the active Python interpreter targets Python >= 3.11 or not.
    if IS_PYTHON_AT_LEAST_3_11:
        assert get_func_contextlib_contextmanager_or_none(
            async_context_manager_factory) is asynccontextmanager
        assert get_func_contextlib_contextmanager_or_none(
            context_manager_factory) is contextmanager
    else:
        assert get_func_contextlib_contextmanager_or_none(
            async_context_manager_factory) is None
        assert get_func_contextlib_contextmanager_or_none(
            context_manager_factory) is None

    # ....................{ FAIL                           }....................
    # Assert this getter rejects isomorphic closures *NOT* created and returned
    # by the @contextlib.contextmanager decorator.
    assert get_func_contextlib_contextmanager_or_none(
        decorator_isomorphic(function)) is None

    # Assert this getter rejects non-isomorphic closures.
    assert get_func_contextlib_contextmanager_or_none(
        decorator_nonisomorphic(function)) is None

    # Assert this getter rejects non-closure callables.
    assert get_func_contextlib_contextmanager_or_none(function) is None

    # Assert this getter rejects non-callables.
    assert get_func_contextlib_contextmanager_or_none(
        'A lovely youth,—no mourning maiden decked') is None
