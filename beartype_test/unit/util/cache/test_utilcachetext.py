#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype exception caching utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.cache.utilcachetext` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import pytest
from random import getrandbits

# ....................{ CLASSES                           }....................
class CachedException(ValueError):
    '''
    Test-specific exception raised by unit tests exercising the
    :func:`beartype._util.cache.utilcachetext.reraise_exception_cached`
    function.
    '''

    pass

# ....................{ TESTS ~ format                    }....................
def test_format_text_cached_pass() -> None:
    '''
    Test successful usage of the
    :func:`beartype._util.cache.utilcachetext.format_text_cached` function.
    '''

    # Defer heavyweight imports.
    from beartype._util.cache.utilcachetext import (
        format_text_cached, CACHED_FORMAT_VAR)

    # Assert that formatting text with the codepath optimized for the default
    # format variable succeeds with text containing that variable.
    assert format_text_cached(
        text='A {0} curse; a {0} sea.'.format(CACHED_FORMAT_VAR),
        format_str='bottomless',
    ) == 'A bottomless curse; a bottomless sea.'

    # Assert that formatting text with the codepath optimized for the default
    # format variable succeeds with text *NOT* containing that variable.
    assert format_text_cached(
        text="You're a hunter with your sanity, aren't you?",
        format_str="Must've taken a wrong turn, then...",
    ) == "You're a hunter with your sanity, aren't you?"

    # Assert that formatting text with the codepath unoptimized for a passed
    # format variable succeeds with text containing that variable.
    assert format_text_cached(
        text='Source of {rlyeh} greatness, {rlyeh} things that be.',
        format_str='all',
        format_var='{rlyeh}',
    ) == 'Source of all greatness, all things that be.'

    # Assert that formatting text with the codepath unoptimized for a passed
    # format variable succeeds with text *NOT* containing that variable.
    assert format_text_cached(
        text='Acts of goodness are not always wise,',
        format_str='and acts of evil are not always foolish,',
        format_var='{but_regardless_we_shall_always_strive_to_be_good}',
    ) == 'Acts of goodness are not always wise,'


def test_format_text_cached_pass() -> None:
    '''
    Test unsuccessful usage of the
    :func:`beartype._util.cache.utilcachetext.format_text_cached` function.
    '''

    # Defer heavyweight imports.
    from beartype.roar import _BeartypeUtilCachedTextException
    from beartype._util.cache.utilcachetext import format_text_cached

    # Assert that format variables must be "{"- and "}"-delimited.
    with pytest.raises(_BeartypeUtilCachedTextException):
        format_text_cached(
            text='Listen for the baneful chants.',
            format_str='Weep with them as one in trance.',
            format_var='{weep_with_us',
        )

# ....................{ TESTS ~ exception                 }....................
def test_reraise_exception_cached_pass() -> None:
    '''
    Test successful usage of the
    :func:`beartype._util.cache.utilcachetext.reraise_exception_cached`
    function.
    '''

    # Defer heavyweight imports.
    from beartype._util.cache.utilcachecall import callable_cached
    from beartype._util.cache.utilcachetext import reraise_exception_cached

    # Format variable substring to be hard-coded into the messages of all
    # exceptions raised by this low-level memoized callable.
    TEST_FORMAT_VAR = '{its_got_bro}'

    # Low-level memoized callable raising non-human-readable exceptions
    # conditionally depending on the value of passed parameters.
    @callable_cached
    def portend_low_level_winter(is_winter_coming: bool) -> str:
        if is_winter_coming:
            raise CachedException(
                '{} intimates that winter is coming.'.format(TEST_FORMAT_VAR))
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
                format_str=(
                    'Random "Song of Fire and Ice" spoiler' if getrandbits(1) else
                    'Random "Dark Souls" plaintext meme'
                ),
                format_var=TEST_FORMAT_VAR,
            )

    # Assert this high-level non-memoized callable raises the same type of
    # exception raised by this low-level memoized callable and preserve this
    # exception for subsequent assertion.
    with pytest.raises(CachedException) as exception_info:
        portend_high_level_winter()

    # Assert this exception's message does *NOT* contain the non-human-readable
    # format variable hard-coded into the messages of all exceptions raised by
    # this low-level memoized callable.
    assert TEST_FORMAT_VAR not in str(exception_info.value)

    # Assert that exceptions messages may contain *NO* format variables.
    try:
        raise CachedException(
            "What's bravery without a dash of recklessness?")
    except Exception as exception:
        with pytest.raises(CachedException):
            reraise_exception_cached(
                exception=exception,
                format_str='and man sees not light,',
                format_var=TEST_FORMAT_VAR,
            )


def test_reraise_exception_cached_fail() -> None:
    '''
    Test unsuccessful usage of the
    :func:`beartype._util.cache.utilcachetext.reraise_exception_cached`
    function.
    '''

    # Defer heavyweight imports.
    from beartype.roar import _BeartypeUtilCachedTextException
    from beartype._util.cache.utilcachetext import reraise_exception_cached

    # Format variable substring to be hard-coded into the messages of all
    # exceptions raised by this low-level memoized callable.
    TEST_FORMAT_VAR = '{aldia}'

    # Assert that format variables must be "{"- and "}"-delimited.
    try:
        raise CachedException(
            'Men are props on the stage of life, '
            'and no matter how tender, '
            'how exquisite... ' + TEST_FORMAT_VAR
        )
    except Exception as exception:
        with pytest.raises(_BeartypeUtilCachedTextException):
            reraise_exception_cached(
                exception=exception,
                format_str='A lie will remain a lie.',
                format_var=TEST_FORMAT_VAR[1:],
            )
        with pytest.raises(_BeartypeUtilCachedTextException):
            reraise_exception_cached(
                exception=exception,
                format_str='Even now there are only embers,',
                format_var=TEST_FORMAT_VAR[:-1],
            )

    # Assert that exception messages must be non-empty.
    try:
        raise CachedException()
    except Exception as exception:
        with pytest.raises(_BeartypeUtilCachedTextException):
            reraise_exception_cached(
                exception=exception,
                format_str='but only endless nights.',
                format_var=TEST_FORMAT_VAR,
            )

    # Assert that exception messages must be strings.
    try:
        raise CachedException(0xDEADBEEF)
    except Exception as exception:
        with pytest.raises(_BeartypeUtilCachedTextException):
            reraise_exception_cached(
                exception=exception,
                format_str='Rise if you would, for that is our curse.',
                format_var=TEST_FORMAT_VAR,
            )
