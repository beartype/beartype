#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype callable calling utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.func.utilfunccall` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_call_func_async_sync() -> None:
    '''
    Test usage of the
    :func:`beartype._util.func.utilfunccall.call_func_async_sync` caller.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.utilfunccall import call_func_async_sync
    from beartype_test.a00_unit.data.data_type import (
        async_coroutine_factory,
        function,
    )
    from pytest import raises

    # Assert this caller returns the value returned by the coroutine created and
    # returned by this coroutine factory.
    assert call_func_async_sync(
        async_coroutine_factory,
        'And wall impregnable of beaming ice.\n'
    ) == (
        'And wall impregnable of beaming ice.\n'
        'Yet not a city, but a flood of ruin'
    )

    # Assert this caller raises the expected exception when passed an uncallable
    # object.
    with raises(_BeartypeUtilCallableException):
        call_func_async_sync('From yon remotest waste, have overthrown')
    # Assert this caller raises the expected exception when passed a synchronous
    # callable.
    with raises(_BeartypeUtilCallableException):
        call_func_async_sync(function)

    async def never_to_be_reclaimed():
        '''
        Arbitrary pure-Python asynchronous non-generator coroutine factory
        function raising an arbitrary exception.
        '''

        # Defer function-specific imports.
        from asyncio import sleep

        # Asynchronously switch to another scheduled asynchronous callable (if any).
        await sleep(0)

        # Raise an arbitrary exception.
        raise ValueError('The dwelling-place')

    # Assert this caller raises the expected exception when passed a coroutine
    # factory whose coroutine raises this exception when called.
    with raises(ValueError):
        call_func_async_sync(never_to_be_reclaimed)
