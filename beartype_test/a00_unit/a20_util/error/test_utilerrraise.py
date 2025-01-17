#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype exception raiser utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.error.utilerrraise` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_reraise_exception_placeholder() -> None:
    '''
    Test the
    :func:`beartype._util.error.utilerrraise.reraise_exception_placeholder`
    function.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.cache.utilcachecall import callable_cached
    from beartype._util.error.utilerrraise import reraise_exception_placeholder
    from pytest import raises
    from random import getrandbits

    # ....................{ CLASSES                        }....................
    class CachedException(ValueError):
        '''
        Test-specific exception intended to be raised below with messages
        containing placeholder substrings replaced by the
        :func:`.reraise_exception_placeholder` re-raiser.
        '''

        pass

    # ....................{ LOCALS                         }....................
    # Source substring to be hard-coded into the messages of all exceptions
    # raised by the low-level memoized callable defined below.
    TEST_SOURCE_STR = '{its_got_bro}'

    # ....................{ CALLABLES                      }....................
    @callable_cached
    def portend_low_level_winter(is_winter_coming: bool) -> str:
        '''
        Low-level memoized callable raising unreadable exceptions conditionally
        depending on the value of the passed parameter.
        '''

        if is_winter_coming:
            raise CachedException(
                f'{TEST_SOURCE_STR} intimates that winter is coming.')
        else:
            return 'PRAISE THE SUN'


    def portend_high_level_winter() -> None:
        '''
        High-level non-memoized callable calling the low-level memoized callable
        and reraising unreadable exceptions raised by the latter with equivalent
        readable exceptions.
        '''

        try:
            # Call the low-level memoized callable without raising exceptions.
            print(portend_low_level_winter(False))

            # Call the low-level memoized callable with raising exceptions.
            print(portend_low_level_winter(True))
        except CachedException as exception:
            # print('exception.args: {!r} ({!r})'.format(exception.args, type(exception.args)))
            reraise_exception_placeholder(
                exception=exception,
                source_str=TEST_SOURCE_STR,
                target_str=(
                    'Random "Song of Fire and Ice" spoiler' if getrandbits(1) else
                    'Random "Dark Souls" plaintext meme'
                ),
            )

    # ....................{ ASSERT                         }....................
    # Assert this high-level non-memoized callable raises the same type of
    # exception raised by this low-level memoized callable and preserve this
    # exception for subsequent assertion.
    with raises(CachedException) as exception_info:
        portend_high_level_winter()

    # Assert that this exception message does *NOT* contain the unreadable
    # source substring hard-coded into the messages of all exceptions raised by
    # this low-level memoized callable.
    assert TEST_SOURCE_STR not in str(exception_info.value)

    # Assert that exception messages may also contain *NO* source substrings.
    try:
        raise CachedException(
            "What's bravery without a dash of recklessness?")
    except Exception as exception:
        with raises(CachedException):
            reraise_exception_placeholder(
                exception=exception,
                source_str=TEST_SOURCE_STR,
                target_str='and man sees not light,',
            )

    # Assert that exception messages may be empty.
    try:
        raise CachedException()
    except Exception as exception:
        with raises(CachedException):
            reraise_exception_placeholder(
                exception=exception,
                source_str=TEST_SOURCE_STR,
                target_str='but only endless nights.',
            )

    # Assert that exception messages need *NOT* be strings.
    try:
        raise CachedException(0xDEADBEEF)
    except Exception as exception:
        with raises(CachedException):
            reraise_exception_placeholder(
                exception=exception,
                source_str=TEST_SOURCE_STR,
                target_str='Rise if you would, for that is our curse.',
            )
