#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-compliant type hint getter** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.utilpepget` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS ~ attr                       }....................
def test_get_hint_pep_args() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_args`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.typing import Tuple
    from beartype._util.hint.pep.utilpepget import (
        _HINT_ARGS_EMPTY_TUPLE,
        get_hint_pep_args,
    )
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import HINTS_PEP_META

    # ....................{ PASS                           }....................
    # For each PEP-compliant hint, assert this getter returns...
    for hint_pep_meta in HINTS_PEP_META:
        # Tuple of all arguments subscripting this hint.
        hint_args = get_hint_pep_args(hint_pep_meta.hint)
        assert isinstance(hint_args, tuple)

        # For subscripted hints, one or more arguments.
        if hint_pep_meta.is_args:
            assert hint_args
        # For non-argumentative hints, *NO* arguments.
        else:
            assert hint_args == ()

    # ....................{ PASS ~ pep                     }....................
    #FIXME: Explicitly validate that this getter handles both PEP 484- and 585-
    #compliant empty tuples by returning "_HINT_ARGS_EMPTY_TUPLE" as expected,
    #please. This is sufficiently critical that we *NEED* to ensure this.

    # Assert that this getter when passed a PEP 484-compliant empty tuple type
    # hint returns a tuple containing an empty tuple for disambiguity.
    assert get_hint_pep_args(Tuple[()]) == _HINT_ARGS_EMPTY_TUPLE

    # If Python >= 3.9, the active Python interpreter supports PEP 585. In this
    # case, assert that this getter when passed a PEP 585-compliant empty tuple
    # type hint returns a tuple containing an empty tuple for disambiguity.
    if IS_PYTHON_AT_LEAST_3_9:
        assert get_hint_pep_args(tuple[()]) == _HINT_ARGS_EMPTY_TUPLE

    # ....................{ FAIL                           }....................
    # Assert this getter returns *NO* type variables for non-"typing" hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert get_hint_pep_args(not_hint_pep) == ()


def test_get_hint_pep_typevars() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_typevars`
    getter.
    '''

    # Defer test-specific imports.
    from beartype._data.hint.pep.sign.datapepsigns import HintSignTypeVar
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_typevars,
        get_hint_pep_sign_or_none,
    )
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import HINTS_PEP_META

    # For each PEP-compliant hint, assert this getter returns...
    for hint_pep_meta in HINTS_PEP_META:
        # Tuple of all type variables subscripting this hint.
        hint_typevars = get_hint_pep_typevars(hint_pep_meta.hint)
        assert isinstance(hint_typevars, tuple)

        # For typevared hints, one or more type variables.
        if hint_pep_meta.is_typevars:
            assert hint_typevars
            for hint_typevar in hint_typevars:
                assert get_hint_pep_sign_or_none(hint_typevar) is (
                    HintSignTypeVar)
        # For non-typevared hints, *NO* type variables.
        else:
            assert hint_typevars == ()

    # Assert this getter returns *NO* type variables for non-"typing" hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert get_hint_pep_typevars(not_hint_pep) == ()

# ....................{ TESTS ~ sign                       }....................
def test_get_hint_pep_sign() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_sign` getter.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPepSignException
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign
    from beartype_test.a00_unit.data.hint.data_hint import (
        HINTS_NONPEP, NonpepCustomFakeTyping)
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)
    from pytest import raises

    # Assert this getter returns the expected unsubscripted "typing" attribute
    # for all PEP-compliant type hints associated with such an attribute.
    for hint_pep_meta in HINTS_PEP_META:
        assert get_hint_pep_sign(hint_pep_meta.hint) is hint_pep_meta.pep_sign

    # Assert this getter raises the expected exception for an instance of a
    # class erroneously masquerading as a "typing" class.
    with raises(BeartypeDecorHintPepSignException):
        # Localize this return value to simplify debugging.
        hint_nonpep_sign = get_hint_pep_sign(NonpepCustomFakeTyping())

    # Assert this getter raises the expected exception for non-"typing" hints.
    for hint_nonpep in HINTS_NONPEP:
        with raises(BeartypeDecorHintPepSignException):
            # Localize this return value to simplify debugging.
            hint_nonpep_sign = get_hint_pep_sign(hint_nonpep)

# ....................{ TESTS ~ origin : type              }....................
def test_get_hint_pep_type_isinstanceable() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_origin_type_isinstanceable`
    getter.
    '''

    # Defer test-specific imports.
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
        if hint_pep_meta.isinstanceable_type is not None:
            assert get_hint_pep_origin_type_isinstanceable(hint_pep_meta.hint) is (
                hint_pep_meta.isinstanceable_type)
        # Raises the expected exception for all other hints.
        else:
            with raises(BeartypeDecorHintPepException):
                get_hint_pep_origin_type_isinstanceable(hint_pep_meta.hint)

    # Assert this getter raises the expected exception for non-PEP-compliant
    # type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        with raises(BeartypeDecorHintPepException):
            get_hint_pep_origin_type_isinstanceable(not_hint_pep)


def test_get_hint_pep_type_isinstanceable_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_origin_type_isinstanceable_or_none`
    getter.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_origin_type_isinstanceable_or_none)
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)

    # Assert this getter returns the expected type origin for all PEP-compliant
    # type hints.
    for hint_pep_meta in HINTS_PEP_META:
        assert get_hint_pep_origin_type_isinstanceable_or_none(
            hint_pep_meta.hint) is hint_pep_meta.isinstanceable_type

    # Assert this getter returns "None" for non-PEP-compliant type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert get_hint_pep_origin_type_isinstanceable_or_none(
            not_hint_pep) is None
