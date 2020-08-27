#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype exception caching utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.cache.utilcacheerror` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises
from random import getrandbits

# ....................{ CLASSES                           }....................
class CachedException(ValueError):
    '''
    Test-specific exception raised by unit tests exercising the
    :func:`beartype._util.cache.utilcacheerror.reraise_exception_cached`
    function.
    '''

    pass

# ....................{ TESTS ~ exception                 }....................
def test_reraise_exception_cached() -> None:
    '''
    Test the
    :func:`beartype._util.cache.utilcacheerror.reraise_exception_cached`
    function.
    '''

    # Defer heavyweight imports.
    from beartype._util.cache.utilcachecall import callable_cached
    from beartype._util.cache.utilcacheerror import reraise_exception_cached

    # Source substring to be hard-coded into the messages of all exceptions
    # raised by the low-level memoized callable defined below.
    TEST_SOURCE_STR = '{its_got_bro}'

    # Low-level memoized callable raising non-human-readable exceptions
    # conditionally depending on the value of passed parameters.
    @callable_cached
    def portend_low_level_winter(is_winter_coming: bool) -> str:
        if is_winter_coming:
            raise CachedException(
                '{} intimates that winter is coming.'.format(TEST_SOURCE_STR))
        else:
            return 'PRAISE THE SUN'

    # High-level non-memoized callable calling the low-level memoized callable
    # and reraising non-human-readable exceptions raised by the latter with
    # equivalent human-readable exceptions.
    def portend_high_level_winter() -> None:
        try:
            # Call the low-level memoized callable without raising exceptions.
            print(portend_low_level_winter(is_winter_coming=False))

            # Call the low-level memoized callable with raising exceptions.
            print(portend_low_level_winter(is_winter_coming=True))
        except CachedException as exception:
            # print('exception.args: {!r} ({!r})'.format(exception.args, type(exception.args)))
            reraise_exception_cached(
                exception=exception,
                source_str=TEST_SOURCE_STR,
                target_str=(
                    'Random "Song of Fire and Ice" spoiler' if getrandbits(1) else
                    'Random "Dark Souls" plaintext meme'
                ),
            )

    # Assert this high-level non-memoized callable raises the same type of
    # exception raised by this low-level memoized callable and preserve this
    # exception for subsequent assertion.
    with raises(CachedException) as exception_info:
        portend_high_level_winter()

    # Assert this exception's message does *NOT* contain the non-human-readable
    # source substring hard-coded into the messages of all exceptions raised by
    # this low-level memoized callable.
    assert TEST_SOURCE_STR not in str(exception_info.value)

    # Assert that exceptions messages may contain *NO* source substrings.
    try:
        raise CachedException(
            "What's bravery without a dash of recklessness?")
    except Exception as exception:
        with raises(CachedException):
            reraise_exception_cached(
                exception=exception,
                source_str=TEST_SOURCE_STR,
                target_str='and man sees not light,',
            )

    # Assert that exception messages may be empty.
    try:
        raise CachedException()
    except Exception as exception:
        with raises(CachedException):
            reraise_exception_cached(
                exception=exception,
                source_str=TEST_SOURCE_STR,
                target_str='but only endless nights.',
            )

    # Assert that exception messages need *NOT* be strings.
    try:
        raise CachedException(0xDEADBEEF)
    except Exception as exception:
        with raises(CachedException):
            reraise_exception_cached(
                exception=exception,
                source_str=TEST_SOURCE_STR,
                target_str='Rise if you would, for that is our curse.',
            )
