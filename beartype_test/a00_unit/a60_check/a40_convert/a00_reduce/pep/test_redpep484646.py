#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`484`-, :pep:`612`-, or :pep:`646`-compliant **type parameter
reduction** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._check.convert._reduce._pep.redpep484646` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ factory                    }....................
def test_make_hint_pep484646_typeargs_to_hints() -> None:
    '''
    Test the private
    :func:`beartype._check.convert._reduce._pep.redpep484646._make_hint_pep484646_typeargs_to_hints`
    factory function.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import (
        BeartypeDecorHintPep484612646Exception,
        BeartypeDecorHintPep484TypeVarViolation,
    )
    from beartype._data.typing.datatyping import (
        S,
        T,
    )
    from beartype_test.a00_unit.data.hint.pep.proposal.data_pep484 import (
        T_any,
        T_sequence,
        T_str_or_bytes,
    )
    from beartype._check.convert._reduce._pep.redpep484646 import (
        _make_hint_pep484646_typeargs_to_hints)
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Type variable lookup table, initialized below.
    typearg_to_hint = {}

    # ....................{ PASS                           }....................
    # Assert that this mapper correctly maps a single type variable to a single
    # type hint.
    typearg_to_hint = _make_hint_pep484646_typeargs_to_hints(None, (S,), (int,))
    assert typearg_to_hint == {S: int}

    # Assert that this mapper correctly maps a single unbounded type variable
    # to a single type hint.
    typearg_to_hint = _make_hint_pep484646_typeargs_to_hints(
        None, (T_any,), (bool,))
    assert typearg_to_hint == {T_any: bool}

    # Assert that this mapper correctly maps a single type variable bounded to a
    # type to a single type hint satisfying that type.
    typearg_to_hint = _make_hint_pep484646_typeargs_to_hints(
        None, (T_sequence,), (list,))
    assert typearg_to_hint == {T_sequence: list}

    # Assert that this mapper correctly maps a single type variable constrained
    # to two or more types to a single type hint satisfying at least one of
    # those types.
    typearg_to_hint = _make_hint_pep484646_typeargs_to_hints(
        None, (T_str_or_bytes,), (bytes,))
    assert typearg_to_hint == {T_str_or_bytes: bytes}

    # Assert that this mapper correctly maps multiple type variables to multiple
    # type hints, including to a previously mapped type variable by silently
    # overwriting the type hint previously mapped to that type variable with the
    # corresponding passed hint.
    typearg_to_hint = _make_hint_pep484646_typeargs_to_hints(
        None, (T, S,), (float, complex,))
    assert typearg_to_hint == {S: complex, T: float}

    # ....................{ FAIL                           }....................
    # Assert that this mapper raises the expected exception when passed *NO*
    # type variables.
    with raises(BeartypeDecorHintPep484612646Exception):
        _make_hint_pep484646_typeargs_to_hints(None, (), (bool,))

    # Assert that this mapper raises the expected exception when passed a type
    # variable that is *NOT* actually a type variables.
    with raises(BeartypeDecorHintPep484612646Exception):
        _make_hint_pep484646_typeargs_to_hints(
            None,
            (S, 'His brother Death. A rare and regal prey',),
            (int, str,),
        )

    # Assert that this mapper raises the expected exception when passed *NO*
    # type hints.
    with raises(BeartypeDecorHintPep484612646Exception):
        _make_hint_pep484646_typeargs_to_hints(None, (S,), ())

    # Assert that this mapper raises the expected exception when passed more
    # type hints than type variables.
    with raises(BeartypeDecorHintPep484612646Exception):
        _make_hint_pep484646_typeargs_to_hints(
            None, (S, T,), (int, bool, complex,))

    # Assert that this mapper raises the expected violation when passed a type
    # hint violating the bounds of a passed type variable.
    with raises(BeartypeDecorHintPep484TypeVarViolation):
        _make_hint_pep484646_typeargs_to_hints(
            None, (S, T, T_sequence,), (float, complex, int,))

    #FIXME: Uncomment *AFTER* we generalize this mapper to type-check violations
    #against arbitrarily complex constraints.
    # # Assert that this mapper raises the expected violation when passed a type
    # # hint violating the constraints of a passed type variable.
    # with raises(BeartypeDecorHintPep484TypeVarViolation):
    #     map_pep484_typevars_to_hints(
    #         typearg_to_hint=typearg_to_hint,
    #         typevars=(S, T, T_str_or_bytes,),
    #         hints=(float, complex, ,),
    #     )

# ....................{ TESTS ~ reduce                     }....................
def test_reduce_hint_pep484646_subbed_typeargs_to_hints() -> None:
    '''
    Test the private
    :mod:`beartype._check.convert._reduce._pep.redpep484646.reduce_hint_pep484646_subbed_typeargs_to_hints`
    reducer.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep484612646Exception
    from beartype.typing import Generic
    from beartype._check.convert._reduce._pep.redpep484646 import (
        reduce_hint_pep484646_subbed_typeargs_to_hints)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12
    from beartype._data.typing.datatyping import (
        S,
        T,
    )
    from pytest import raises

    # ....................{ PEP 484                        }....................
    # Assert that this reducer reduces the PEP 484-compliant "typing.Generic"
    # superclass subscripted by only type variables to simply that superclass.
    assert reduce_hint_pep484646_subbed_typeargs_to_hints(
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
            unit_test_reduce_hint_pep484646_subbed_typeargs_to_hints_for_pep695)

        # Perform this test.
        unit_test_reduce_hint_pep484646_subbed_typeargs_to_hints_for_pep695()
    # Else, this interpreter targets Python < 3.12 and thus fails to support PEP
    # 695.

    # ....................{ FAIL                           }....................
    # Assert this reducer raises the expected exception when the passed object
    # is *NOT* a PEP 484- or 646-compliant type parameter.
    with raises(BeartypeDecorHintPep484612646Exception):
        reduce_hint_pep484646_subbed_typeargs_to_hints(
            'In thy devastating omnipotence,')
