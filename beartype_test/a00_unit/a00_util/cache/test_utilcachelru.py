#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2021 by Cecil Curry.
# See "LICENSE" for further details.

"""
**Beartype Least Recently Used (LRU) caching utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.cache.utilcachelru` submodule.
"""

# ....................{ IMPORTS                           }....................
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises
from beartype.roar import _BeartypeUtilLRUCacheException


# ....................{ TESTS                             }....................
def test_lrucachestrong_one_pass() -> None:
    """
    Test successful usage of the
    :func:`beartype._util.cache.utilcachelru.LRUCacheStrong` class against an
    LRU cache caching at most one key-value pair.
    """

    # Defer heavyweight imports.
    from beartype._util.cache.utilcachelru import LRUCacheStrong

    # Arbitrary key-value pair.
    LRU_CACHE_KEY_A = 'KEY_A'
    LRU_CACHE_VALUE_A = 'VALUE_A'

    # Another arbitrary key-value pair.
    LRU_CACHE_KEY_B = 'KEY_B'
    LRU_CACHE_VALUE_B = 'VALUE_B'

    lru_cache = LRUCacheStrong(size=1)
    assert len(lru_cache) == 0

    # Cache and confirm the first and only key-value pair of this cache is this pair.
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
    :func:`beartype._util.cache.utilcachelru.LRUCacheStrong` class against an
    LRU cache caching at most two key-value pairs.
    """

    # Defer heavyweight imports.
    from beartype._util.cache.utilcachelru import LRUCacheStrong

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

    lru_cache = LRUCacheStrong(size=2)

    # Cache two arbitrary key-value pairs and confirm they've been cached in insertion order.
    lru_cache[LRU_CACHE_KEY_A] = LRU_CACHE_VALUE_A
    lru_cache[LRU_CACHE_KEY_B] = LRU_CACHE_VALUE_B
    lru_cache_items = iter(lru_cache.items())
    assert len(lru_cache) == 2
    assert next(lru_cache_items) == LRU_CACHE_ITEM_A
    assert next(lru_cache_items) == LRU_CACHE_ITEM_B

    # Confirm __getitem__ resets the key in the cache.
    # (These key-value pairs should be cached in reverse order.)
    assert lru_cache[LRU_CACHE_KEY_A] == LRU_CACHE_VALUE_A
    lru_cache_items = iter(lru_cache.items())

    assert len(lru_cache) == 2
    assert next(lru_cache_items) == LRU_CACHE_ITEM_B
    assert next(lru_cache_items) == LRU_CACHE_ITEM_A

    # Confirm __contains__ resets the key in the cache.
    # (These key-value pairs should be cached in their original order.)
    assert LRU_CACHE_KEY_B in lru_cache
    lru_cache_items = iter(lru_cache.items())

    assert len(lru_cache) == 2
    assert next(lru_cache_items) == LRU_CACHE_ITEM_A
    assert next(lru_cache_items) == LRU_CACHE_ITEM_B

    # Confirm the implicit enforcement of cache size
    lru_cache[LRU_CACHE_KEY_C] = LRU_CACHE_VALUE_C
    assert LRU_CACHE_KEY_A not in lru_cache
    assert len(lru_cache) == 2

    # Confirm the remaining key-value pairs have been cached in insertion order.
    lru_cache_items = iter(lru_cache.items())
    assert next(lru_cache_items) == LRU_CACHE_ITEM_B
    assert next(lru_cache_items) == LRU_CACHE_ITEM_C

    # Confirm __setitem__ resets the key in the cache.
    lru_cache[LRU_CACHE_KEY_B] = LRU_CACHE_VALUE_B
    lru_cache_items = iter(lru_cache.items())
    assert next(lru_cache_items) == LRU_CACHE_ITEM_C
    assert next(lru_cache_items) == LRU_CACHE_ITEM_B



def test_lrucachestrong_fail() -> None:
    """
    Test unsuccessful usage of the
    :func:`beartype._util.cache.utilcachelru.LRUCacheStrong` class.
    """

    # Defer heavyweight imports.
    from beartype._util.cache.utilcachelru import LRUCacheStrong

    # Confirm behaviour for a non-integer size.
    with raises(_BeartypeUtilLRUCacheException):
        LRUCacheStrong(size="Wait a minute, I'm not an int!")

    # Confirm behaviour for a non-positive size.
    with raises(_BeartypeUtilLRUCacheException):
        LRUCacheStrong(size=0)
