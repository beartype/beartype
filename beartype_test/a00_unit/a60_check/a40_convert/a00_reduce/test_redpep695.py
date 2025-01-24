#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`695`-compliant **type alias reduction** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._check.convert._reduce._pep.redpep695` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ reducer                    }....................
def test_reduce_hint_pep695_unsubscripted() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep695.reduce_hint_pep695_unsubscripted`
    iterator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12

    # If the active Python interpreter targets Python >= 3.12 and thus supports
    # PEP 695...
    if IS_PYTHON_AT_LEAST_3_12:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.pep695.data_pep695util import (
            unit_test_reduce_hint_pep695_unsubscripted)

        # Perform this test.
        unit_test_reduce_hint_pep695_unsubscripted()
    # Else, this interpreter targets Python < 3.12 and thus fails to support PEP
    # 695.
