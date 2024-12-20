#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`695` **type hint utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep695` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_is_hint_pep695_subscripted() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep695.is_hint_pep695_subscripted`
    tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep695 import (
        is_hint_pep695_subscripted)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12

    # If the active Python interpreter targets Python >= 3.12 and thus supports
    # PEP 695...
    if IS_PYTHON_AT_LEAST_3_12:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.pep695.data_pep695_util import (
            unit_test_is_hint_pep695_subscripted)

        # Perform this test.
        unit_test_is_hint_pep695_subscripted()
    # Else, this interpreter targets Python < 3.12 and thus fails to support PEP
    # 695.

    # ....................{ FAIL                           }....................
    # Assert this tester rejects objects that are *NOT* PEP 585-compliant
    # subscripted builtins.
    assert is_hint_pep695_subscripted(
        'And thou, colossal Skeleton, that, still') is False

# ....................{ TESTS ~ getter                     }....................
def test__get_hint_pep695_subscripted_typevar_to_hint() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep695._get_hint_pep695_subscripted_typevar_to_hint`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep695Exception
    from beartype._util.hint.pep.proposal.pep695 import (
        _get_hint_pep695_subscripted_typevar_to_hint)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12
    from pytest import raises

    # If the active Python interpreter targets Python >= 3.12 and thus supports
    # PEP 695...
    if IS_PYTHON_AT_LEAST_3_12:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.pep695.data_pep695_util import (
            unit_test__get_hint_pep695_subscripted_typevar_to_hint)

        # Perform this test.
        unit_test__get_hint_pep695_subscripted_typevar_to_hint()
    # Else, this interpreter targets Python < 3.12 and thus fails to support PEP
    # 695.

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed an object
    # that is *NOT* a PEP 695-compliant subscripted type alias.
    with raises(BeartypeDecorHintPep695Exception):
        _get_hint_pep695_subscripted_typevar_to_hint(
            'In thy devastating omnipotence,')

# ....................{ TESTS ~ iterator                   }....................
def test_iter_hint_pep695_forwardrefs() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep695.iter_hint_pep695_unsubscripted_forwardrefs`
    iterator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep695Exception
    from beartype._util.hint.pep.proposal.pep695 import (
        iter_hint_pep695_unsubscripted_forwardrefs)
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
        next(iter_hint_pep695_unsubscripted_forwardrefs(
            'Tumultuously accorded with those fits'))

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
        from beartype_test.a00_unit.data.pep.pep695.data_pep695_util import (
            unit_test_reduce_hint_pep695_unsubscripted)

        # Perform this test.
        unit_test_reduce_hint_pep695_unsubscripted()
    # Else, this interpreter targets Python < 3.12 and thus fails to support PEP
    # 695.
