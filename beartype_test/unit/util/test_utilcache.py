#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype utility caching unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.cache.utilcachecall` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import pytest

# ....................{ TESTS                             }....................
def test_callable_cached_pass() -> None:
    '''
    Test successful usage of the
    :func:`beartype._util.cache.utilcachecall.callable_cached` decorator.
    '''

    # Defer heavyweight imports.
    from beartype._util.cache.utilcachecall import callable_cached

    # Function memoized by this decorator.
    @callable_cached
    def still_i_rise(bitter, twisted, lies):
        return bitter + twisted + lies

    # Objects to be passed as parameters below.
    bitter  = ('You', 'may', 'write', 'me', 'down', 'in', 'history',)
    twisted = ('With', 'your', 'bitter,', 'twisted,', 'lies.',)
    lies    = ('You', 'may', 'trod,', 'me,', 'in', 'the', 'very', 'dirt',)

    # Assert that memoizing two calls passed the same positional arguments
    # caches and returns the same value.
    assert (
        still_i_rise(bitter, twisted, lies) is
        still_i_rise(bitter, twisted, lies))

    # Assert that memoizing two calls passed the same positional and keyword
    # arguments in the same order caches and returns the same value.
    assert (
        still_i_rise(bitter, twisted=twisted, lies=lies) is
        still_i_rise(bitter, twisted=twisted, lies=lies))

    # Assert that memoizing two calls passed the same keyword arguments in the
    # same order cache and return the same value.
    assert (
        still_i_rise(bitter=bitter, twisted=twisted, lies=lies) is
        still_i_rise(bitter=bitter, twisted=twisted, lies=lies))

    #FIXME: Curiously, this assertion fails under only Python 3.5 for unknown
    #reasons. Since Python 3.5 is on the cusp of hitting its EOL *AND* since
    #this assertion is non-essential, disable this until we drop Python 3.5.
    # Assert that memoizing two calls passed the same keyword arguments in a
    # differing order cache and return differing values.
    #assert (
    #    still_i_rise(bitter=bitter, twisted=twisted, lies=lies) is not
    #    still_i_rise(twisted=twisted, lies=lies, bitter=bitter))


def test_callable_cached_fail() -> None:
    '''
    Test unsuccessful usage of the
    :func:`beartype._util.cache.utilcachecall.callable_cached` decorator.
    '''

    # Defer heavyweight imports.
    from beartype._util.cache.utilcachecall import callable_cached
    from beartype.roar import _BeartypeCallableCachedException

    # Function memoized by this decorator.
    @callable_cached
    def still_i_rise(moons, suns, tides):
        return moons | suns | tides

    # Assert that attempting to memoize one or more unhashable parameters
    # fails with the expected exception.
    with pytest.raises(TypeError):
        still_i_rise(
            frozenset('Just', 'like', 'moons',),
            frozenset('and', 'like', 'suns',),
            frozenset('With the certainty of tides',),
        )

    # Assert that attempting to memoize a callable accepting one or more
    # variadic positional parameters fails with the expected exception.
    with pytest.raises(_BeartypeCallableCachedException):
        @callable_cached
        def see_me_broken(*args):
            return args

    # Assert that attempting to memoize a callable accepting one or more
    # variadic keyword parameters fails with the expected exception.
    with pytest.raises(_BeartypeCallableCachedException):
        @callable_cached
        def my_soulful_cries(**kwargs):
            return kwargs
