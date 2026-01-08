#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`484`-, :pep:`612`-, or :pep:`646`-compliant **type parameter
reduction** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._check.convert._reduce._pep.redpep484612646` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ factory                    }....................
def test_make_hint_pep484612646_typearg_to_hint() -> None:
    '''
    Test the private
    :func:`beartype._check.convert._reduce._pep.redpep484612646._make_hint_pep484612646_typearg_to_hint`
    factory function.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import (
        BeartypeDecorHintPep484612646Exception,
        BeartypeDecorHintPep484TypeVarViolation,
    )
    from beartype._check.convert._reduce._pep.redpep484612646 import (
        _make_hint_pep484612646_typearg_to_hint)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11
    from beartype_test.a00_unit.data.pep.data_pep484 import (
        S,
        T,
        U,
        V,
        T_any,
        T_sequence,
        T_str_or_bytes,
    )
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # List of all valid type parameter mapping cases to be tested, each defined
    # as a 3-tuple "(hints_typearg, hints_child, typearg_to_hint)" where:
    # * "hints_typearg" is the input tuple of one or more type parameters to be
    #   mapped to child hints.
    # * "hints_child" is the input tuple of zero or more child hints to map
    #   these type parameters to.
    # * "typearg_to_hint" is the output dictionary expected to be returned from
    #   the _make_hint_pep484612646_typearg_to_hint() factory when passed these
    #   input tuples.
    typearg_mappings_valid = [
        # ....................{ PEP 484                    }....................
        # A single PEP 484-compliant type variable maps to a single child hint.
        ((S,), (int,), {S: int}),

        # A single PEP 484-compliant type variable bound to an ignorable hint
        # maps to a single child hint.
        ((T_any,), (bool,), {T_any: bool}),

        # A single PEP 484-compliant type variable bound to an arbitrary type
        # maps to a single child hint satisfying that type.
        ((T_sequence,), (list,), {T_sequence: list}),

        # A single PEP 484-compliant type variable constrained to two or more
        # types maps to a single child hint satisfying at least one of those
        # types.
        ((T_str_or_bytes,), (bytes,), {T_str_or_bytes: bytes}),

        # Multiple PEP 484-compliant type variables map to multiple child hints.
        ((T, S,), (float, complex,), {S: complex, T: float}),
    ]

    # List of all invalid type parameter mapping cases to be tested, each
    # defined as a 3-tuple "(hints_typearg, hints_child, exception_type)" where:
    # * "hints_typearg" is the input tuple of one or more type parameters to be
    #   mapped to child hints.
    # * "hints_child" is the input tuple of zero or more child hints to map
    #   these type parameters to.
    # * "exception_type" is the type of output exception expected to be raised
    #   by the _make_hint_pep484612646_typearg_to_hint() factory when passed
    #   these input tuples.
    typearg_mappings_invalid = [
        # ....................{ CORE                       }....................
        # Assert that this factory raises the expected exception when passed
        # *NO* type parameters.
        ((), (bool,), BeartypeDecorHintPep484612646Exception),

        # Assert that this factory raises the expected exception when passed a
        # tuple of type parameters containing a valid type parameter and another
        # arbitrary object that is *NOT* a type variables.
        (
            (S, 'His brother Death. A rare and regal prey',),
            (int, str,),
            BeartypeDecorHintPep484612646Exception,
        ),

        # ....................{ PEP 484                    }....................
        # Assert that this factory raises the expected exception when passed one
        # PEP 484-compliant type variable but *NO* corresponding child hint.
        ((S,), (), BeartypeDecorHintPep484612646Exception),

        # Assert that this factory raises the expected exception when passed
        # more child hints than PEP 484-compliant type variables.
        (
            (S, T,),
            (int, bool, complex,),
            BeartypeDecorHintPep484612646Exception,
        ),

        # Assert that this factory raises the expected violation when passed a
        # child hint violating the bounds of a passed PEP 484-compliant type
        # variable.
        (
            (S, T, T_sequence,),
            (float, complex, int,),
            BeartypeDecorHintPep484TypeVarViolation,
        ),

        #FIXME: Uncomment *AFTER* we generalize this mapper to type-check
        #violations against arbitrarily complex constraints.
        # # Assert that this mapper raises the expected violation when passed a type
        # # hint violating the constraints of a passed type variable.
        # (
        #     (S, T, T_str_or_bytes,),
        #     (float, complex, ,),
        #     BeartypeDecorHintPep484TypeVarViolation,
        # )
    ]

    # ..................{ PEP 646                            }..................
    # If the active Python interpreter targets Python >= 3.11 and thus supports
    # PEP 646...
    if IS_PYTHON_AT_LEAST_3_11:
        # ....................{ IMPORTS                    }....................
        # Defer PEP-specific imports.
        # from beartype.roar import BeartypeDecorHintPep646Exception
        from beartype._util.hint.pep.proposal.pep646692 import (
            make_hint_pep646_tuple_unpacked_prefix)
        from beartype_test.a00_unit.data.pep.data_pep646 import (
            tuple_fixed_empty_unpacked_prefix,
            Ts_unpacked,
            Us_unpacked,
        )

        # ....................{ LOCALS                     }....................
        # Extend this list with PEP 646-compliant valid type parameter mapping
        # cases.
        typearg_mappings_valid.extend((
            # A single PEP 646-compliant unpacked type variable tuple maps to
            # a single PEP 646-compliant unpacked child tuple hint subscripted
            # by the empty tuple (signifying zero child hints).
            (
                (Ts_unpacked,),
                (),
                {Ts_unpacked: tuple_fixed_empty_unpacked_prefix,},
            ),

            # A PEP 484-compliant type variable followed by a PEP 646-compliant
            # unpacked type variable tuple maps to a single child hint followed
            # by a PEP 646-compliant unpacked child tuple hint subscripted
            # by the empty tuple (signifying zero child hints).
            (
                (T, Ts_unpacked,),
                (int,),
                {T: int, Ts_unpacked: tuple_fixed_empty_unpacked_prefix,},
            ),

            # A PEP 646-compliant unpacked type variable tuple followed by a PEP
            # 484-compliant type variable maps to a PEP 646-compliant unpacked
            # child tuple hint subscripted by the empty tuple (signifying zero
            # child hints) followed by a single child hint.
            #
            # Note that this is simply the reverse order of the type parameters
            # in the prior case, which fascinatingly changes nothing. I'm tired.
            (
                (Ts_unpacked, T,),
                (int,),
                {T: int, Ts_unpacked: tuple_fixed_empty_unpacked_prefix,},
            ),

            # A PEP 484-compliant type variable followed by a PEP 646-compliant
            # unpacked type variable tuple maps to exactly two child hints.
            (
                (T, Ts_unpacked,),
                (str, bytes,),
                {T: str, Ts_unpacked: bytes,},
            ),

            # A PEP 646-compliant unpacked type variable tuple followed by a
            # PEP 484-compliant type variable maps to exactly two child hints.
            #
            # Note that this is simply the reverse order of the type parameters
            # in the prior case, which actually changes something for once. \o/
            (
                (Ts_unpacked, T,),
                (str, bytes,),
                {Ts_unpacked: str, T: bytes,},
            ),

            # Two PEP 484-compliant type variables followed by a PEP
            # 646-compliant unpacked type variable tuple followed by two PEP
            # 484-compliant type variables maps to four or more child hints.
            (
                (S, T, Ts_unpacked, U, V,),
                (bool, int, float, complex, str, bytes,),
                {
                    S: bool,
                    T: int,
                    Ts_unpacked: make_hint_pep646_tuple_unpacked_prefix((
                        float, complex,)),
                    U: str,
                    V: bytes,
                },
            ),
        ))

        # Extend this list with PEP 646-compliant invalid type parameter
        # mapping cases.
        typearg_mappings_invalid.extend((
            # Assert that this factory raises the expected exception when passed
            # two PEP 646-compliant unpacked type parameters interspersed with
            # an arbitrary number of PEP 484-compliant type variables.
            (
                (S, Ts_unpacked, Us_unpacked, T,),
                (float, bool,),
                BeartypeDecorHintPep484612646Exception,
            ),
        ))
    # Else, the active Python interpreter targets Python < 3.11 and thus fails
    # to support PEP 646.

    # ....................{ PASS                           }....................
    # For each valid type parameter mapping case...
    for hints_typearg, hints_child, typearg_to_hint_expected in (
        typearg_mappings_valid):
        # Dictionary mapping these type parameters to child hints.
        typearg_to_hint = _make_hint_pep484612646_typearg_to_hint(
            # Pretend these type parameters parametrized a valid type hint.
            # Since this factory only uses this hint to construct readable
            # exception messages, the value of this hint is irrelevant for
            # testing purposes.
            None,
            hints_typearg,
            hints_child,
        )

        # Assert that this factory produced the expected output dictionary.
        assert typearg_to_hint == typearg_to_hint_expected

    # ....................{ FAIL                           }....................
    # For each invalid type parameter mapping case...
    for hints_typearg, hints_child, exception_type in typearg_mappings_invalid:
        # Assert that this factory raises the expected type of exception when
        # passed these input tuples.
        with raises(exception_type):
            _make_hint_pep484612646_typearg_to_hint(
                None, hints_typearg, hints_child)

# ....................{ TESTS ~ reduce                     }....................
def test_reduce_hint_pep484612646_subbed_typeargs_to_hints() -> None:
    '''
    Test the private
    :mod:`beartype._check.convert._reduce._pep.redpep484612646.reduce_hint_pep484612646_subbed_typeargs_to_hints`
    reducer.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep484612646Exception
    from beartype.typing import Generic
    from beartype._check.convert._reduce._pep.redpep484612646 import (
        reduce_hint_pep484612646_subbed_typeargs_to_hints)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12
    from beartype_test.a00_unit.data.pep.data_pep484 import (
        S,
        T,
    )
    from pytest import raises

    # ....................{ PEP 484                        }....................
    # Assert that this reducer reduces the PEP 484-compliant "typing.Generic"
    # superclass subscripted by only type variables to simply that superclass.
    assert reduce_hint_pep484612646_subbed_typeargs_to_hints(
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
            unit_test_reduce_hint_pep484612646_subbed_typeargs_to_hints_for_pep695)

        # Perform this test.
        unit_test_reduce_hint_pep484612646_subbed_typeargs_to_hints_for_pep695()
    # Else, this interpreter targets Python < 3.12 and thus fails to support PEP
    # 695.

    # ....................{ FAIL                           }....................
    # Assert this reducer raises the expected exception when the passed object
    # is *NOT* a PEP 484- or 646-compliant type parameter.
    with raises(BeartypeDecorHintPep484612646Exception):
        reduce_hint_pep484612646_subbed_typeargs_to_hints(
            'In thy devastating omnipotence,')
