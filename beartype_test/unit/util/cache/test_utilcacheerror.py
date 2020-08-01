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
import pytest
from random import getrandbits

# ....................{ TESTS                             }....................
def test_reraise_exception_cached_pass() -> None:
    '''
    Test successful usage of the
    :func:`beartype._util.cache.utilcacheerror.reraise_exception_cached`
    function.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintValuePepException
    from beartype._util.cache.utilcachecall import callable_cached
    from beartype._util.cache.utilcacheerror import reraise_exception_cached

    # Format variable substring to be hard-coded into the messages of all
    # exceptions raised by this low-level memoized callable.
    FORMAT_VAR = '{its_got_bro}'

    # Low-level memoized callable raising non-human-readable exceptions
    # conditionally depending on the value of passed parameters.
    @callable_cached
    def portend_low_level_winter(is_winter_coming: bool) -> str:
        if is_winter_coming:
            raise BeartypeDecorHintValuePepException(
                '{} intimates that winter is coming.'.format(FORMAT_VAR))
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
        except BeartypeDecorHintValuePepException as exception:
            # print('exception.args: {!r} ({!r})'.format(exception.args, type(exception.args)))
            reraise_exception_cached(
                exception=exception,
                format_str=(
                    'Random "Song of Fire and Ice" spoiler' if getrandbits(1) else
                    'Random "Dark Souls" plaintext meme'
                ),
                format_var=FORMAT_VAR,
            )

    # Assert this high-level non-memoized callable raises the same type of
    # exception raised by this low-level memoized callable.
    with pytest.raises(BeartypeDecorHintValuePepException) as exception_info:
        portend_high_level_winter()

    # Assert this exception's message does *NOT* contain the non-human-readable
    # format variable hard-coded into the messages of all exceptions raised by
    # this low-level memoized callable.
    assert FORMAT_VAR not in str(exception_info.value)


def test_reraise_exception_cached_fail() -> None:
    '''
    Test unsuccessful usage of the
    :func:`beartype._util.cache.utilcacheerror.reraise_exception_cached`
    function.
    '''

    # Defer heavyweight imports.
    from beartype.roar import _BeartypeUtilCachedExceptionException
    from beartype._util.cache.utilcacheerror import reraise_exception_cached

    # Format variable substring to be hard-coded into the messages of all
    # exceptions raised by this low-level memoized callable.
    FORMAT_VAR = '{aldia}'

    # Assert that format variables must be "{"- and "}"-delimited.
    try:
        raise ValueError(
            'Men are props on the stage of life, '
            'and no matter how tender, '
            'how exquisite... ' + FORMAT_VAR
        )
    except Exception as exception:
        with pytest.raises(_BeartypeUtilCachedExceptionException):
            reraise_exception_cached(
                exception=exception,
                format_str='A lie will remain a lie.',
                format_var=FORMAT_VAR[1:],
            )
        with pytest.raises(_BeartypeUtilCachedExceptionException):
            reraise_exception_cached(
                exception=exception,
                format_str='Even now there are only embers,',
                format_var=FORMAT_VAR[:-1],
            )

    # Assert that exceptions messages must contain format variables.
    try:
        raise ValueError(
            "What's bravery without a dash of recklessness?")
    except Exception as exception:
        with pytest.raises(_BeartypeUtilCachedExceptionException):
            reraise_exception_cached(
                exception=exception,
                format_str='and man sees not light,',
                format_var=FORMAT_VAR,
            )

    # Assert that exception messages must be non-empty.
    try:
        raise ValueError()
    except Exception as exception:
        with pytest.raises(_BeartypeUtilCachedExceptionException):
            reraise_exception_cached(
                exception=exception,
                format_str='but only endless nights.',
                format_var=FORMAT_VAR,
            )

    # Assert that exception messages must be strings.
    try:
        raise ValueError(0xDEADBEEF)
    except Exception as exception:
        with pytest.raises(_BeartypeUtilCachedExceptionException):
            reraise_exception_cached(
                exception=exception,
                format_str='Rise if you would, for that is our curse.',
                format_var=FORMAT_VAR,
            )
