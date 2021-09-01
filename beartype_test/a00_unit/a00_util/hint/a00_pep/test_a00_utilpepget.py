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
    from pytest import raises

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

# ....................{ TESTS ~ origin : type             }....................
def test_get_hint_pep_type_origin_isinstanceable() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_origin_type_isinstanceable`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintPepException
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_origin_type_isinstanceable)
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)
    from pytest import raises

    # Assert this getter...
    for hint_pep_meta in HINTS_PEP_META:
        # Returns the expected type origin for all PEP-compliant type hints
        # originating from an origin type.
        if hint_pep_meta.stdlib_type is not None:
            assert get_hint_pep_origin_type_isinstanceable(hint_pep_meta.hint) is (
                hint_pep_meta.stdlib_type)
        # Raises the expected exception for all other hints.
        else:
            with raises(BeartypeDecorHintPepException):
                get_hint_pep_origin_type_isinstanceable(hint_pep_meta.hint)

    # Assert this getter raises the expected exception for non-PEP-compliant
    # type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        with raises(BeartypeDecorHintPepException):
            get_hint_pep_origin_type_isinstanceable(not_hint_pep)


def test_get_hint_pep_type_origin_stdlib_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_type_origin_isinstanceable_or_none`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintPepException
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_type_origin_isinstanceable_or_none)
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)
    from pytest import raises

    # Assert this getter returns the expected type origin for all PEP-compliant
    # type hints.
    for hint_pep_meta in HINTS_PEP_META:
        assert get_hint_pep_type_origin_isinstanceable_or_none(hint_pep_meta.hint) is (
            hint_pep_meta.stdlib_type)

    # Assert this getter raises the expected exception for non-PEP-compliant
    # type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        with raises(BeartypeDecorHintPepException):
            get_hint_pep_type_origin_isinstanceable_or_none(not_hint_pep)

# ....................{ TESTS ~ kind : typevar            }....................
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
