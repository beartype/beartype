#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`695` **type hint utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.utilpep695` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ iterator                   }....................
def test_iter_hint_pep695_forwardrefs() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.utilpep695.iter_hint_pep695_forwardrefs`
    iterator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep695Exception
    from beartype._util.hint.pep.proposal.utilpep695 import (
        iter_hint_pep695_forwardrefs)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12
    from pytest import raises

    # If the active Python interpreter targets Python >= 3.12 and thus supports
    # PEP 695...
    if IS_PYTHON_AT_LEAST_3_12:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.pep695.data_pep695_util import (
            unit_test_iter_hint_pep695_forwardrefs)

        # Perform this test.
        unit_test_iter_hint_pep695_forwardrefs()
    # Else, this interpreter targets Python < 3.12 and thus fails to support PEP
    # 695.

    # ....................{ FAIL                           }....................
    # Assert this iterator raises the expected exception when passed an
    # arbitrary PEP 695-noncompliant object.
    with raises(BeartypeDecorHintPep695Exception):
        next(iter_hint_pep695_forwardrefs(
            'Tumultuously accorded with those fits'))

# ....................{ TESTS ~ reducer                    }....................
def test_reduce_hint_pep695() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.utilpep695.reduce_hint_pep695`
    iterator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12

    # If the active Python interpreter targets Python >= 3.12 and thus supports
    # PEP 695...
    if IS_PYTHON_AT_LEAST_3_12:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.pep695.data_pep695_util import (
            unit_test_reduce_hint_pep695)

        # Perform this test.
        unit_test_reduce_hint_pep695()
    # Else, this interpreter targets Python < 3.12 and thus fails to support PEP
    # 695.
