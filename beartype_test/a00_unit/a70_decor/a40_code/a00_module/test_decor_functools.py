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
    from beartype.roar import (
        BeartypeCallHintParamViolation,
        BeartypeDecorWrappeeException,
    )
    from beartype._util.py.utilpyversion import IS_PYTHON_3_8
    from functools import lru_cache
    from pytest import raises

    # ....................{ IDEAL                          }....................
    @lru_cache(maxsize=3)
    @beartype
    def increment_int_goodly(n: int) -> int:
        '''
        Arbitrary :func:`functools.lru_cache`-memoized callable decorated by
        :func:`beartype.beartype` in the ideal order.
        '''

        return n + 1


    # Assert that the ideal memoized callable when passed a valid parameter
    # returns the expected return.
    assert increment_int_goodly(42) == 43

    # Assert that the ideal memoized callable when passed an invalid parameter
    # raises the expected exception.
    with raises(BeartypeCallHintParamViolation):
        increment_int_goodly('The lone couch of his everlasting sleep:—')

    # ....................{ NON-IDEAL                      }....................
    # If the active Python interpreter targets Python 3.8, then @beartype fails
    # to support the edge case of non-ideal decoration ordering. In this case,
    # assert that @beartype raises the expected exception.
    if IS_PYTHON_3_8:
        with raises(BeartypeDecorWrappeeException):
            @beartype
            @lru_cache(maxsize=3)
            def increment_int_badly(n: int) -> int:
                '''
                Arbitrary :func:`functools.lru_cache`-memoized callable
                decorated by :func:`beartype.beartype` in a non-ideal order.
                '''

                return n + 1
    # Else, the active Python interpreter targets Python >= 3.9. In this case,
    # @beartype supports the edge case of non-ideal decoration ordering.
    else:
        @beartype
        @lru_cache(maxsize=3)
        def increment_int_badly(n: int) -> int:
            '''
            Arbitrary :func:`functools.lru_cache`-memoized callable decorated by
            :func:`beartype.beartype` in a non-ideal order.
            '''

            return n + 1

        # Assert that the non-ideal memoized callable when passed a valid parameter
        # returns the expected return.
        assert increment_int_badly(24) == 25

        # Assert that the non-ideal memoized callable when passed an invalid
        # parameter raises the expected exception.
        with raises(BeartypeCallHintParamViolation):
            increment_int_badly('Gentle, and brave, and generous,—no lorn bard')
