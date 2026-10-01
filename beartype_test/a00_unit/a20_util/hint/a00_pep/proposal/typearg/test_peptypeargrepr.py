#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type parameter representation utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.typearg.peptypeargrepr` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_make_hint_typearg_unpacked_repr() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.typearg.peptypeargrepr.make_hint_typearg_unpacked_repr`
    factory.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep484612646Exception
    from beartype._util.hint.pep.proposal.typearg.peptypeargrepr import (
        make_hint_typearg_unpacked_repr)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11
    from beartype_test.a00_unit.data.pep.data_pep612 import P
    from beartype_test.a00_unit.data.pep.pep484.data_pep484 import (
        T,
        T_bound_int,
        T_constraint_str_or_bytes,
    )
    from pytest import raises

    # ....................{ PASS ~ pep : 484               }....................
    # Unique repr() for a PEP 484-compliant unbounded type variable.
    T_repr = make_hint_typearg_unpacked_repr(T)

    # Assert that this repr() contains the expected substrings.
    assert 'TypeVar' in T_repr
    assert "'T'" in T_repr

    # Unique repr() for a PEP 484-compliant bounded type variable.
    T_bound_int_repr = make_hint_typearg_unpacked_repr(T_bound_int)

    # Assert that this repr() contains the expected substrings.
    assert 'bound' in T_bound_int_repr
    assert 'int' in T_bound_int_repr

    # Unique repr() for a PEP 484-compliant constrained type variable.
    T_constraint_str_or_bytes_repr = make_hint_typearg_unpacked_repr(
        T_constraint_str_or_bytes)

    # Assert that this repr() contains the expected substrings.
    assert 'constraints' in T_constraint_str_or_bytes_repr
    assert 'str' in T_constraint_str_or_bytes_repr
    assert 'bytes' in T_constraint_str_or_bytes_repr

    # ....................{ PASS ~ pep : 612               }....................
    # Unique repr() for a PEP 612-compliant parameter specification.
    P_repr = make_hint_typearg_unpacked_repr(P)

    # Assert that this repr() contains the expected substrings.
    assert 'ParamSpec' in P_repr
    assert "'P'" in P_repr

    # ....................{ PASS ~ pep : 646               }....................
    # If the active Python interpreter targets Python >= 3.11 and thus supports
    # PEP 646...
    if IS_PYTHON_AT_LEAST_3_11:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.data_pep646 import Ts_unpacked

        # Unique repr() for a PEP 646-compliant unpacked type variable tuple.
        Ts_unpacked_repr = make_hint_typearg_unpacked_repr(Ts_unpacked)

        # Assert that this repr() contains the expected substrings.
        assert 'TypeVarTuple' in Ts_unpacked_repr
        assert "'Ts'" in Ts_unpacked_repr

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed an object
    # that is *NOT* a type parameter.
    with raises(BeartypeDecorHintPep484612646Exception):
        make_hint_typearg_unpacked_repr(
            'Rich with a sprinkling of fair musk-rose blooms:')
