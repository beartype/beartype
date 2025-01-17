#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype decorator :mod:`contextlib`-specific unit tests.

This submodule unit tests the :func:`beartype.beartype` decorator with respect
the standard :mod:`contextlib` module.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS                              }....................
@skip_if_python_version_less_than('3.11.0')
async def test_decor_contextlib_asynccontextmanager() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on
    :func:`contextlib.asynccontextmanager`-based **asynchronous context
    managers** (i.e., generator factory functions decorated by that standard
    decorator) if the active Python interpreter targets Python >= 3.11 and thus
    defines the ``co_qualname`` attribute on code objects required to implement
    this functionality *or* skip this test otherwise.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from asyncio import run as asyncio_run
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from beartype.typing import (
        AsyncIterator,
        Union,
    )
    from contextlib import asynccontextmanager
    from pytest import raises

    # ....................{ CONTEXTS                       }....................
    @asynccontextmanager
    @beartype
    async def art_king_of(
        this_frail_world: Union[int, float]) -> AsyncIterator[int]:
        '''
        Arbitrary :func:`contextlib.asynccontextmanager`-decorated context
        manager decorated by :func:`beartype.beartype` in the ideal order.
        '''

        yield int(this_frail_world)


    @beartype
    @asynccontextmanager
    async def from_the_red_field(
        of_slaughter: str) -> AsyncIterator[Union[str, bool]]:
        '''
        Arbitrary :func:`contextlib.asynccontextmanager`-decorated context
        manager decorated by :func:`beartype.beartype` in a non-ideal order.
        '''

        yield of_slaughter

    # ....................{ PASS                           }....................
    # Assert that the ideal context manager when passed a valid parameter
    # returns the expected return.
    async with art_king_of(len(
        'Art king of this frail world, from the red field')) as (
        from_the_reeking_hospital):
        assert from_the_reeking_hospital == len(
            'Art king of this frail world, from the red field')

    # Assert that the non-ideal context manager when passed a valid parameter
    # returns the expected return.
    async with from_the_red_field(
        'Of slaughter, from the reeking hospital,') as (
        the_patriots_sacred_couch):
        assert the_patriots_sacred_couch == (
            'Of slaughter, from the reeking hospital,')

    # ....................{ FAIL                           }....................
    # Assert that the ideal context manager when passed an invalid parameter
    # raises the expected exception.
    with raises(BeartypeCallHintParamViolation):
        await art_king_of("The patriot's sacred couch, the snowy bed")

    # Assert that the non-ideal context manager when passed an invalid parameter
    # raises the expected exception.
    with raises(BeartypeCallHintParamViolation):
        await from_the_red_field(b'Of innocence, the scaffold and the throne,')


@skip_if_python_version_less_than('3.11.0')
def test_decor_contextlib_contextmanager() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on
    :func:`contextlib.contextmanager`-based **synchronous context managers**
    (i.e., generator factory functions decorated by that standard decorator) if
    the active Python interpreter targets Python >= 3.11 and thus defines the
    ``co_qualname`` attribute on code objects required to implement this
    functionality *or* skip this test otherwise.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from beartype.typing import (
        Iterator,
        Union,
    )
    from contextlib import contextmanager
    from pytest import raises

    # ....................{ CONTEXTS                       }....................
    @contextmanager
    @beartype
    def and_motions_of(
        the_forests_and_the_sea: Union[int, float]) -> Iterator[int]:
        '''
        Arbitrary :func:`contextlib.contextmanager`-decorated context manager
        decorated by :func:`beartype.beartype` in the ideal order.
        '''

        yield int(the_forests_and_the_sea)


    @beartype
    @contextmanager
    def may_modulate_with(
        murmurs_of_the_air: str) -> Iterator[Union[str, bool]]:
        '''
        Arbitrary :func:`contextlib.contextmanager`-decorated context manager
        decorated by :func:`beartype.beartype` in a non-ideal order.
        '''

        yield murmurs_of_the_air

    # ....................{ PASS                           }....................
    # Assert that the ideal context manager when passed a valid parameter
    # returns the expected return.
    with and_motions_of(len(
        'Of night and day, and the deep heart of man.')) as (
        deep_heart_of_man):
        assert deep_heart_of_man == len(
            'Of night and day, and the deep heart of man.')

    # Assert that the non-ideal context manager when passed a valid parameter
    # returns the expected return.
    with may_modulate_with(
        'And voice of living beings, and woven hymns') as and_woven_hymns:
        assert and_woven_hymns == 'And voice of living beings, and woven hymns'

    # ....................{ FAIL                           }....................
    # Assert that the ideal context manager when passed an invalid parameter
    # raises the expected exception.
    with raises(BeartypeCallHintParamViolation):
        and_motions_of('No human hands with pious reverence reared,')

    # Assert that the non-ideal context manager when passed an invalid parameter
    # raises the expected exception.
    with raises(BeartypeCallHintParamViolation):
        may_modulate_with(b'There was a Poet whose untimely tomb')
