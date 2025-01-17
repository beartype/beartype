#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **type-checking expression snippet class unit tests.**

This submodule unit tests the public API of the public
:mod:`beartype._check.code.snip.codesnipcls.PITH_INDEX_TO_VAR_NAME` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_pith_index_to_var_name() -> None:
    '''
    Test the :obj:`beartype._check.code.snip.codesnipcls.PITH_INDEX_TO_VAR_NAME`
    dictionary singleton.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._check.code.snip.codesnipcls import PITH_INDEX_TO_VAR_NAME
    from beartype._check.checkmagic import VAR_NAME_PITH_PREFIX
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this dictionary indexed by various positive integers creates and
    # returns the expected local pith variable names.
    assert PITH_INDEX_TO_VAR_NAME[1] == f'{VAR_NAME_PITH_PREFIX}1'
    assert PITH_INDEX_TO_VAR_NAME[2] == f'{VAR_NAME_PITH_PREFIX}2'

    # Assert this dictionary internally caches these constants.
    assert PITH_INDEX_TO_VAR_NAME[1] is PITH_INDEX_TO_VAR_NAME[1]
    assert PITH_INDEX_TO_VAR_NAME[2] is PITH_INDEX_TO_VAR_NAME[2]

    # ....................{ FAIL                           }....................
    # Assert that attempting to index this dictionary by non-integer indices
    # raises the expected exception.
    with raises(AssertionError):
        PITH_INDEX_TO_VAR_NAME[2.34]

    # Assert that attempting to index this dictionary by negative indices
    # raises the expected exception.
    with raises(AssertionError):
        PITH_INDEX_TO_VAR_NAME[-1]
