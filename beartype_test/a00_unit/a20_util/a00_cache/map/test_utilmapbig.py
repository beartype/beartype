#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

"""
Project-wide **unbounded cache** utility unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.cache.map.utilmapbig` submodule.
"""

# ....................{ IMPORTS                            }....................
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_cacheunboundedstrong() -> None:
    """
    Test successful usage of the
    :class:`beartype._util.cache.map.utilmapbig.CacheUnboundedStrong` class.
    """

    # Defer test-specific imports.
    from beartype._util.cache.map.utilmapbig import CacheUnboundedStrong

    # Initially empty unbounded cache.
    cache_unbounded = CacheUnboundedStrong()

    # Arbitrary key-value pairs.
    KEY_A =   'My own, my human mind, which passively'
    VALUE_A = 'Now renders and receives fast influencings,'
    KEY_B =   'Holding an unremitting interchange'
    VALUE_B = 'With the clear universe of things around;'

    def value_factory(key) -> object:
        '''
        Arbitrary function accepting an arbitrary key and dynamically returning
        the value to be associated with this key.
        '''

        # Trivially return the hash of this key.
        return hash(key)

    # Assert that statically getting an uncached key returns the passed value
    # (i.e., caches that key with that value).
    assert cache_unbounded.cache_or_get_cached_value(
        key=KEY_A, value=VALUE_A) is VALUE_A

    # Assert that statically getting a cached key returns the previously
    # (rather than currently) passed value.
    assert cache_unbounded.cache_or_get_cached_value(
        key=KEY_A, value=VALUE_B) is VALUE_A

    # Assert that dynamically getting a cached key returns the previously
    # passed value rather than a value returned by the passed value factory.
    assert cache_unbounded.cache_or_get_cached_func_return_passed_arg(
        key=KEY_A, value_factory=value_factory, arg=KEY_A) is VALUE_A

    # Assert that dynamically getting an uncached key returns the value
    # returned by the passed value factory (i.e., caches that key with that
    # value).
    assert cache_unbounded.cache_or_get_cached_func_return_passed_arg(
        key=KEY_B, value_factory=value_factory, arg=KEY_B) == hash(KEY_B)
