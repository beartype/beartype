#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
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
        # BeartypeDecorWrappeeException,
    )
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
    @beartype
    @lru_cache(maxsize=3)
    def increment_int_badly(n: int) -> int:
        '''
        Arbitrary :func:`functools.lru_cache`-memoized callable decorated by
        :func:`beartype.beartype` in a non-ideal order.
        '''

        return n + 1

    # Assert that the non-ideal memoized callable when passed a valid parameter
    # returns the expected value.
    assert increment_int_badly(24) == 25

    # Assert that the non-ideal memoized callable when passed an invalid
    # parameter raises the expected exception.
    with raises(BeartypeCallHintParamViolation):
        increment_int_badly('Gentle, and brave, and generous,—no lorn bard')

    # ....................{ CLASSES                        }....................
    @beartype
    class IntIncrementer(object):
        '''
        Arbitrary :func:`beartype.beartype`-decorated class defining various
        :func:`functools.lru_cache`-memoized methods exercising edge cases.
        '''

        # ....................{ NON-IDEAL ~ static         }....................
        @staticmethod
        @lru_cache(maxsize=3)
        def increment_int_badly_statically(n: int) -> int:
            '''
            Arbitrary :func:`functools.lru_cache`-memoized static method
            implicitly decorated by :func:`beartype.beartype` in a non-ideal
            order.

            This static method exercises an edge cases, as:

            #. The :func:`.lru_cache` decorator creates and returns a
               **pseudo-callable object** (i.e., object callable only due to the
               type of that object defining the ``__call__()`` dunder method)
               rather than a pure-Python function.
            #. The builtin :class:`staticmethod` type then creates and returns a
               C-based descriptor object calling that pseudo-callable object.
            #. The :func:`beartype.beartype` decorator then:

               #. Unwraps that C-based descriptor object to access that
                  pseudo-callable object.
               #. Recreates that C-based descriptor object to instead wrap a
                  dynamically generated type-checking wrapper function calling
                  that pseudo-callable object.

            In short, madness.
            '''

            return n + 1

    # Assert that the non-ideal memoized callable when passed a valid parameter
    # returns the expected value.
    assert IntIncrementer.increment_int_badly_statically(42) == 43

    # Assert that the non-ideal memoized callable when passed an invalid
    # parameter raises the expected exception.
    with raises(BeartypeCallHintParamViolation):
        IntIncrementer.increment_int_badly_statically(
            'As if the ebbing air had but one wave;')
