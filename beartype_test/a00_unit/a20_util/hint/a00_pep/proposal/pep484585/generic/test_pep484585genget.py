#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484` and :pep:`585` **generic type hint getter** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget`
submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ getters : args             }....................
def test_get_hint_pep484585_generic_args_full(pep484585_generics) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.pep484585generic.get_hint_pep484585_generic_args_full`
    getter.

    Parameters
    ----------
    pep484585_generics : 'beartype_test.a00_unit.data.hint.pep.proposal._fixture.data_pep484585generic._Pep484585Generics'
        **Generics dataclass** (i.e., object comprising various :pep:`484`- and
        :pep:`585`-compliant :class:`typing.Generic` subclasses).
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep484585Exception
    from beartype.typing import (
        Generic,
        List,
        Sequence,
    )
    from beartype._data.hint.datahinttyping import (
        S,
        T,
        U,
    )
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget import (
        get_hint_pep484585_generic_args_full)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # List of all generic argument cases, each of which is a 2-tuple of the
    # form "(src_generic, trg_args)" such that:
    # * "src_generic" is a PEP 484- or 585-compliant generic to be passed as the
    #   input "hint" parameter to this getter.
    # * "trg_args" is the output tuple returned by this getter when passed that
    #   input generic.
    PEP484585_GENERIC_ARGS_FULL = [
        (pep484585_generics.Pep484GenericST, (S, T,)),
        (pep484585_generics.Pep484GenericST[int, float], (int, float,)),
        (pep484585_generics.Pep484585SequenceU, (U,)),
        (pep484585_generics.Pep484585SequenceU[complex], (complex,)),
        (pep484585_generics.Pep484585GenericSTSequenceU, (bool, int, T, U,)),
        (pep484585_generics.Pep484585GenericIntTSequenceU, (bool, int, float, U,)),
        (pep484585_generics.Pep484585GenericUUST, (U, S, T, U,)),
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
        (pep484585_generics.Pep484GenericST, Generic, (S, T,)),
        (pep484585_generics.Pep484GenericST, Generic[S, T], (S, T,)),
        (pep484585_generics.Pep484GenericST[int, float], Generic, (int, float,)),
        (pep484585_generics.Pep484585SequenceU, Sequence, (U,)),
        (pep484585_generics.Pep484585SequenceU[complex], Sequence, (complex,)),
        (pep484585_generics.Pep484585GenericSTSequenceU, List, (bool,)),
        (pep484585_generics.Pep484585GenericSTSequenceU, pep484585_generics.Pep484GenericST, (int, T,)),
        (pep484585_generics.Pep484585GenericSTSequenceU, pep484585_generics.Nongeneric, ()),
        (pep484585_generics.Pep484585GenericSTSequenceU, pep484585_generics.Pep484585SequenceU, (U,)),
        (
            pep484585_generics.Pep484585GenericIntTSequenceU,
            pep484585_generics.Pep484585GenericSTSequenceU,
            (bool, int, float, U,),
        ),
        (pep484585_generics.Pep484585GenericUUST, pep484585_generics.Pep484585SequenceU, (U,)),
        (pep484585_generics.Pep484585GenericUUST, pep484585_generics.Pep484GenericST, (S, T)),
    ]

    # If the active Python interpreter targets Python >= 3.9 and thus behaves
    # sanely with respect to complex subscripted generics, extend this list with
    # cases covering complex subscripted generics. For unknown and presumably
    # irrelevant reasons, Python 3.8 raises exceptions here. *shrug*
    if IS_PYTHON_AT_LEAST_3_9:
        PEP484585_GENERIC_ARGS_FULL.extend((
            (pep484585_generics.Pep484585GenericSTSequenceU[float, complex], (bool, int, float, complex,)),
            (pep484585_generics.Pep484585GenericIntTSequenceU[complex], (bool, int, float, complex,)),
            (pep484585_generics.Pep484585GenericUUST[bool, int, float], (bool, int, float, bool,)),
            (pep484585_generics.Pep585GenericUIntT, (U, int, T, U,)),
            (pep484585_generics.Pep585GenericUIntT[bool, float], (bool, int, float, bool,)),
        ))

        PEP484585_GENERIC_BASE_TARGET_ARGS_FULL.extend((
            (
                pep484585_generics.Pep484585GenericSTSequenceU[float, complex],
                pep484585_generics.Pep484GenericST,
                (int, float,),
            ),
            (
                pep484585_generics.Pep484585GenericSTSequenceU[float, complex],
                pep484585_generics.Pep484585SequenceU,
                (complex,),
            ),
            (
                pep484585_generics.Pep484585GenericIntTSequenceU[complex],
                pep484585_generics.Pep484585GenericSTSequenceU,
                (bool, int, float, complex,),
            ),
            (
                pep484585_generics.Pep484585GenericUUST[bool, int, float],
                List[U],
                (bool,),
            ),
            (
                pep484585_generics.Pep484585GenericUUST[bool, int, float],
                pep484585_generics.Pep484GenericST,
                (int, float),
            ),
            (pep484585_generics.Pep585GenericUIntT, pep484585_generics.Pep484585SequenceU, (U,)),
            (pep484585_generics.Pep585GenericUIntT, pep484585_generics.Pep484GenericST, (int, T)),
            (pep484585_generics.Pep585GenericUIntT[bool, float], List[U], (bool,)),
            (pep484585_generics.Pep585GenericUIntT[bool, float], pep484585_generics.Pep484GenericST, (int, float)),
        ))

    # ....................{ PASS                           }....................
    # Assert that this getter returns the expected tuples for the passed
    # generics, including subscripted and unsubscripted forms of these generics.
    for src_generic, trg_args in PEP484585_GENERIC_ARGS_FULL:
        assert get_hint_pep484585_generic_args_full(src_generic) == trg_args

        # Additionally assert that this getter returns the same tuple when
        # passed the passed generic as the target pseudo-superclass. By
        # definition, any class is the superclass of itself. (Math goes hard.)
        assert get_hint_pep484585_generic_args_full(
            src_generic, src_generic) == trg_args

    # Assert that this getter returns the expected tuples for the passed
    # generics and target pseudo-superclasses of these generics, including
    # subscripted and unsubscripted forms of these generics.
    for src_generic, src_base_target, trg_args in (
        PEP484585_GENERIC_BASE_TARGET_ARGS_FULL):
        assert get_hint_pep484585_generic_args_full(
            src_generic, src_base_target) == trg_args

    # ....................{ FAIL                           }....................
    # Assert that this getter raises the expected exception when passed an
    # object that is *NOT* a PEP 484- or 585-compliant generic.
    with raises(BeartypeDecorHintPep484585Exception):
        get_hint_pep484585_generic_args_full(pep484585_generics.Nongeneric)

# ....................{ TESTS ~ getters : base             }....................
def test_get_hint_pep484585_generic_bases_unerased(hints_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget.get_hint_pep484585_generic_bases_unerased`
    getter.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPepException
    from beartype._data.hint.pep.sign.datapepsigns import HintSignGeneric
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget import (
        get_hint_pep484585_generic_bases_unerased)
    from beartype._util.hint.pep.utilpeptest import is_hint_pep_type_typing
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from pytest import raises

    # Assert this getter...
    for hint_pep_meta in hints_pep_meta:
        # Returns one or more unerased pseudo-superclasses for PEP-compliant
        # generics.
        if hint_pep_meta.pep_sign is HintSignGeneric:
            hint_pep_bases = get_hint_pep484585_generic_bases_unerased(
                hint_pep_meta.hint)
            assert isinstance(hint_pep_bases, tuple)
            assert hint_pep_bases
        # Raises an exception for concrete PEP-compliant type hints *NOT*
        # defined by the "typing" module.
        elif not is_hint_pep_type_typing(hint_pep_meta.hint):
            with raises(BeartypeDecorHintPepException):
                get_hint_pep484585_generic_bases_unerased(hint_pep_meta.hint)
        # Else, this hint is defined by the "typing" module. In this case, this
        # hint may or may not be implemented as a generic conditionally
        # depending on the current Python version -- especially under the
        # Python < 3.7.0 implementations of the "typing" module, where
        # effectively *EVERYTHING* was internally implemented as a generic.
        # While we could technically correct for this conditionality, doing so
        # would render the resulting code less maintainable for no useful gain.
        # Ergo, we quietly ignore this edge case and get on with actual coding.

    # Assert this getter raises the expected exception for non-PEP-compliant
    # type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        with raises(BeartypeDecorHintPepException):
            assert get_hint_pep484585_generic_bases_unerased(not_hint_pep)


def test_get_hint_pep484585_generic_base_in_module_first() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget.get_hint_pep484585_generic_base_in_module_first`
    finder.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep484585Exception
    from beartype.typing import Generic
    from beartype._data.hint.datahinttyping import T
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget import (
        get_hint_pep484585_generic_base_in_module_first)
    from pytest import raises

    # ....................{ CLASSES                        }....................
    class ToWhichThisClosingNight(object):
        '''
        Arbitrary superclass.
        '''

        pass


    class OfTheDyingYear(Generic[T], str, ToWhichThisClosingNight):
        '''
        Arbitrary generic subclassing:

        * The generic superclass subscripted by a type variable.
        * An arbitrary type *not* defined by the :mod:`beartype_test` package.
        * An arbitrary type defined by the :mod:`beartype_test` package.
        '''

        pass

    # ....................{ LOCALS                         }....................
    # Tuple of all generic type hints to be tested below, including...
    TEST_GENERICS = (
        # An unsubscripted generic.
        OfTheDyingYear,
        # A subscripted generic (subscripted by an arbitrary type).
        OfTheDyingYear[int],
    )

    # ....................{ ASSERTS                        }....................
    # For each such generic type hint...
    for test_generic in TEST_GENERICS:
        # ....................{ PASS                       }....................
        # Assert that this finder passed this generic returns the first unerased
        # superclass of this generic declared by this package.
        assert get_hint_pep484585_generic_base_in_module_first(
            hint=test_generic, module_name='beartype_test') is (
            ToWhichThisClosingNight)

        # ....................{ FAIL                       }....................
        # Assert that this finder passed this generic and the name of a
        # hypothetical module guaranteed *NOT* to exist raises the expected
        # exception.
        with raises(BeartypeDecorHintPep484585Exception):
            get_hint_pep484585_generic_base_in_module_first(
                hint=test_generic,
                module_name='will_be.the.dome_of.a_vast_sepulchre',
            )

# ....................{ TESTS ~ getters : type             }....................
def test_get_hint_pep484585_generic_type_or_none(hints_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget.get_hint_pep484585_generic_type_or_none`
    getter.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype._data.hint.pep.sign.datapepsigns import HintSignGeneric
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget import (
        get_hint_pep484585_generic_type_or_none)

    # Assert this getter returns the expected type origin for all
    # PEP-compliant type hint generics. While we could support non-generics as
    # well, there's little benefit and significant costs to doing so. Instead,
    # we assert this getter only returns the expected type origin for a small
    # subset of type hints.
    for hint_pep_meta in hints_pep_meta:
        if hint_pep_meta.pep_sign is HintSignGeneric:
            assert get_hint_pep484585_generic_type_or_none(
                hint_pep_meta.hint) is hint_pep_meta.generic_type

    #FIXME: Uncomment if we ever want to exercise extreme edge cases. *shrug*
    # from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    #
    # # Assert this getter returns the expected type origin for all
    # # PEP-compliant type hints.
    # for hint_pep_meta in HINTS_PEP_META:
    #     assert get_hint_pep484585_generic_type_or_none(
    #         hint_pep_meta.hint) is hint_pep_meta.generic_type
    #
    # # Assert this getter raises the expected exception for non-PEP-compliant
    # # type hints.
    # for not_hint_pep in NOT_HINTS_PEP:
    #     assert get_hint_pep484585_generic_type_or_none(not_hint_pep) is None
