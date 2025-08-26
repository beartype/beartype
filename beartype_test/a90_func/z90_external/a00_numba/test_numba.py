#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Numba** integration tests.

This submodule functionally tests the :mod:`beartype` package against the
third-party Numba package.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
@skip_unless_package('numba')
def test_numba_njit() -> None:
    '''
    Functional test validating that the :mod:`beartype` package raises *no*
    unexpected exceptions when decorating callables also decorated by the
    third-party :func:`numba.njit` decorator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from numba import njit

    # ....................{ CALLABLES                      }....................
    @beartype
    @njit(cache=True)
    def had_shone_gleam_stony_orbs_so_from_his_steps() -> bool:
        '''
        Arbitrary callable decorated by both the :func:`beartype.beartype` *and*
        :func:`numba.njit` decorators in that order.
        '''

        return True

    # ....................{ ASSERTS                        }....................
    # Assert that calling the above callable returns the expected value.
    assert had_shone_gleam_stony_orbs_so_from_his_steps() is True
