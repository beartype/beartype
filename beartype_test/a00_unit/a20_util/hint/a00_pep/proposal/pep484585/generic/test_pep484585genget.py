#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
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
# from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS ~ base                       }....................
def test_get_hint_pep484585_generic_base_extrinsic_sign_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget.get_hint_pep484585_generic_base_extrinsic_sign_or_none`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.typing import (
        Generic,
        NamedTuple,
        TypedDict,
    )
    from beartype._data.typing.datatyping import T
    from beartype._data.hint.sign.datahintsigns import (
        HintSignNamedTuple,
        HintSignTypedDict,
    )
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget import (
        get_hint_pep484585_generic_base_extrinsic_sign_or_none)

    # ....................{ CLASSES                        }....................
    #FIXME: Useful docstring for when we use the generics defined below.
    # Python < 3.11 fails to support multiple inheritance in concert with the
    # :class:`typing.Generic` superclass and either of the
    # :class:`typing.NamedTuple` or :class:`typing.TypedDict` superclasses. Ergo,
    # Python < 3.11 fails to support either generic named tuples *or* generic
    # typed dictionaries. Ergo, Python < 3.11 fails to support this unit test.

    #FIXME: When we get around to supporting this, note that "typing.NamedTuple"
    #*ONLY* supports multiple inheritance in partnership with "typing.Generic"
    #under Python >= 3.11. Under older Python versions, the "typing" module
    #raises the following exception on attempting to define such subclasses:
    #    TypeError: Multiple inheritance with NamedTuple is not supported
    # class GenericNamedTuple(NamedTuple, Generic[T]):
    #     '''
    #     Arbitrary **generic named tuple** (i.e., type subclassing both the
    #     :pep:`484`-compliant :class:`typing.Generic` superclass *and* the
    #     :pep:`484`-compliant :class:`typing.NamedTuple` superclass).
    #     '''
    #
    #     generic_item: T

    #FIXME: Nice, but currently unused.
    # class GenericTypedDict(TypedDict, Generic[T]):
    #     '''
    #     Arbitrary **generic typed dictionary** (i.e., type subclassing both the
    #     :pep:`484`-compliant :class:`typing.Generic` superclass *and* the
    #     :pep:`589`-compliant :class:`typing.TypedDict` superclass).
    #     '''
    #
    #     generic_item: T

    # ....................{ LOCALS                         }....................
    # Tuple of 2-tuples "(hint_base, hint_extrinsic_sign)" where:
    # * "hint_base" is a valid pseudo-superclass of a PEP 484- or 585-compliant
    #   generic.
    # * "hint_extrinsic_sign" is either:
    #   * If that pseudo-superclass is extrinsic, the sign uniquely identifying
    #     that pseudo-superclass.
    #   * If that pseudo-superclass is intrinsic, "None".
    TEST_GENERIC_BASES_EXTRINSIC_SIGNS = (
        # Intrinsic PEP 484-compliant "typing.Generic" pseudo-superclass in both
        # subscripted and unsubscripted forms.
        (Generic, None),
        (Generic[T], None),

        # Extrinsic PEP 484-compliant "typing.NamedTuple" pseudo-superclass.
        (NamedTuple, HintSignNamedTuple),

        # Extrinsic PEP 589-compliant "typing.TypedDict" pseudo-superclass.
        (TypedDict, HintSignTypedDict),
    )

    # ....................{ ASSERTS                        }....................
    # For each such unsubscripted generic and additional non-generic sign...
    for hint_base, hint_extrinsic_sign in TEST_GENERIC_BASES_EXTRINSIC_SIGNS:
        # Assert that this getter passed this generic returns this sign.
        assert get_hint_pep484585_generic_base_extrinsic_sign_or_none(
            hint_base) is hint_extrinsic_sign


def test_get_hint_pep484585_generic_bases_unerased(hints_piths_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget.get_hint_pep484585_generic_bases_unerased`
    getter.

    Parameters
    ----------
    hints_piths_pep_meta : List[beartype_test.a00_unit.data.hint.metadata.pith.data_hintpithmeta.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPepException
    from beartype._data.hint.sign.datahintsignset import HINT_SIGNS_GENERIC
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget import (
        get_hint_pep484585_generic_bases_unerased)
    from beartype._util.hint.pep.utilpeptest import is_hint_pep_type_typing
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from pytest import raises

    # For each PEP-compliant hint to be tested...
    for hint_pep_meta in hints_piths_pep_meta:
        # If this is a generic hint, assert that this getter returns the
        # expected unerased pseudo-superclasses of this generic.
        if hint_pep_meta.pep_sign in HINT_SIGNS_GENERIC:
            hint_pep_bases = get_hint_pep484585_generic_bases_unerased(
                hint_pep_meta.hint)
            assert isinstance(hint_pep_bases, tuple)
            assert hint_pep_bases
        # Else, this is *NOT* a generic hint.
        #
        # If this hint is *NOT* defined by the "typing" module, assert that this
        # getter raises the expected exception.
        elif not is_hint_pep_type_typing(hint_pep_meta.hint):
            # print(f'hint_pep_meta: {repr(hint_pep_meta)}')
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
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep484585Exception
    from beartype.typing import Generic
    from beartype._data.typing.datatyping import T
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
            hint=test_generic, module_names=frozenset(('beartype_test',))) is (
            ToWhichThisClosingNight)

        # ....................{ FAIL                       }....................
        # Assert that this finder passed this generic and the name of a
        # hypothetical module guaranteed *NOT* to exist raises the expected
        # exception.
        with raises(BeartypeDecorHintPep484585Exception):
            get_hint_pep484585_generic_base_in_module_first(
                hint=test_generic,
                module_names=frozenset((
                    'will_be.the.dome_of.a_vast_sepulchre',)),
            )

# ....................{ TESTS ~ type                       }....................
def test_get_hint_pep484585_generic_unsubbed_type_or_none(hints_piths_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget.get_hint_pep484585_generic_unsubbed_type_or_none`
    getter.

    Parameters
    ----------
    hints_piths_pep_meta : List[beartype_test.a00_unit.data.hint.metadata.pith.data_hintpithmeta.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype._data.hint.sign.datahintsigns import HintSignPep484585GenericUnsubbed
    from beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget import (
        get_hint_pep484585_generic_unsubbed_type_or_none)

    # Assert this getter returns the expected type origin for all
    # PEP-compliant type hint generics. While we could support non-generics as
    # well, there's little benefit and significant costs to doing so. Instead,
    # we assert this getter only returns the expected type origin for a small
    # subset of type hints.
    for hint_pep_meta in hints_piths_pep_meta:
        if hint_pep_meta.pep_sign is HintSignPep484585GenericUnsubbed:
            assert get_hint_pep484585_generic_unsubbed_type_or_none(
                hint_pep_meta.hint) is hint_pep_meta.generic_type

    #FIXME: Uncomment if we ever want to exercise extreme edge cases. *shrug*
    # from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    #
    # # Assert this getter returns the expected type origin for all
    # # PEP-compliant type hints.
    # for hint_pep_meta in HINTS_PEP_META:
    #     assert get_hint_pep484585_generic_unsubbed_type_or_none(
    #         hint_pep_meta.hint) is hint_pep_meta.generic_type
    #
    # # Assert this getter raises the expected exception for non-PEP-compliant
    # # type hints.
    # for not_hint_pep in NOT_HINTS_PEP:
    #     assert get_hint_pep484585_generic_unsubbed_type_or_none(not_hint_pep) is None
