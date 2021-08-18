#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-compliant type hint getter** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.utilpepget` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# from beartype_test.util.mark.pytskip import skip_if_python_version_less_than
from pytest import raises

# ....................{ TESTS ~ sign                      }....................
def test_get_hint_pep_sign() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_sign` getter.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintPepSignException
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign
    from beartype_test.a00_unit.data.hint.data_hint import (
        HINTS_NONPEP, NonPepCustomFakeTyping)
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)

    # Assert this getter returns the expected unsubscripted "typing" attribute
    # for all PEP-compliant type hints associated with such an attribute.
    for hint_pep_meta in HINTS_PEP_META:
        assert get_hint_pep_sign(hint_pep_meta.hint) == (
            hint_pep_meta.pep_sign)

    # Assert this getter raises the expected exception for an instance of a
    # class erroneously masquerading as a "typing" class.
    with raises(BeartypeDecorHintPepSignException):
        # Localize this return value to simplify debugging.
        hint_nonpep_sign = get_hint_pep_sign(NonPepCustomFakeTyping())

    # Assert this getter raises the expected exception for non-"typing" hints.
    for hint_nonpep in HINTS_NONPEP:
        with raises(BeartypeDecorHintPepSignException):
            # Localize this return value to simplify debugging.
            hint_nonpep_sign = get_hint_pep_sign(hint_nonpep)

# ....................{ TESTS ~ origin : generic          }....................
def test_get_hint_pep_generic_type_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_generic_type_or_none`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype._data.hint.pep.sign.datapepsigns import HintSignGeneric
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_generic_type_or_none)
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)

    # Assert this getter returns the expected type origin for all
    # PEP-compliant type hint generics. While we could support non-generics as
    # well, there's little benefit and significant costs to doing so. Instead,
    # we assert this getter only returns the expected type origin for a small
    # subset of type hints.
    for hint_pep_meta in HINTS_PEP_META:
        if hint_pep_meta.pep_sign is HintSignGeneric:
            assert get_hint_pep_generic_type_or_none(
                hint_pep_meta.hint) is hint_pep_meta.generic_type

    #FIXME: Uncomment if we ever want to exercise extreme edge cases. *shrug*
    # from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_7
    # from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    #
    # # Assert this getter returns the expected type origin for all
    # # PEP-compliant type hints.
    # for hint_pep_meta in HINTS_PEP_META:
    #     assert get_hint_pep_generic_type_or_none(
    #         hint_pep_meta.hint) is hint_pep_meta.generic_type
    #
    # # Assert this getter raises the expected exception for non-PEP-compliant
    # # type hints.
    # for not_hint_pep in NOT_HINTS_PEP:
    #     assert get_hint_pep_generic_type_or_none(not_hint_pep) is None

# ....................{ TESTS ~ origin : stdlib           }....................
def test_get_hint_pep_type_origin_stdlib() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_type_stdlib`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintPepException
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_type_stdlib)
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)

    # Assert this getter...
    for hint_pep_meta in HINTS_PEP_META:
        # Returns the expected type origin for all PEP-compliant type hints
        # originating from an origin type.
        if hint_pep_meta.stdlib_type is not None:
            assert get_hint_pep_type_stdlib(hint_pep_meta.hint) is (
                hint_pep_meta.stdlib_type)
        # Raises the expected exception for all other hints.
        else:
            with raises(BeartypeDecorHintPepException):
                get_hint_pep_type_stdlib(hint_pep_meta.hint)

    # Assert this getter raises the expected exception for non-PEP-compliant
    # type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        with raises(BeartypeDecorHintPepException):
            get_hint_pep_type_stdlib(not_hint_pep)


def test_get_hint_pep_type_origin_stdlib_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_type_stdlib_or_none`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintPepException
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_type_stdlib_or_none)
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)

    # Assert this getter returns the expected type origin for all PEP-compliant
    # type hints.
    for hint_pep_meta in HINTS_PEP_META:
        assert get_hint_pep_type_stdlib_or_none(hint_pep_meta.hint) is (
            hint_pep_meta.stdlib_type)

    # Assert this getter raises the expected exception for non-PEP-compliant
    # type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        with raises(BeartypeDecorHintPepException):
            get_hint_pep_type_stdlib_or_none(not_hint_pep)

# ....................{ TESTS ~ subtype : generic         }....................
def test_get_hint_pep_generic_bases_unerased() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_generic_bases_unerased`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintPepException
    from beartype._data.hint.pep.sign.datapepsigns import HintSignGeneric
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_generic_bases_unerased)
    from beartype._util.hint.pep.utilpeptest import is_hint_pep_type_typing
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import HINTS_PEP_META

    # Assert this getter...
    for hint_pep_meta in HINTS_PEP_META:
        # Returns one or more unerased pseudo-superclasses for PEP-compliant
        # generics.
        if hint_pep_meta.pep_sign is HintSignGeneric:
            hint_pep_bases = get_hint_pep_generic_bases_unerased(
                hint_pep_meta.hint)
            assert isinstance(hint_pep_bases, tuple)
            assert hint_pep_bases
        # Raises an exception for concrete PEP-compliant type hints *NOT*
        # defined by the "typing" module.
        elif not is_hint_pep_type_typing(hint_pep_meta.hint):
            with raises(BeartypeDecorHintPepException):
                get_hint_pep_generic_bases_unerased(hint_pep_meta.hint)
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
            assert get_hint_pep_generic_bases_unerased(not_hint_pep) is None

# ....................{ TESTS ~ subtype : typevar         }....................
def test_get_hint_pep_typevars() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_typevars`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_typevars
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import HINTS_PEP_META

    # Assert this getter returns...
    for hint_pep_meta in HINTS_PEP_META:
        # Tuple of all tupe variables returned by this function.
        hint_pep_typevars = get_hint_pep_typevars(hint_pep_meta.hint)

        # Returns one or more type variables for typevared PEP-compliant type
        # hints.
        if hint_pep_meta.is_typevared:
            assert isinstance(hint_pep_typevars, tuple)
            assert hint_pep_typevars
        # *NO* type variables for untypevared PEP-compliant type hints.
        else:
            assert hint_pep_typevars == ()

    # Assert this getter returns *NO* type variables for non-"typing" hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert get_hint_pep_typevars(not_hint_pep) == ()
