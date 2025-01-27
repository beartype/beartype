#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`, :pep:`612`, and :pep:`644` **type parameter utility**
unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep484612646` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ getter                     }....................
def test_get_hint_pep484612646_name() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep484612646.get_hint_pep484612646_typeparam_name`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep484612646Exception
    from beartype._data.hint.datahinttyping import T
    from beartype._util.hint.pep.proposal.pep484612646 import (
        get_hint_pep484612646_typeparam_name)
    from beartype._util.py.utilpyversion import (
        IS_PYTHON_AT_LEAST_3_11,
        IS_PYTHON_AT_LEAST_3_10,
    )
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this getter passed a PEP 484-compliant type variable returns the
    # name of this type variable.
    assert get_hint_pep484612646_typeparam_name(T) == 'T'

    # If the active Python interpreter targets Python >= 3.10 and thus supports
    # PEP 612...
    if IS_PYTHON_AT_LEAST_3_10:
        # Defer version-specific imports.
        from beartype.typing import ParamSpec

        # Arbitrary parameter specification.
        P = ParamSpec('P')

        # Assert this getter passed a PEP 612-compliant parameter specification
        # returns the name of this parameter specification.
        assert get_hint_pep484612646_typeparam_name(P) == 'P'

        # If the active Python interpreter targets Python >= 3.11 and thus
        # supports PEP 646...
        if IS_PYTHON_AT_LEAST_3_11:
            # Defer version-specific imports.
            from beartype.typing import TypeVarTuple

            # Arbitrary type variable tuple.
            Ts = TypeVarTuple('Ts')

            # Assert this getter passed a PEP 646-compliant type variable tuple
            # returns the name of this type variable tuple.
            assert get_hint_pep484612646_typeparam_name(Ts) == 'Ts'

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed an object
    # that is *NOT* a type parameter.
    with raises(BeartypeDecorHintPep484612646Exception):
        get_hint_pep484612646_typeparam_name(
            'As with a palsied tongue, and while his beard')
