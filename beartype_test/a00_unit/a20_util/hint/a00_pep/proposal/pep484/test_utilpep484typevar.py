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
    from beartype._data.hint.datahinttyping import T
    from beartype._util.hint.pep.proposal.pep484.pep484typevar import (
        get_hint_pep484_typevar_bound_or_none)
    from beartype_test.a00_unit.data.hint.pep.proposal.data_pep484 import (
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
    mapper.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import (
        BeartypeDecorHintPep484TypeVarException,
        BeartypeDecorHintPep484TypeVarViolation,
    )
    from beartype._data.hint.datahinttyping import (
        S,
        T,
    )
    from beartype_test.a00_unit.data.hint.pep.proposal.data_pep484 import (
        T_sequence,
        T_str_or_bytes,
    )
    from beartype._util.hint.pep.proposal.pep484.pep484typevar import (
        map_pep484_typevars_to_hints)
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Type variable lookup table, initialized below.
    typevar_to_hint = {}

    # ....................{ PASS                           }....................
    # Assert that this mapper correctly maps a single type variable to a single
    # type hint.
    map_pep484_typevars_to_hints(
        typevar_to_hint=typevar_to_hint,
        typevars=(S,),
        hints=(int,),
    )
    assert typevar_to_hint == {S: int}
    typevar_to_hint.clear()

    # Assert that this mapper correctly maps a single type variable bounded to a
    # type to a single type hint satisfying that type.
    map_pep484_typevars_to_hints(
        typevar_to_hint=typevar_to_hint,
        typevars=(T_sequence,),
        hints=(list,),
    )
    assert typevar_to_hint == {T_sequence: list}
    typevar_to_hint.clear()

    # Assert that this mapper correctly maps a single type variable constrained
    # to two or more types to a single type hint satisfying at least one of
    # those types.
    map_pep484_typevars_to_hints(
        typevar_to_hint=typevar_to_hint,
        typevars=(T_str_or_bytes,),
        hints=(bytes,),
    )
    assert typevar_to_hint == {T_str_or_bytes: bytes}
    typevar_to_hint.clear()

    # Assert that this mapper correctly maps multiple type variables to multiple
    # type hints, including to a previously mapped type variable by silently
    # overwriting the type hint previously mapped to that type variable with the
    # corresponding passed hint.
    map_pep484_typevars_to_hints(
        typevar_to_hint=typevar_to_hint,
        typevars=(T, S,),
        hints=(float, complex,),
    )
    assert typevar_to_hint == {S: complex, T: float}
    typevar_to_hint.clear()

    # ....................{ FAIL                           }....................
    # Assert that this mapper raises the expected exception when passed *NO*
    # type variables.
    with raises(BeartypeDecorHintPep484TypeVarException):
        map_pep484_typevars_to_hints(
            typevar_to_hint=typevar_to_hint,
            typevars=(),
            hints=(bool,),
        )

    # Assert that this mapper raises the expected exception when passed a type
    # variable that is *NOT* actually a type variables.
    with raises(BeartypeDecorHintPep484TypeVarException):
        map_pep484_typevars_to_hints(
            typevar_to_hint=typevar_to_hint,
            typevars=(S, 'His brother Death. A rare and regal prey',),
            hints=(int, str,),
        )

    # Assert that this mapper raises the expected exception when passed *NO*
    # type hints.
    with raises(BeartypeDecorHintPep484TypeVarException):
        map_pep484_typevars_to_hints(
            typevar_to_hint=typevar_to_hint,
            typevars=(S,),
            hints=(),
        )

    # Assert that this mapper raises the expected exception when passed more
    # type hints than type variables.
    with raises(BeartypeDecorHintPep484TypeVarException):
        map_pep484_typevars_to_hints(
            typevar_to_hint=typevar_to_hint,
            typevars=(S, T,),
            hints=(int, bool, complex,),
        )

    # Assert that this mapper raises the expected violation when passed a type
    # hint violating the bounds of a passed type variable.
    with raises(BeartypeDecorHintPep484TypeVarViolation):
        map_pep484_typevars_to_hints(
            typevar_to_hint=typevar_to_hint,
            typevars=(S, T, T_sequence,),
            hints=(float, complex, int,),
        )

    #FIXME: Uncomment *AFTER* we generalize this mapper to type-check violations
    #against arbitrarily complex constraints.
    # # Assert that this mapper raises the expected violation when passed a type
    # # hint violating the constraints of a passed type variable.
    # with raises(BeartypeDecorHintPep484TypeVarViolation):
    #     map_pep484_typevars_to_hints(
    #         typevar_to_hint=typevar_to_hint,
    #         typevars=(S, T, T_str_or_bytes,),
    #         hints=(float, complex, ,),
    #     )
