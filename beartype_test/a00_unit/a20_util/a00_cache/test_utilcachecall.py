#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype callable caching utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.cache.utilcachecall` submodule.
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
    :func:`beartype._util.cache.utilcachecall.callable_cached` decorator.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableCachedException
    from beartype._util.cache.utilcachecall import callable_cached
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


def test_method_cached_arg_by_id() -> None:
    '''
    Test the
    :func:`beartype._util.cache.utilcachecall.method_cached_arg_by_id`
    decorator.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableCachedException
    from beartype._util.cache.utilcachecall import method_cached_arg_by_id
    from pytest import raises

    # ..................{ CLASSES                            }..................
    class LikeDust(object):
        '''
        Arbitrary class containing an arbitrary callable memoized by this
        decorator.
        '''

        @method_cached_arg_by_id
        def just_like_moons(self, and_like_suns):
            '''
            Arbitrary callable memoized by this decorator.
            '''

            # If an arbitrary condition, raise an exception whose value depends
            # on these parameters to exercise this decorator's conditional
            # caching of exceptions.
            if len(and_like_suns) == 6:
                raise ValueError(and_like_suns)

            # Else, return a value depending on these parameters to exercise
            # this decorator's conditional caching of return values.
            return [id(self), and_like_suns]

    # ..................{ LOCALS                             }..................
    # Instance of this class.
    like_air = LikeDust()

    # Hashable objects to be passed as parameters below.
    moons = ('Just', 'like', 'moons', 'and', 'like', 'suns,')
    tides = ('With', 'the', 'certainty,', 'of,', 'tides,',)

    # Shallow copies of hashable objects defined above.
    #
    # Note that copying a list in a manner guaranteeing even a shallow copy is
    # surprisingly non-trivial. See this relevant StackOverflow answer:
    #     https://stackoverflow.com/a/15214661/2809027
    tides_copy = tuple(list(tides))

    # Unhashable objects to be passed as parameters below.
    hopes = ['Just', 'like', 'hopes,', 'springing,', 'high',]

    # ..................{ PASS                               }..................
    # Assert that memoizing two calls passed the same positional arguments
    # caches and returns the same value.
    assert (
        like_air.just_like_moons(tides) is
        like_air.just_like_moons(tides))

    # Assert that memoizing two calls passed a copy of the above arguments
    # caches and returns a different value.
    assert (
        like_air.just_like_moons(tides_copy) is not
        like_air.just_like_moons(tides))

    # Assert that memoizing a call expected to raise an exception does so.
    with raises(ValueError) as exception_first_info:
        like_air.just_like_moons(moons)

    # Assert that repeating that call reraises the same exception.
    with raises(ValueError) as exception_next_info:
        like_air.just_like_moons(moons)
    assert exception_first_info.value is exception_next_info.value

    # Assert that passing one or more unhashable parameters to this callable
    # succeeds with the expected return value.
    assert like_air.just_like_moons(hopes) == [id(like_air), hopes]

    # ..................{ FAIL                               }..................
    # Assert that attempting to memoize a callable accepting *NO* parameters
    # fails with the expected exception.
    with raises(_BeartypeUtilCallableCachedException):
        @method_cached_arg_by_id
        def into_a_daybreak_thats_wondrously_clear():
            return 0

    # Assert that attempting to memoize a callable accepting one or more
    # variadic positional parameters fails with the expected exception.
    with raises(_BeartypeUtilCallableCachedException):
        @method_cached_arg_by_id
        def leaving_behind_nights_of_terror_and_fear(*args):
            return args


def test_property_cached() -> None:
    '''
    Test the
    :func:`beartype._util.cache.utilcachecall.property_cached` decorator.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype._util.cache.utilcachecall import property_cached

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
