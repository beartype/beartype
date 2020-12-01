#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint getter utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.utilhintpepget` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ TESTS ~ sign                      }....................
def test_get_hint_pep_sign_pass() -> None:
    '''
    Test successful usage of the
    :func:`beartype._util.hint.pep.utilhintpepget.get_hint_pep_sign` getter.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpepget import get_hint_pep_sign
    from beartype_test.unit.data.hint.pep.data_hintpep import HINTS_PEP_META

    # Assert this getter returns the expected unsubscripted "typing" attribute
    # for all PEP-compliant type hints associated with such an attribute.
    for hint_pep_meta in HINTS_PEP_META:
        assert get_hint_pep_sign(hint_pep_meta.hint) == (
            hint_pep_meta.pep_sign)


def test_get_hint_pep_sign_fail() -> None:
    '''
    Test unsuccessful usage of the
    :func:`beartype._util.hint.pep.utilhintpepget.get_hint_pep_sign` getter.
    '''

    # Defer heavyweight imports.
    from beartype.roar import (
        BeartypeDecorHintPepException,
        BeartypeDecorHintPepSignException,
    )
    from beartype._util.hint.pep.utilhintpepget import get_hint_pep_sign
    from beartype_test.unit.data.hint.data_hint import (
        NOT_HINTS_PEP, NonPepCustomFakeTyping)

    # Assert this getter raises the expected exception for an instance of a
    # class erroneously masquerading as a "typing" class.
    with raises(BeartypeDecorHintPepSignException):
        # Localize this return value to simplify debugging.
        hint_pep_sign = get_hint_pep_sign(NonPepCustomFakeTyping())

    # Assert this getter raises the expected exception for non-"typing" hints.
    for not_hint_pep in NOT_HINTS_PEP:
        with raises(BeartypeDecorHintPepException):
            # Localize this return value to simplify debugging.
            hint_pep_sign = get_hint_pep_sign(not_hint_pep)

# ....................{ TESTS ~ type                      }....................
def test_get_hint_pep_type_origin() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpepget.get_hint_pep_type_origin`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintPepException
    from beartype._util.hint.pep.utilhintpepget import (
        get_hint_pep_type_origin)
    from beartype_test.unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.unit.data.hint.pep.data_hintpep import HINTS_PEP_META

    # Assert this getter...
    for hint_pep_meta in HINTS_PEP_META:
        # Returns the expected type origin for all PEP-compliant type hints
        # originating from an origin type.
        if hint_pep_meta.type_origin is not None:
            assert get_hint_pep_type_origin(hint_pep_meta.hint) is (
                hint_pep_meta.type_origin)
        # Raises the expected exception for all other hints.
        else:
            with raises(BeartypeDecorHintPepException):
                get_hint_pep_type_origin(hint_pep_meta.hint)

    # Assert this getter raises the expected exception for non-PEP-compliant
    # type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        with raises(BeartypeDecorHintPepException):
            get_hint_pep_type_origin(not_hint_pep)


def test_get_hint_pep_type_origin_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpepget.get_hint_pep_type_origin_or_none`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintPepException
    from beartype._util.hint.pep.utilhintpepget import (
        get_hint_pep_type_origin_or_none)
    from beartype_test.unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.unit.data.hint.pep.data_hintpep import HINTS_PEP_META

    # Assert this getter returns the expected type origin for all PEP-compliant
    # type hints.
    for hint_pep_meta in HINTS_PEP_META:
        assert get_hint_pep_type_origin_or_none(hint_pep_meta.hint) is (
            hint_pep_meta.type_origin)

    # Assert this getter raises the expected exception for non-PEP-compliant
    # type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        with raises(BeartypeDecorHintPepException):
            get_hint_pep_type_origin_or_none(not_hint_pep)

# ....................{ TESTS ~ subtype : generic         }....................
def test_get_hint_pep_generic_bases_unerased() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpepget.get_hint_pep_generic_bases_unerased`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintPepException
    from beartype._util.hint.pep.utilhintpepget import (
        get_hint_pep_generic_bases_unerased)
    from beartype._util.hint.pep.utilhintpeptest import is_hint_pep_class_typing
    from beartype_test.unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.unit.data.hint.pep.data_hintpep import HINTS_PEP_META
    from typing import Generic

    # Assert this getter...
    for hint_pep_meta in HINTS_PEP_META:
        # Returns one or more unerased pseudo-superclasses for PEP-compliant
        # generics.
        if hint_pep_meta.pep_sign is Generic:
            hint_pep_bases = get_hint_pep_generic_bases_unerased(
                hint_pep_meta.hint)
            assert isinstance(hint_pep_bases, tuple)
            assert hint_pep_bases
        # Raises an exception for concrete PEP-compliant type hints *NOT*
        # defined by the "typing" module.
        elif not is_hint_pep_class_typing(hint_pep_meta.hint):
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
    :func:`beartype._util.hint.pep.utilhintpepget.get_hint_pep_typevars`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpepget import get_hint_pep_typevars
    from beartype_test.unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.unit.data.hint.pep.data_hintpep import HINTS_PEP_META

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
