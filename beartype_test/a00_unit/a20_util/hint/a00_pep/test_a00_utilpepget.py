#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
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
def test_get_hint_pep_args(hints_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_args`
    getter.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.typing import Tuple
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_args,
        _HINT_ARGS_EMPTY_TUPLE,
    )
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP

    # ....................{ ASSERTS                        }....................
    # For each PEP-compliant hint, assert this getter returns...
    for hint_pep_meta in hints_pep_meta:
        # Tuple of all arguments subscripting this hint.
        hint_args = get_hint_pep_args(hint_pep_meta.hint)
        assert isinstance(hint_args, tuple)

        # For subscripted hints, one or more arguments.
        if hint_pep_meta.is_args:
            assert hint_args
        # For non-argumentative hints, *NO* arguments.
        else:
            assert hint_args == ()

    # Assert this getter returns *NO* type variables for non-"typing" hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert get_hint_pep_args(not_hint_pep) == ()

    # ....................{ ASSERTS ~ tuple                }....................
    # Explicitly validate that this getter handles both PEP 484- and 585-
    # compliant empty tuples by returning "_HINT_ARGS_EMPTY_TUPLE" as expected.

    # Assert that this getter when passed a PEP 484-compliant empty tuple type
    # hint returns a tuple containing an empty tuple for disambiguity.
    assert get_hint_pep_args(Tuple[()]) == _HINT_ARGS_EMPTY_TUPLE

    # Assert that this getter when passed a PEP 585-compliant empty tuple type
    # hint returns a tuple containing an empty tuple for disambiguity.
    assert get_hint_pep_args(tuple[()]) == _HINT_ARGS_EMPTY_TUPLE


def test_get_hint_pep_typevars(hints_pep_meta) -> None:
    '''
    Test the :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_typevars`
    getter.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._data.hint.pep.sign.datapepsigns import HintSignTypeVar
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_typevars,
        get_hint_pep_sign_or_none,
    )
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP

    # ....................{ ASSERTS                        }....................
    # For each PEP-compliant test hint...
    for hint_pep_meta in hints_pep_meta:
        # Tuple of all type variables discovered by this getter.
        hint_typevars = get_hint_pep_typevars(hint_pep_meta.hint)
        assert isinstance(hint_typevars, tuple)

        # Assert that all items of this tuple are actually type variables.
        for hint_typevar in hint_typevars:
            assert get_hint_pep_sign_or_none(hint_typevar) is HintSignTypeVar

        # If this hint is parametrized by one or more type variables...
        if hint_pep_meta.is_typevars:
            # Assert that this getter returns one or more type variables.
            assert hint_typevars

            # If the exact type variables parametrizing this hint are known
            # at test time...
            if hint_pep_meta.typevars:
                # Assert that this getter returns only these type variables.
                assert hint_pep_meta.typevars == hint_typevars
            # Else, the exact type variables parametrizing this hint are
            # unknown at test time. In this case, silently ignore the exact
            # contents of this tuple.
        # Else, this hint is unparametrized by type variables. In this case,
        # assert that this getter returns the empty tuple.
        else:
            assert hint_typevars == ()

    # Assert this getter returns *NO* type variables for non-"typing" hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert get_hint_pep_typevars(not_hint_pep) == ()

# ....................{ TESTS ~ sign                       }....................
def test_get_hint_pep_sign(hints_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_sign` getter.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPepSignException
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign
    from beartype_test.a00_unit.data.hint.data_hint import (
        HINTS_NONPEP, NonpepCustomFakeTyping)
    from pytest import raises

    # Assert this getter returns the expected unsubscripted "typing" attribute
    # for all PEP-compliant type hints associated with such an attribute.
    for hint_pep_meta in hints_pep_meta:
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
def test_get_hint_pep_type_isinstanceable(hints_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_origin_type_isinstanceable`
    getter.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPepException
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_origin_type_isinstanceable)
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from pytest import raises

    # Assert this getter...
    for hint_pep_meta in hints_pep_meta:
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


def test_get_hint_pep_type_isinstanceable_or_none(hints_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_origin_type_isinstanceable_or_none`
    getter.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_origin_type_isinstanceable_or_none)
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP

    # Assert this getter returns the expected type origin for all PEP-compliant
    # type hints.
    for hint_pep_meta in hints_pep_meta:
        assert get_hint_pep_origin_type_isinstanceable_or_none(
            hint_pep_meta.hint) is hint_pep_meta.isinstanceable_type

    # Assert this getter returns "None" for non-PEP-compliant type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert get_hint_pep_origin_type_isinstanceable_or_none(
            not_hint_pep) is None
