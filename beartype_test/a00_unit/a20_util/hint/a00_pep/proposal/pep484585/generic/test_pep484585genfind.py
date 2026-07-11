#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484` and :pep:`585` **generic type hint finder** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep484585.generic.pep484585genfind`
submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# from beartype_test._util.mark.pytskip import skip
# from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS                              }....................
# @skip("Currently brokey. lol <- it's sad, actually")
def test_find_hint_pep484585_generic_args_full() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.pep484585genfind.find_hint_pep484585_generic_args_full`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep484585Exception
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585genfind import (
        find_hint_pep484585_generic_args_full)
    from beartype_test.a00_unit.data.pep.generic.data_pep484generic import (
        Nongeneric,
        Pep484GenericST,
        Pep484GenericSTToUU,
    )
    from beartype_test.a00_unit.data.pep.generic.data_pep585generic import (
        Pep585ListT,
        Pep585SequenceU,
    )
    from beartype_test.a00_unit.data.pep.generic.data_pep484585generic import (
        Pep484585GenericIntTSequenceU,
        Pep484585GenericIntFloatSequenceU,
        Pep484585SequenceUGenericSTListU,
        Pep484585SequenceUGenericIntTListU,
    )
    from beartype_test.a00_unit.data.pep.pep484.data_pep484 import (
        S,
        T,
        U,
    )
    from collections.abc import Sequence
    from pytest import raises
    from typing import Generic

    # ....................{ LOCALS                         }....................
    # List of all generic argument cases, each of which is a 2-tuple of the
    # form "(src_generic, trg_args)" such that:
    # * "src_generic" is a PEP 484- or 585-compliant generic to be passed as the
    #   input "hint" parameter to this getter.
    # * "trg_args" is the output tuple returned by this getter when passed that
    #   input generic.
    PEP484585_GENERIC_ARGS_FULL = [
        # ....................{ PEP ~ 484                  }....................
        (Pep484GenericST, (S, T,)),
        (Pep484GenericST[int, float], (int, float,)),
        (Pep484GenericSTToUU, (S, U, S, T, U)),
        (
            Pep484GenericSTToUU[int, float, complex],
            (int, complex, int, float, complex),
        ),

        # ....................{ PEP ~ 585                  }....................
        (Pep585SequenceU, (U,)),
        (Pep585SequenceU[complex], (complex,)),

        # ....................{ PEP ~ (484|585)            }....................
        (Pep484585GenericIntTSequenceU, (bool, int, T, U,)),
        (
            Pep484585GenericIntTSequenceU[float, complex],
            (bool, int, float, complex,),
        ),
        (Pep484585GenericIntFloatSequenceU, (bool, int, float, U,)),
        (
            Pep484585GenericIntFloatSequenceU[complex],
            (bool, int, float, complex,),
        ),
        (Pep484585SequenceUGenericSTListU, (U, S, T, U,)),
        (
            Pep484585SequenceUGenericSTListU[bool, int, float],
            (bool, int, float, bool,),
        ),
        (Pep484585SequenceUGenericIntTListU, (U, int, T, U,)),
        (
            Pep484585SequenceUGenericIntTListU[bool, float],
            (bool, int, float, bool,),
        ),
    ]

    # List of all generic argument cases, each of which is a 2-tuple of the
    # form "(src_generic, src_base_target, trg_args)" such that:
    # * "src_generic" is a PEP 484- or 585-compliant generic to be passed as the
    #   input "hint" parameter to this getter.
    # * "src_base_target" is a target pseudo-superclass to be passed as the
    #   input "hint_base_target" parameter to this getter.
    # * "trg_args" is the output tuple returned by this getter when passed that
    #   input generic and target pseudo-superclass.
    PEP484585_GENERIC_BASE_TARGET_ARGS_FULL = [
        # ....................{ PEP ~ 484                  }....................
        (Pep484GenericST, Generic, (S, T,)),
        (Pep484GenericST, Generic[S, T], (S, T,)),
        (Pep484GenericST[int, float], Generic, (int, float,)),

        # ....................{ PEP ~ 585                  }....................
        (Pep585SequenceU, Sequence, (U,)),
        (Pep585SequenceU[complex], Sequence, (complex,)),

        # ....................{ PEP ~ (484|585)            }....................
        (Pep484585GenericIntTSequenceU, list, (bool,)),
        (Pep484585GenericIntTSequenceU, Pep484GenericST, (int, T,)),
        (Pep484585GenericIntTSequenceU, Nongeneric, ()),
        (Pep484585GenericIntTSequenceU, Pep585SequenceU, (U,)),
        (
            Pep484585GenericIntTSequenceU[float, complex],
            Pep484GenericST,
            (int, float,),
        ),
        (
            Pep484585GenericIntTSequenceU[float, complex],
            Pep585SequenceU,
            (complex,),
        ),
        (
            Pep484585GenericIntFloatSequenceU,
            Pep484585GenericIntTSequenceU,
            (bool, int, float, U,),
        ),
        (
            Pep484585GenericIntFloatSequenceU[complex],
            Pep484585GenericIntTSequenceU,
            (bool, int, float, complex,),
        ),
        (Pep484585SequenceUGenericSTListU, Pep585SequenceU, (U,)),
        (Pep484585SequenceUGenericSTListU, Pep484GenericST, (S, T)),
        (Pep484585SequenceUGenericSTListU[bool, int, float], list[U], (bool,)),
        (
            Pep484585SequenceUGenericSTListU[bool, int, float],
            Pep484GenericST,
            (int, float),
        ),
        (Pep484585SequenceUGenericIntTListU, Pep585SequenceU, (U,)),
        (Pep484585SequenceUGenericIntTListU, Pep484GenericST, (int, T)),

        #FIXME: *FASCINATING*. These are the only two failing cases left. Let's
        #a-go, QA bros! W000t. Okay. Almost w000t. No is w000ting just yet.
        # (Pep484585SequenceUGenericIntTListU[bool, float], list[U], (bool,)),
        # (
        #     Pep484585SequenceUGenericIntTListU[bool, float],
        #     Pep484GenericST,
        #     (int, float),
        # ),
    ]

    # ....................{ PASS                           }....................
    # Assert that this getter returns the expected tuples for the passed
    # generics, including subscripted and unsubscripted forms of these generics.
    for src_generic, trg_args in PEP484585_GENERIC_ARGS_FULL:
        trg_args_found = find_hint_pep484585_generic_args_full(src_generic)
        assert trg_args == trg_args_found

        # Additionally assert that this getter returns the same tuple when
        # passed the passed generic as the target pseudo-superclass. By
        # definition, any class is the superclass of itself. (Math goes hard.)
        trg_args_found = find_hint_pep484585_generic_args_full(
            src_generic, src_generic)
        assert trg_args == trg_args_found

    # Assert that this getter returns the expected tuples for the passed
    # generics and target pseudo-superclasses of these generics, including
    # subscripted and unsubscripted forms of these generics.
    for src_generic, src_base_target, trg_args in (
        PEP484585_GENERIC_BASE_TARGET_ARGS_FULL):
        trg_args_found = find_hint_pep484585_generic_args_full(
            src_generic, src_base_target)
        assert trg_args == trg_args_found

    # ....................{ FAIL                           }....................
    # Assert that this getter raises the expected exception when passed an
    # object that is *NOT* a PEP 484- or 585-compliant generic.
    with raises(BeartypeDecorHintPep484585Exception):
        find_hint_pep484585_generic_args_full(Nongeneric)

    # Assert that this getter raises the expected exception when passed an
    # PEP 585-compliant generic subscripted by more child hints than this
    # generic was originally parametrized by type parameters.
    with raises(BeartypeDecorHintPep484585Exception):
        find_hint_pep484585_generic_args_full(Pep585ListT[int, str])
