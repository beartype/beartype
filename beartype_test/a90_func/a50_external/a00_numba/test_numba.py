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
    #FIXME: Note that enabling "cache=True" causes Numba to
    #non-deterministically raise unreadable exceptions resembling:
    #    RuntimeError: cannot cache function
    #    'test_numba_njit.<locals>.had_shone_gleam_stony_orbs_so_from_his_steps':
    #    no locator available for file
    #    '/home/leycec/py/beartype/beartype_test/a90_func/z90_external/a00_numba/test_numba.py'
    #
    #It's possible this issue could be resolved by explicitly removing *ALL*
    #previously compiled bytecode associated with @njit-decorated callables,
    #perhaps by:
    #* Isolating this callable definition to a new
    #  "beartype_test.a90_func.data.external.numba.data_numba" submodule.
    #* Importing and calling below:
    #      from beartype_test.a90_func.data.external import numba
    #      from beartype_test._util.data.pytdataclean import clean_data_subpackage
    #      clean_data_subpackage(numba)
    #
    #      from beartype_test.a90_func.data.external.numba import data_numba
    #
    #Kinda awkward, but should work. There's no need to bother at the moment,
    #though. Simply disabling caching altogether trivially suffices for now.
    @beartype
    @njit(cache=False)
    def had_shone_gleam_stony_orbs_so_from_his_steps() -> bool:
        '''
        Arbitrary callable decorated by both the :func:`beartype.beartype` *and*
        :func:`numba.njit` decorators in that order.
        '''

        return True

    # ....................{ ASSERTS                        }....................
    # Assert that calling the above callable returns the expected value.
    assert had_shone_gleam_stony_orbs_so_from_his_steps() is True
