#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype decorator :mod:`functools`-specific unit tests.

This submodule unit tests the :func:`beartype.beartype` decorator with respect
the standard :mod:`functools` module.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_decor_functools_lru_cache() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on
    :func:`functools.lru_cache`-based **memoized callables** (i.e., pure-Python
    callables decorated by that standard decorator, which then creates and
    returns low-level C-based callable objects memoizing those callables).
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    # from beartype.roar import BeartypeCallHintParamViolation
    from beartype.typing import (
        Iterator,
        # Union,
    )
    from functools import lru_cache
    from pytest import raises

    # ....................{ CONTEXTS                       }....................
    @lru_cache(maxsize=3)
    @beartype
    def increment_int_goodly(n: int) -> Iterator[int]:
        '''
        Arbitrary :func:`functools.lru_cache`-decorated callable decorated by
        :func:`beartype.beartype` in the ideal order.
        '''

        yield n + 1


    @beartype
    @lru_cache(maxsize=3)
    def increment_int_badly(n: int) -> int:
        '''
        Arbitrary :func:`functools.lru_cache`-decorated callable decorated by
        :func:`beartype.beartype` in a non-ideal order.
        '''

        return n + 1

    #FIXME: Uncomment us after worky, please.
    # # ....................{ PASS                           }....................
    # # Assert that the non-ideal context manager when passed a valid parameter
    # # returns the expected return.
    # with may_modulate_with(
    #     'And voice of living beings, and woven hymns') as and_woven_hymns:
    #     assert and_woven_hymns == 'And voice of living beings, and woven hymns'
    #
    # # Assert that the ideal context manager when passed a valid parameter
    # # returns the expected return.
    # with and_motions_of(len(
    #     'Of night and day, and the deep heart of man.')) as (
    #     deep_heart_of_man):
    #     assert deep_heart_of_man == len(
    #         'Of night and day, and the deep heart of man.')
    #
    # # ....................{ FAIL                           }....................
    # # Assert that the non-ideal context manager when passed an invalid parameter
    # # raises the expected exception.
    # with raises(BeartypeCallHintParamViolation):
    #     may_modulate_with(b'There was a Poet whose untimely tomb')
    #
    # # Assert that the ideal context manager when passed an invalid parameter
    # # raises the expected exception.
    # with raises(BeartypeCallHintParamViolation):
    #     and_motions_of('No human hands with pious reverence reared,')
