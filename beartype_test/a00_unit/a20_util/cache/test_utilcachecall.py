#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype callable caching utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.cache.utilcachecall` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype.roar._roarwarn import _BeartypeUtilCallableCachedKwargsWarning
from beartype_test.util.mark.pytmark import ignore_warnings
from pytest import raises

# ....................{ TESTS                             }....................
# Prevent pytest from capturing and displaying all expected non-fatal
# beartype-specific warnings emitted by the @callable_cached decorator.
@ignore_warnings(_BeartypeUtilCallableCachedKwargsWarning)
def test_callable_cached_pass() -> None:
    '''
    Test successful usage of the
    :func:`beartype._util.cache.utilcachecall.callable_cached` decorator.
    '''

    # Defer heavyweight imports.
    from beartype._util.cache.utilcachecall import callable_cached

    # Callable memoized by this decorator.
    @callable_cached
    def still_i_rise(bitter, twisted, lies):
        # If an arbitrary condition, raise an exception whose value depends on
        # these parameters to exercise this decorator's conditional caching of
        # exceptions.
        if len(lies) == 6:
            raise ValueError(lies)

        # Else, return a value depending on these parameters to exercise this
        # decorator's conditional caching of return values.
        return bitter + twisted + lies

    # Objects to be passed as parameters below.
    bitter  = ('You', 'may', 'write', 'me', 'down', 'in', 'history',)
    twisted = ('With', 'your', 'bitter,', 'twisted,', 'lies.',)
    lies    = ('You', 'may', 'trod,', 'me,', 'in', 'the', 'very', 'dirt',)
    dust    = ('But', 'still,', 'like', 'dust,', "I'll", 'rise',)

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

    # Assert that memoizing a call expected to raise an exception does so.
    with raises(ValueError) as exception_first_info:
        still_i_rise(bitter, twisted, dust)

    # Assert that repeating that call reraises the same exception.
    with raises(ValueError) as exception_next_info:
        still_i_rise(bitter, twisted, dust)
        assert exception_first_info is exception_next_info

    # Assert that memoizing two calls passed the same keyword arguments in a
    # differing order cache and return differing values.
    assert (
       still_i_rise(bitter=bitter, twisted=twisted, lies=lies) is not
       still_i_rise(twisted=twisted, lies=lies, bitter=bitter))

    # Assert that passing one or more unhashable parameters to this callable
    # succeeds with the expected return value.
    assert still_i_rise(
        ('Just', 'like', 'moons',),
        ('and', 'like', 'suns',),
        ('With the certainty of tides',),
    ) == (
        'Just', 'like', 'moons',
        'and', 'like', 'suns',
        'With the certainty of tides',
    )


def test_callable_cached_fail() -> None:
    '''
    Test unsuccessful usage of the
    :func:`beartype._util.cache.utilcachecall.callable_cached` decorator.
    '''

    # Defer heavyweight imports.
    from beartype._util.cache.utilcachecall import callable_cached
    from beartype.roar._roarexc import _BeartypeUtilCallableCachedException

    # Assert that attempting to memoize a callable accepting one or more
    # variadic positional parameters fails with the expected exception.
    with raises(_BeartypeUtilCallableCachedException):
        @callable_cached
        def see_me_broken(*args):
            return args

    # Assert that attempting to memoize a callable accepting one or more
    # variadic keyword parameters fails with the expected exception.
    with raises(_BeartypeUtilCallableCachedException):
        @callable_cached
        def my_soulful_cries(**kwargs):
            return kwargs
