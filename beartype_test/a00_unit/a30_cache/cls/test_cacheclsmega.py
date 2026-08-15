#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

"""
Project-wide **unbounded cache type hierarchy** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._cache.cls.cacheclsmega` submodule.
"""

# ....................{ IMPORTS                            }....................
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_cachemegastrongcaller() -> None:
    '''
    Test the :class:`beartype._cache.cls.cacheclsmega.CacheMegaStrongCaller`
    concrete subclass.
    '''

    # ....................{ IMPORTS                         }....................
    # Defer test-specific imports.
    from beartype._cache.cls.cacheclsmega import CacheMegaStrongCaller

    # ....................{ LOCALS                          }....................
    # Initially empty unbounded cache.
    cache_mega = CacheMegaStrongCaller()

    # Arbitrary key-value pairs.
    KEY_A =   'My own, my human mind, which passively'
    VALUE_A = 'Now renders and receives fast influencings,'
    KEY_B =   'Holding an unremitting interchange'
    VALUE_B = 'With the clear universe of things around;'

    # ....................{ CALLABLES                       }....................
    def value_factory(key) -> object:
        '''
        Arbitrary function accepting an arbitrary key and dynamically returning
        the value to be associated with this key.
        '''

        # Trivially return the hash of this key.
        return hash(key)

    # ....................{ __len__                        }....................
    # Assert that this cache is currently empty.
    assert len(cache_mega) == 0

    # ....................{ get_value_cached_or_cache      }....................
    # Assert that statically getting an uncached key returns the passed value
    # (i.e., caches that key with that value).
    assert cache_mega.get_value_cached_or_cache(
        key=KEY_A, value=VALUE_A) is VALUE_A

    # Assert that statically getting a cached key returns the previously
    # (rather than currently) passed value.
    assert cache_mega.get_value_cached_or_cache(
        key=KEY_A, value=VALUE_B) is VALUE_A

    # ....................{ cache_or_get_cached_func_return}....................
    # Assert that dynamically getting a cached key returns the previously
    # passed value rather than a value returned by the passed value factory.
    assert cache_mega.get_func_arg_return_cached_or_cache(
        key=KEY_A, value_factory=value_factory, arg=KEY_A) is VALUE_A

    # Assert that dynamically getting an uncached key returns the value
    # returned by the passed value factory (i.e., caches that key with that
    # value).
    assert cache_mega.get_func_arg_return_cached_or_cache(
        key=KEY_B, value_factory=value_factory, arg=KEY_B) == hash(KEY_B)

    # ....................{ clear_cache                    }....................
    # Assert that this cache is now non-empty.
    assert len(cache_mega) > 0

    # Remove all previously cached key-value pairs from this cache.
    cache_mega.clear_cache()

    # Assert that this cache has reverted back to being empty again.
    assert len(cache_mega) == 0


def test_cachemegastrongsubclassabc() -> None:
    '''
    Test the
    :class:`beartype._cache.cls.cacheclsmega.CacheMegaStrongSubclassABC`
    superclass.
    '''

    # ....................{ IMPORTS                         }....................
    # Defer test-specific imports.
    from beartype._cache.cls.cacheclsmega import CacheMegaStrongSubclassABC

    # ....................{ CLASSES                         }....................
    class ForwardHeStooped(CacheMegaStrongSubclassABC):
        def _make_value(
            self,

            # Subclass-specific variadic parameters passed from the parent
            # get_value_cached_or_cache() method.
            over_the: str,
            airy_shore: bytes,
        ) -> object:
            '''
            Arbitrary function accepting an arbitrary key and dynamically
            returning the value to be associated with this key.
            '''
            assert isinstance(over_the, str)
            assert isinstance(airy_shore, bytes)

            return over_the + airy_shore.decode('utf8')

    # ....................{ LOCALS                          }....................
    # Initially empty unbounded cache.
    cache_mega = ForwardHeStooped()

    # Arbitrary key-value pair.
    KEY_A =        "Forward he stoop'd over the airy shore,"
    OVER_THE_A =   "And plung'd all noiseless "
    AIRY_SHORE_A = b'into the deep night.'
    VALUE_A =      "And plung'd all noiseless into the deep night."

    # Yet another arbitrary key-value pair.
    KEY_B =        'Holding an unremitting interchange'
    OVER_THE_B =   'A thing of beauty is '
    AIRY_SHORE_B = b'a joy for ever:'
    VALUE_B =      'A thing of beauty is a joy for ever:'

    # ....................{ __len__                        }....................
    # Assert that this cache is currently empty.
    assert len(cache_mega) == 0

    # ....................{ get_value_cached_or_cache      }....................
    # Assert that getting an uncached key returns a new value created from the
    # passed parameters.
    assert cache_mega.get_value_cached_or_cache(
        key=KEY_A, over_the=OVER_THE_A, airy_shore=AIRY_SHORE_A) == VALUE_A

    # Assert that getting a cached key returns the value previously associated
    # with that key rather than a new value created from the passed parameters.
    assert cache_mega.get_value_cached_or_cache(
        key=KEY_A, over_the=OVER_THE_B, airy_shore=AIRY_SHORE_B) == VALUE_A

    # Assert that getting another uncached key returns yet another new value
    # created from the passed parameters.
    assert cache_mega.get_value_cached_or_cache(
        key=KEY_B, over_the=OVER_THE_B, airy_shore=AIRY_SHORE_B) == VALUE_B

    # Assert that getting another cached key returns the value previously
    # associated with that key rather than yet another new value created from
    # the passed parameters.
    assert cache_mega.get_value_cached_or_cache(
        key=KEY_B, over_the=OVER_THE_A, airy_shore=AIRY_SHORE_A) == VALUE_B

    # ....................{ clear_cache                    }....................
    # Assert that this cache is now non-empty.
    assert len(cache_mega) > 0

    # Remove all previously cached key-value pairs from this cache.
    cache_mega.clear_cache()

    # Assert that this cache has reverted back to being empty again.
    assert len(cache_mega) == 0
