#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype Least Recently Used (LRU) caching utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.cache.utilcachelru` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ TESTS                             }....................
def test_lrucachestrong_one_pass() -> None:
    '''
    Test successful usage of the
    :func:`beartype._util.cache.utilcachelru.LRUCacheStrong` class against an
    LRU cache caching at most one key-value pair.
    '''

    # Defer heavyweight imports.
    from beartype._util.cache.utilcachelru import LRUCacheStrong
    from beartype.roar import _BeartypeUtilLRUCacheException

    # Arbitrary key-value pair.
    LRU_CACHE_KEY_A =   'There will be time, there will be time'
    LRU_CACHE_VALUE_A = 'To prepare a face to meet the faces that you meet;'

    # Another arbitrary key-value pair.
    LRU_CACHE_KEY_B =   'There will be time to murder and create,'
    LRU_CACHE_VALUE_B = 'And time for all the works and days of hands'

    # LRU cache caching at most one key-value pair.
    lru_cache = LRUCacheStrong(size=1)

    # Assert this cache to be empty.
    assert len(lru_cache) == 0

    # Cache an arbitrary key-value pair.
    lru_cache[LRU_CACHE_KEY_A] = LRU_CACHE_VALUE_A

    # Assert the first and only key-value pair of this cache to be this pair.
    assert len(lru_cache) == 1
    assert lru_cache[LRU_CACHE_KEY_A] == LRU_CACHE_VALUE_A

    # Cache another arbitrary key-value pair.
    lru_cache[LRU_CACHE_KEY_B] = LRU_CACHE_VALUE_B

    # Assert the first and only key-value pair of this cache to be this pair.
    assert len(lru_cache) == 1
    assert lru_cache[LRU_CACHE_KEY_B] == LRU_CACHE_VALUE_B

    # Uncache this key-value pair.
    del lru_cache[LRU_CACHE_KEY_B]

    # Assert this cache to be empty.
    assert len(lru_cache) == 0


def test_lrucachestrong_two_pass() -> None:
    '''
    Test successful usage of the
    :func:`beartype._util.cache.utilcachelru.LRUCacheStrong` class against an
    LRU cache caching at most two key-value pairs.
    '''

    # Defer heavyweight imports.
    from beartype._util.cache.utilcachelru import LRUCacheStrong
    from beartype.roar import _BeartypeUtilLRUCacheException

    # Arbitrary key-value pair.
    LRU_CACHE_KEY_A =   'That lift and drop a question on your plate;'
    LRU_CACHE_VALUE_A = 'Time for you and time for me,'
    LRU_CACHE_ITEM_A = (LRU_CACHE_KEY_A, LRU_CACHE_VALUE_A)

    # Another arbitrary key-value pair.
    LRU_CACHE_KEY_B =   'And time yet for a hundred indecisions,'
    LRU_CACHE_VALUE_B = 'And for a hundred visions and revisions,'
    LRU_CACHE_ITEM_B = (LRU_CACHE_KEY_B, LRU_CACHE_VALUE_B)

    # Another arbitrary key-value pair.
    LRU_CACHE_KEY_C =   'Before the taking of a toast and tea.'
    LRU_CACHE_VALUE_C = 'In the room the women come and go'
    LRU_CACHE_ITEM_C = (LRU_CACHE_KEY_C, LRU_CACHE_VALUE_C)

    # LRU cache caching at most two key-value pairs.
    lru_cache = LRUCacheStrong(size=2)

    # Assert this cache to be empty.
    assert len(lru_cache) == 0

    # Cache an arbitrary key-value pair.
    lru_cache[LRU_CACHE_KEY_A] = LRU_CACHE_VALUE_A

    # Assert the first and only key-value pair of this cache to be this pair.
    assert len(lru_cache) == 1
    assert lru_cache[LRU_CACHE_KEY_A] == LRU_CACHE_VALUE_A

    # Cache another arbitrary key-value pair.
    lru_cache[LRU_CACHE_KEY_B] = LRU_CACHE_VALUE_B

    # Assert these key-value pairs to have been cached in insertion order.
    assert len(lru_cache) == 2
    lru_cache_items = iter(lru_cache.items())
    assert next(lru_cache_items) == LRU_CACHE_ITEM_A
    assert next(lru_cache_items) == LRU_CACHE_ITEM_B

    # Get the first key-value pair added above.
    assert lru_cache[LRU_CACHE_KEY_A] == LRU_CACHE_VALUE_A

    # Assert these key-value pairs to now be cached in the reverse order.
    assert len(lru_cache) == 2
    lru_cache_items = iter(lru_cache.items())
    assert next(lru_cache_items) == LRU_CACHE_ITEM_B
    assert next(lru_cache_items) == LRU_CACHE_ITEM_A

    # Assert the second key-value pair to still be cached.
    assert LRU_CACHE_KEY_B in lru_cache

    # Assert these key-value pairs to now be cached again in insertion order.
    assert len(lru_cache) == 2
    lru_cache_items = iter(lru_cache.items())
    assert next(lru_cache_items) == LRU_CACHE_ITEM_A
    assert next(lru_cache_items) == LRU_CACHE_ITEM_B

    # Cache another arbitrary key-value pair.
    lru_cache[LRU_CACHE_KEY_C] = LRU_CACHE_VALUE_C

    # Assert the first key-value pair to have been implicitly uncached.
    assert LRU_CACHE_KEY_A not in lru_cache

    # Assert the remaining key-value pairs to have been cached in insertion
    # order.
    assert len(lru_cache) == 2
    lru_cache_items = iter(lru_cache.items())
    assert next(lru_cache_items) == LRU_CACHE_ITEM_B
    assert next(lru_cache_items) == LRU_CACHE_ITEM_C


def test_lrucachestrong_fail() -> None:
    '''
    Test unsuccessful usage of the
    :func:`beartype._util.cache.utilcachelru.LRUCacheStrong` class.
    '''

    # Defer heavyweight imports.
    from beartype._util.cache.utilcachelru import LRUCacheStrong
    from beartype.roar import _BeartypeUtilLRUCacheException

    # Assert that attempting to initialize an LRU cache with a non-integer
    # capacity raises the expected exception.
    with raises(_BeartypeUtilLRUCacheException):
        LRUCacheStrong(size=(
            'And indeed there will be time'
            'For the yellow smoke that slides along the street,'
            'Rubbing its back upon the window-panes;'
        ))

    # Assert that attempting to initialize an LRU cache with a non-positive
    # capacity raises the expected exception.
    with raises(_BeartypeUtilLRUCacheException):
        LRUCacheStrong(size=0)
