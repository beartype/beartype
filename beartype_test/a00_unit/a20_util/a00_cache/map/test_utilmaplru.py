#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

"""
Project-wide **Least Recently Used (LRU) cache** utility unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.cache.map.utilmaplru` submodule.
"""

# ....................{ IMPORTS                           }....................
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises
from beartype.roar._roarexc import _BeartypeUtilCacheLruException

# ....................{ TESTS                             }....................
def test_lrucachestrong_one_pass() -> None:
    """
    Test successful usage of the
    :func:`beartype._util.cache.map.utilmaplru.CacheLruStrong` class against an
    LRU cache caching at most one key-value pair.
    """

    # Defer test-specific imports.
    from beartype._util.cache.map.utilmaplru import CacheLruStrong

    # Arbitrary key-value pair.
    LRU_CACHE_KEY_A = 'KEY_A'
    LRU_CACHE_VALUE_A = 'VALUE_A'

    # Another arbitrary key-value pair.
    LRU_CACHE_KEY_B = 'KEY_B'
    LRU_CACHE_VALUE_B = 'VALUE_B'

    lru_cache = CacheLruStrong(size=1)
    assert len(lru_cache) == 0

    # Cache and confirm the first and only key-value pair of this cache is this
    # pair.
    lru_cache[LRU_CACHE_KEY_A] = LRU_CACHE_VALUE_A
    assert len(lru_cache) == 1
    assert lru_cache[LRU_CACHE_KEY_A] == LRU_CACHE_VALUE_A

    # Test the implicit enforcement of cache size
    lru_cache[LRU_CACHE_KEY_B] = LRU_CACHE_VALUE_B
    assert len(lru_cache) == 1
    assert lru_cache[LRU_CACHE_KEY_B] == LRU_CACHE_VALUE_B

    del lru_cache[LRU_CACHE_KEY_B]
    assert len(lru_cache) == 0


def test_lrucachestrong_two_pass() -> None:
    """
    Test successful usage of the
    :func:`beartype._util.cache.map.utilmaplru.CacheLruStrong` class against an
    LRU cache caching at most two key-value pairs.
    """

    # Defer test-specific imports.
    from beartype._util.cache.map.utilmaplru import CacheLruStrong

    # Arbitrary key-value pair.
    LRU_CACHE_KEY_A = 'KEY_A'
    LRU_CACHE_VALUE_A = 'VALUE_A'
    LRU_CACHE_ITEM_A = (LRU_CACHE_KEY_A, LRU_CACHE_VALUE_A)

    # Another arbitrary key-value pair.
    LRU_CACHE_KEY_B = 'KEY_B'
    LRU_CACHE_VALUE_B = 'VALUE_B'
    LRU_CACHE_ITEM_B = (LRU_CACHE_KEY_B, LRU_CACHE_VALUE_B)

    # Another arbitrary key-value pair.
    LRU_CACHE_KEY_C = 'KEY_C'
    LRU_CACHE_VALUE_C = 'VALUE_C'
    LRU_CACHE_ITEM_C = (LRU_CACHE_KEY_C, LRU_CACHE_VALUE_C)

    lru_cache = CacheLruStrong(size=2)

    # Cache two arbitrary key-value pairs and confirm they've been cached in
    # insertion order.
    lru_cache[LRU_CACHE_KEY_A] = LRU_CACHE_VALUE_A
    lru_cache[LRU_CACHE_KEY_B] = LRU_CACHE_VALUE_B
    lru_cache_items = iter(lru_cache.items())
    assert len(lru_cache) == 2
    assert next(lru_cache_items) == LRU_CACHE_ITEM_A
    assert next(lru_cache_items) == LRU_CACHE_ITEM_B

    # Confirm __getitem__ resets the key in the cache.
    assert lru_cache[LRU_CACHE_KEY_A] == LRU_CACHE_VALUE_A
    lru_cache_items = iter(lru_cache.items())
    assert len(lru_cache) == 2
    assert next(lru_cache_items) == LRU_CACHE_ITEM_B
    assert next(lru_cache_items) == LRU_CACHE_ITEM_A

    # Confirm __contains__ resets the key in the cache.
    assert LRU_CACHE_KEY_B in lru_cache
    lru_cache_items = iter(lru_cache.items())
    assert next(lru_cache_items) == LRU_CACHE_ITEM_A
    assert next(lru_cache_items) == LRU_CACHE_ITEM_B

    # Confirm the implicit enforcement of cache size
    lru_cache[LRU_CACHE_KEY_C] = LRU_CACHE_VALUE_C
    assert len(lru_cache) == 2
    assert LRU_CACHE_KEY_A not in lru_cache

    # Confirm the remaining key-value pairs have been cached in insertion
    # order.
    lru_cache_items = iter(lru_cache.items())
    assert next(lru_cache_items) == LRU_CACHE_ITEM_B
    assert next(lru_cache_items) == LRU_CACHE_ITEM_C

    # Confirm __setitem__ resets a cached key.
    lru_cache[LRU_CACHE_KEY_B] = LRU_CACHE_VALUE_B
    lru_cache_items = iter(lru_cache.items())
    assert next(lru_cache_items) == LRU_CACHE_ITEM_C
    assert next(lru_cache_items) == LRU_CACHE_ITEM_B


def test_lrucachestrong_fail() -> None:
    """
    Test unsuccessful usage of the
    :func:`beartype._util.cache.map.utilmaplru.CacheLruStrong` class.
    """

    # Defer test-specific imports.
    from beartype._util.cache.map.utilmaplru import CacheLruStrong

    # Confirm behaviour for a non-integer size.
    with raises(_BeartypeUtilCacheLruException):
        CacheLruStrong(size="Wait a minute, I'm not an int!")

    # Confirm behaviour for a non-positive size.
    with raises(_BeartypeUtilCacheLruException):
        CacheLruStrong(size=0)
