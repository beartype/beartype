#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484` and :pep:`585` **generic type hint utility unit
tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep484585.utilpep484585generic` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ testers                    }....................
def test_is_hint_pep484585_generic() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.utilpep484585generic.is_hint_pep484585_generic`
    tester.
    '''

    # Defer test-specific imports.
    from beartype._data.hint.pep.sign.datapepsigns import HintSignGeneric
    from beartype._util.hint.pep.proposal.pep484585.utilpep484585generic import (
        is_hint_pep484585_generic)
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)

    # Assert this tester:
    # * Accepts generic PEP 484-compliant generics.
    # * Rejects concrete PEP-compliant type hints.
    for hint_pep_meta in HINTS_PEP_META:
        assert is_hint_pep484585_generic(hint_pep_meta.hint) is (
            hint_pep_meta.pep_sign is HintSignGeneric)

    # Assert this tester rejects non-PEP-compliant type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert is_hint_pep484585_generic(not_hint_pep) is False

# ....................{ TESTS ~ getters                    }....................
def test_get_hint_pep484585_generic_type_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.utilpep484585generic.get_hint_pep484585_generic_type_or_none`
    getter.
    '''

    # Defer test-specific imports.
    from beartype._data.hint.pep.sign.datapepsigns import HintSignGeneric
    from beartype._util.hint.pep.proposal.pep484585.utilpep484585generic import (
        get_hint_pep484585_generic_type_or_none)
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)

    # Assert this getter returns the expected type origin for all
    # PEP-compliant type hint generics. While we could support non-generics as
    # well, there's little benefit and significant costs to doing so. Instead,
    # we assert this getter only returns the expected type origin for a small
    # subset of type hints.
    for hint_pep_meta in HINTS_PEP_META:
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


def test_get_hint_pep484585_generic_bases_unerased() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.utilpep484585generic.get_hint_pep484585_generic_bases_unerased`
    getter.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPepException
    from beartype._data.hint.pep.sign.datapepsigns import HintSignGeneric
    from beartype._util.hint.pep.proposal.pep484585.utilpep484585generic import (
        get_hint_pep484585_generic_bases_unerased)
    from beartype._util.hint.pep.utilpeptest import is_hint_pep_type_typing
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import HINTS_PEP_META
    from pytest import raises

    # Assert this getter...
    for hint_pep_meta in HINTS_PEP_META:
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

# ....................{ TESTS ~ finders                    }....................
def test_find_hint_pep484585_generic_module_base_first() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.utilpep484585generic.find_hint_pep484585_generic_module_base_first`
    finder.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep484585Exception
    from beartype.typing import (
        Generic,
        TypeVar,
    )
    from beartype._util.hint.pep.proposal.pep484585.utilpep484585generic import (
        find_hint_pep484585_generic_module_base_first)
    from pytest import raises

    # Arbitrary type variable referenced below.
    T = TypeVar('T')

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
        assert find_hint_pep484585_generic_module_base_first(
            hint=test_generic, module_name='beartype_test') is (
            ToWhichThisClosingNight)

        # ....................{ FAIL                       }....................
        # Assert that this finder passed this generic and the name of a
        # hypothetical module guaranteed *NOT* to exist raises the expected
        # exception.
        with raises(BeartypeDecorHintPep484585Exception):
            find_hint_pep484585_generic_module_base_first(
                hint=test_generic,
                module_name='will_be.the.dome_of.a_vast_sepulchre',
            )
