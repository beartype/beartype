#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :mod:`functools` utility unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.api.standard.utilfunctools` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_is_func_functools_lru_cache() -> None:
    '''
    Test the
    :func:`beartype._util.api.standard.utilfunctools.is_func_functools_lru_cache`
    tester.
    '''

    # Defer test-specific imports.
    from beartype._util.api.standard.utilfunctools import is_func_functools_lru_cache
    from beartype_test.a00_unit.data.data_type import (
        function_lru_cached,
        function,
    )

    # Assert this tester accepts a @functools.lru_cache-memoized callable.
    assert is_func_functools_lru_cache(function_lru_cached) is True

    # Assert this tester rejects a callable *NOT* decorated by that decorator.
    assert is_func_functools_lru_cache(function) is False

    # Assert this tester rejects a non-callable *WITHOUT* raising exceptions.
    assert is_func_functools_lru_cache(
        'With weeping flowers, or votive cypress wreath,') is False


def test_is_func_functools_partial() -> None:
    '''
    Test the
    :func:`beartype._util.api.standard.utilfunctools.is_func_functools_partial`
    tester.
    '''

    # Defer test-specific imports.
    from beartype._util.api.standard.utilfunctools import is_func_functools_partial
    from beartype_test.a00_unit.data.data_type import (
        function,
        function_partial,
    )

    # Assert this tester accepts a "functools.partial"-wrapped callable.
    assert is_func_functools_partial(function_partial) is True

    # Assert this tester rejects a callable *NOT* decorated by that decorator.
    assert is_func_functools_partial(function) is False

    # Assert this tester rejects a non-callable *WITHOUT* raising exceptions.
    assert is_func_functools_partial(
        'For well he knew that mighty Shadow loves') is False

# ....................{ TESTS ~ getter                     }....................
def test_get_func_functools_partial_args() -> None:
    '''
    Test the
    :func:`beartype._util.api.standard.utilfunctools.get_func_functools_partial_args`
    getter.
    '''

    # Defer test-specific imports.
    from beartype._util.api.standard.utilfunctools import (
        get_func_functools_partial_args)
    from beartype_test.a00_unit.data.data_type import (
        FUNCTION_PARTIALIZED_ARG_VALUE,
        FUNCTION_PARTIALIZED_KWARG_NAME,
        FUNCTION_PARTIALIZED_KWARG_VALUE,
        builtin_partial,
        function_partial,
    )

    # Assert this unwrapper returns the expected 2-tuple providing the
    # positional and keyword parameters passed to the C-based callable wrapped
    # by the "functools.partial" class.
    assert get_func_functools_partial_args(builtin_partial) == ((2,), {})

    # Assert this unwrapper returns the expected 2-tuple providing the
    # positional and keyword parameters passed to the pure-Python callable
    # wrapped by the "functools.partial" class.
    assert get_func_functools_partial_args(function_partial) == (
        (FUNCTION_PARTIALIZED_ARG_VALUE,),
        {FUNCTION_PARTIALIZED_KWARG_NAME: FUNCTION_PARTIALIZED_KWARG_VALUE},
    )

# ....................{ TESTS ~ tester                     }....................
def test_unwrap_func_functools_partial_once() -> None:
    '''
    Test the
    :func:`beartype._util.api.standard.utilfunctools.unwrap_func_functools_partial_once`
    unwrapper.
    '''

    # Defer test-specific imports.
    from beartype._util.api.standard.utilfunctools import (
        unwrap_func_functools_partial_once)
    from beartype_test.a00_unit.data.data_type import (
        builtin_partial,
        function_partialized,
        function_partial,
    )

    # Assert this unwrapper returns the expected C-based callable wrapped by
    # the "functools.partial" class.
    assert unwrap_func_functools_partial_once(builtin_partial) is divmod

    # Assert this unwrapper returns the expected pure-Python callable wrapped by
    # the "functools.partial" class.
    assert unwrap_func_functools_partial_once(function_partial) is (
        function_partialized)
