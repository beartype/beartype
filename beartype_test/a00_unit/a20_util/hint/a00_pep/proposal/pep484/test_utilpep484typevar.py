#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`484`-compliant **type variable utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep484.pep484typevar` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ getter                     }....................
def test_get_hint_pep484_typevar_bound_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484.pep484typevar.get_hint_pep484_typevar_bound_or_none`
    tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep484Exception
    from beartype._util.hint.pep.proposal.pep484.pep484typevar import (
        get_hint_pep484_typevar_bound_or_none)
    from beartype_test.a00_unit.data.hint.pep.proposal.data_pep484 import (
        T,
        T_int,
        T_str_or_bytes,
    )
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this getter returns "None" for unbounded type variables.
    assert get_hint_pep484_typevar_bound_or_none(T) is None

    # Assert this getter reduces bounded type variables to their upper bound.
    assert get_hint_pep484_typevar_bound_or_none(T_int) is int

    # Union of all constraints parametrizing a constrained type variable,
    # reduced from that type variable.
    typevar_constraints_union = get_hint_pep484_typevar_bound_or_none(
        T_str_or_bytes)

    # Assert this union contains all constraints parametrizing this variable.
    assert str   in typevar_constraints_union.__args__
    assert bytes in typevar_constraints_union.__args__

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed a non-type
    # variable.
    with raises(BeartypeDecorHintPep484Exception):
        get_hint_pep484_typevar_bound_or_none(str)

# ....................{ TESTS ~ mapper                     }....................
def test_map_typevars_to_hints() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484.pep484typevar.map_typevars_to_hints`
    tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep484Exception
    from beartype._data.hint.datahinttyping import (
        S,
        T,
    )
    from beartype._util.hint.pep.proposal.pep484.pep484typevar import (
        map_typevars_to_hints)
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Type variable lookup table, initialized below.
    typevar_to_hint = {}

    # ....................{ PASS                           }....................
    # Assert that this getter correctly maps a single type variable to a single
    # type hint.
    map_typevars_to_hints(
        typevar_to_hint=typevar_to_hint,
        typevars=(S,),
        hints=(int,),
    )
    assert typevar_to_hint == {S: int}

    # Assert that this getter correctly maps multiple type variable to multiple 
    # type hints, including to a previously mapped type variable by silently
    # overwriting the type hint previously mapped to that type variable with the
    # corresponding passed hint.
    map_typevars_to_hints(
        typevar_to_hint=typevar_to_hint,
        typevars=(T, S,),
        hints=(float, complex,),
    )
    assert typevar_to_hint == {S: complex, T: float}

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed *NO* type
    # variables.
    with raises(BeartypeDecorHintPep484Exception):
        map_typevars_to_hints(
            typevar_to_hint=typevar_to_hint,
            typevars=(),
            hints=(bool,),
        )

    # Assert this getter raises the expected exception when passed *NO* type
    # hints.
    with raises(BeartypeDecorHintPep484Exception):
        map_typevars_to_hints(
            typevar_to_hint=typevar_to_hint,
            typevars=(S,),
            hints=(),
        )

    # Assert this getter raises the expected exception when passed more type
    # hints than type variables.
    with raises(BeartypeDecorHintPep484Exception):
        map_typevars_to_hints(
            typevar_to_hint=typevar_to_hint,
            typevars=(S, T,),
            hints=(int, bool, complex,),
        )
