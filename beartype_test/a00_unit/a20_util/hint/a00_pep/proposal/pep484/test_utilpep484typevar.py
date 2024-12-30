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



def test_get_hint_pep484_typevars_to_hints() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484.pep484typevar._get_hint_pep484_typevars_to_hints`
    getter.
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
        _get_hint_pep484_typevars_to_hints)
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Type variable lookup table, initialized below.
    typevar_to_hint = {}

    # ....................{ PASS                           }....................
    # Assert that this mapper correctly maps a single type variable to a single
    # type hint.
    typevar_to_hint = _get_hint_pep484_typevars_to_hints(
        typevars=(S,), hints=(int,))
    assert typevar_to_hint == {S: int}

    # Assert that this mapper correctly maps a single type variable bounded to a
    # type to a single type hint satisfying that type.
    typevar_to_hint = _get_hint_pep484_typevars_to_hints(
        typevars=(T_sequence,), hints=(list,))
    assert typevar_to_hint == {T_sequence: list}

    # Assert that this mapper correctly maps a single type variable constrained
    # to two or more types to a single type hint satisfying at least one of
    # those types.
    typevar_to_hint = _get_hint_pep484_typevars_to_hints(
        typevars=(T_str_or_bytes,), hints=(bytes,))
    assert typevar_to_hint == {T_str_or_bytes: bytes}

    # Assert that this mapper correctly maps multiple type variables to multiple
    # type hints, including to a previously mapped type variable by silently
    # overwriting the type hint previously mapped to that type variable with the
    # corresponding passed hint.
    typevar_to_hint = _get_hint_pep484_typevars_to_hints(
        typevars=(T, S,), hints=(float, complex,))
    assert typevar_to_hint == {S: complex, T: float}

    # ....................{ FAIL                           }....................
    # Assert that this mapper raises the expected exception when passed *NO*
    # type variables.
    with raises(BeartypeDecorHintPep484TypeVarException):
        _get_hint_pep484_typevars_to_hints(
            typevars=(), hints=(bool,))

    # Assert that this mapper raises the expected exception when passed a type
    # variable that is *NOT* actually a type variables.
    with raises(BeartypeDecorHintPep484TypeVarException):
        _get_hint_pep484_typevars_to_hints(
            typevars=(S, 'His brother Death. A rare and regal prey',),
            hints=(int, str,),
        )

    # Assert that this mapper raises the expected exception when passed *NO*
    # type hints.
    with raises(BeartypeDecorHintPep484TypeVarException):
        _get_hint_pep484_typevars_to_hints(
            typevars=(S,), hints=())

    # Assert that this mapper raises the expected exception when passed more
    # type hints than type variables.
    with raises(BeartypeDecorHintPep484TypeVarException):
        _get_hint_pep484_typevars_to_hints(
            typevars=(S, T,), hints=(int, bool, complex,))

    # Assert that this mapper raises the expected violation when passed a type
    # hint violating the bounds of a passed type variable.
    with raises(BeartypeDecorHintPep484TypeVarViolation):
        _get_hint_pep484_typevars_to_hints(
            typevars=(S, T, T_sequence,), hints=(float, complex, int,))

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

# ....................{ TESTS ~ reduce                     }....................
def test_reduce_hint_pep484_subscripted_typevar_to_hint() -> None:
    '''
    Test the public
    :mod:`beartype._util.hint.pep.proposal.pep484.pep484typevar.reduce_hint_pep484_subscripted_typevar_to_hint`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep484TypeVarException
    from beartype.typing import (
        Generic,
    )
    from beartype._util.hint.pep.proposal.pep484.pep484typevar import (
        reduce_hint_pep484_subscripted_typevar_to_hint)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12
    from beartype._data.hint.datahinttyping import (
        S,
        T,
        # U,
    )
    # from beartype_test.a00_unit.data.hint.pep.proposal.pep484585.data_pep484585generic import (
    #     Pep484GenericST,
    # )
    from pytest import raises

    # ....................{ PEP 484                        }....................
    # Assert that this reducer reduces the PEP 484-compliant "typing.Generic"
    # superclass subscripted by only type variables to simply that superclass.
    assert reduce_hint_pep484_subscripted_typevar_to_hint(
        Generic[S, T]) is Generic

    # ....................{ PEP 695                        }....................
    # If the active Python interpreter targets Python >= 3.12 and thus supports
    # PEP 695...
    #
    # Note that PEP 695-compliant type aliases are used here as a reference
    # "subscripted hint", due to being the easiest subscripted hints to define,
    # use, and debug (under Python >= 3.12, anyway). Valid alternatives include:
    # * PEP 484- or 585-compliant subscripted generics, which are considerably
    #   more cumbersome to define.
    if IS_PYTHON_AT_LEAST_3_12:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.pep695.data_pep695util import (
            unit_test_reduce_hint_pep484_subscripted_typevar_to_hint)

        # Perform this test.
        unit_test_reduce_hint_pep484_subscripted_typevar_to_hint()
    # Else, this interpreter targets Python < 3.12 and thus fails to support PEP
    # 695.

    # ....................{ FAIL                           }....................
    # Assert this reducer raises the expected exception when passed an object
    # that is *NOT* a PEP 695-compliant subscripted type alias.
    with raises(BeartypeDecorHintPep484TypeVarException):
        reduce_hint_pep484_subscripted_typevar_to_hint(
            'In thy devastating omnipotence,')
