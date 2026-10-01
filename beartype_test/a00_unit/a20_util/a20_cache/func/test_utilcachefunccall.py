#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable caching utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.cache.func.utilcachefunc` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_callable_cached() -> None:
    '''
    Test the
    :func:`beartype._util.cache.func.utilcachefunc.callable_cached`
    decorator.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype._util.cache.func.utilcachefunc import callable_cached
    from pytest import raises

    # ..................{ CALLABLES                          }..................
    @callable_cached
    def still_i_rise(bitter, twisted, lies):
        '''
        Arbitrary non-variadic callable memoized by this decorator.
        '''

        # If an arbitrary condition, raise an exception whose value depends on
        # these parameters to exercise this decorator's conditional caching of
        # exceptions.
        if len(lies) == 6:
            raise ValueError(lies)

        # Else, return a value depending on these parameters to exercise this
        # decorator's conditional caching of return values.
        return bitter + twisted + lies


    @callable_cached
    def from_savage_men(with_his, sweet_voice = ('and, eyes',), *args):
        '''
        Arbitrary variadic callable memoized by this decorator.
        '''

        # If an arbitrary condition, raise an exception whose value depends on
        # these parameters to exercise this decorator's conditional caching of
        # exceptions.
        if len(args) == 6:
            raise ValueError(lies)

        # Else, return a value depending on these parameters to exercise this
        # decorator's conditional caching of return values.
        return with_his + sweet_voice + args

    # ..................{ LOCALS                             }..................
    # Hashable objects to be passed as parameters below.
    bitter  = ('You', 'may', 'write', 'me', 'down', 'in', 'history',)
    twisted = ('With', 'your', 'bitter,', 'twisted,', 'lies.',)
    lies    = ('You', 'may', 'trod,', 'me,', 'in', 'the', 'very', 'dirt',)
    dust    = ('But', 'still,', 'like', 'dust,', "I'll", 'rise',)

    # ..................{ PASS ~ non-variadic                }..................
    # Test the non-variadic function defined above.

    # Assert that memoizing two calls passed the same positional arguments
    # caches and returns the same value.
    assert (
        still_i_rise(bitter, twisted, lies) is
        still_i_rise(bitter, twisted, lies))

    # Assert that memoizing a call expected to raise an exception does so.
    with raises(ValueError) as exception_first_info:
        still_i_rise(bitter, twisted, dust)

    # Assert that repeating that call reraises the same exception.
    with raises(ValueError) as exception_next_info:
        still_i_rise(bitter, twisted, dust)
    assert exception_first_info.value is exception_next_info.value

    # Assert that passing one or more unhashable parameters to this callable
    # succeeds with the expected return value.
    assert still_i_rise(
        ['Just', 'like', 'moons',],
        ['and', 'like', 'suns',],
        ['With the certainty of tides',],
    ) == [
        'Just', 'like', 'moons',
        'and', 'like', 'suns',
        'With the certainty of tides',
    ]

    # ..................{ PASS ~ non-variadic                }..................
    # Test the variadic function defined above.

    # Assert that memoizing two calls passed *NO* optional or variadic
    # positional arguments caches and returns the same value.
    assert from_savage_men(bitter) is from_savage_men(bitter)

    # Assert that memoizing two calls passed optional positional arguments but
    # *NO* variadic positional arguments caches and returns the same value.
    assert from_savage_men(bitter, twisted) is from_savage_men(bitter, twisted)

    # Assert that memoizing two calls passed the same positional arguments
    # caches and returns the same value.
    assert (
        from_savage_men(bitter, twisted, *lies) is
        from_savage_men(bitter, twisted, *lies))


def test_property_cached() -> None:
    '''
    Test the
    :func:`beartype._util.cache.func.utilcachefunc.property_cached` decorator.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype._util.cache.func.utilcacheproperty import property_cached

    # ..................{ CLASSES                            }..................
    class Keeper(object):
        '''
        Arbitrary class defining the property to be cached.
        '''

        def __init__(self, keys: int) -> None:
            self.keys = keys


        @property
        @property_cached
        def keys_cached(self) -> int:
            # Property value to be both cached and returned.
            keys_cached = self.keys * 2

            # To detect erroneous attempts to call this property method multiple
            # times for the same object, modify the object variable from which
            # this property value derived in a predictable way on each call of
            # this property method.
            self.keys /= 2

            # Return this property value.
            return keys_cached

    # ..................{ LOCALS                             }..................
    # Value of the "Keeper.keys" attribute *BEFORE* invoking keys_cached().
    KEY_COUNT_PRECACHED = 7

    # Value of the "Keeper.keys" attribute *AFTER* invoking keys_cached().
    KEY_COUNT_POSTCACHED = KEY_COUNT_PRECACHED / 2

    # Value of the "Keeper.keys_cached" property.
    KEY_COUNT_CACHED = KEY_COUNT_PRECACHED * 2

    # Instance of this class initialized with this value.
    i_want_out = Keeper(keys=KEY_COUNT_PRECACHED)

    # ..................{ PASS                               }..................
    # Assert this attribute to be as initialized.
    assert i_want_out.keys == KEY_COUNT_PRECACHED

    # Assert this property to be as cached.
    assert i_want_out.keys_cached == KEY_COUNT_CACHED

    # Assert this attribute to have been modified by this property call.
    assert i_want_out.keys == KEY_COUNT_POSTCACHED

    # Assert this property to still be as cached.
    assert i_want_out.keys_cached == KEY_COUNT_CACHED

    # Assert this attribute to *NOT* have been modified again, validating that
    # the prior property access returned the previously cached value rather than
    # recalling this property method.
    assert i_want_out.keys == KEY_COUNT_POSTCACHED
