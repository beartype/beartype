#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
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
def test_get_hint_pep_args(hints_piths_pep_meta) -> None:
    '''
    Test the :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_args`
    getter.

    Parameters
    ----------
    hints_piths_pep_meta : list[beartype_test.a00_unit.data.hint.cls.pith.data_clshintpith.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPepException
    from beartype.typing import Tuple
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_args,
        _HINT_ARGS_EMPTY_TUPLE,
    )
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from pytest import raises

    # ....................{ CLASSES                        }....................
    class TheWholeMammothBrood(object):
        '''
        Arbitrary PEP-noncompliant type defining the ``__args__`` dunder
        attribute to *not* be a tuple.
        '''

        __args__ = 'But one of the whole mammoth-brood still kept'

    # ....................{ PASS                           }....................
    # For each PEP-compliant hint, assert this getter returns...
    for hint_pep_meta in hints_piths_pep_meta:
        # Localize this hint to simplify debugging.
        hint = hint_pep_meta.hint

        # Tuple of all arguments subscripting this hint.
        hint_args = get_hint_pep_args(hint)
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

    # ....................{ PASS ~ tuple                   }....................
    # Explicitly validate that this getter handles both PEP 484- and 585-
    # compliant empty tuples by returning "_HINT_ARGS_EMPTY_TUPLE" as expected.

    # Assert this getter when passed a PEP 484-compliant empty tuple hint
    # returns a tuple containing an empty tuple for disambiguity.
    assert get_hint_pep_args(Tuple[()]) == _HINT_ARGS_EMPTY_TUPLE

    # Assert this getter when passed a PEP 585-compliant empty tuple hint
    # returns a tuple containing an empty tuple for disambiguity.
    assert get_hint_pep_args(tuple[()]) == _HINT_ARGS_EMPTY_TUPLE

    # ....................{ FAIL                           }....................
    # Assert this getter when passed a PEP-noncompliant hint defining the
    # "__args__" dunder attribute to *NOT* be a tuple raises the expected
    # exception.
    with raises(BeartypeDecorHintPepException):
        get_hint_pep_args(TheWholeMammothBrood)

# ....................{ TESTS ~ attr : typeargs            }....................
def test_get_hint_pep_typeargs_packed(
    hints_piths_pep_meta: 'list[beartype_test.a00_unit.data.hint.cls.pith.data_clshintpith.HintPepMetadata]',
) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_typeargs_packed`
    getter.

    Parameters
    ----------
    hints_piths_pep_meta : list[beartype_test.a00_unit.data.hint.cls.pith.data_clshintpith.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPepException
    from beartype._util.hint.pep.utilpepget import get_hint_pep_typeargs_packed
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from pytest import raises

    # ....................{ CLASSES                        }....................
    class HisSovereigntyAndRuleAndMajesty(object):
        '''
        Arbitrary PEP-noncompliant type defining the ``__parameters__`` dunder
        attribute to *not* be a tuple.
        '''

        __parameters__ = "His sov'reignty, and rule, and majesty;—"

    # ....................{ PASS ~ iterate                 }....................
    # Assert this getter returns *NO* type parameters for non-"typing" hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert get_hint_pep_typeargs_packed(not_hint_pep) == ()

    # For each PEP-compliant test hint...
    for hint_pep_meta in hints_piths_pep_meta:
        # This hint, localized purely to simplify debugging. *sigh*
        hint = hint_pep_meta.hint

        # Tuples of the one or more packed type parameters parametrizing the
        # subscripted and unsubscripted forms of this generic if this hint is a
        # PEP 484- or 585-compliant generic *OR* the empty tuple otherwise
        # (e.g., if this hint is *NOT* such a generic).
        hint_typeargs_packed_subbed = get_hint_pep_typeargs_packed(
            hint=hint, is_unsub=False)
        hint_typeargs_packed_unsubbed = get_hint_pep_typeargs_packed(
            hint=hint, is_unsub=True)

        # If the unsubscripted form of this hint is parametrized by one or more
        # type parameters, assert this getter returned one or more type
        # parameters when passed the unsubscripted form of this hint.
        if hint_pep_meta.is_typeargs:
            assert hint_typeargs_packed_unsubbed

        # Assert that the contents of these tuples are as expected.
        _assert_hint_typeargs_packed(
            hint_typeargs_packed_actual=hint_typeargs_packed_subbed,
            hint_typeargs_packed_expect=hint_pep_meta.typeargs_packed_subbed,
        )
        _assert_hint_typeargs_packed(
            hint_typeargs_packed_actual=hint_typeargs_packed_unsubbed,
            hint_typeargs_packed_expect=hint_pep_meta.typeargs_packed_unsubbed,
        )

    # ....................{ FAIL                           }....................
    # Assert this getter when passed a PEP-noncompliant hint defining the
    # "__parameters__" dunder attribute to *NOT* be a tuple raises the expected
    # exception.
    with raises(BeartypeDecorHintPepException):
        get_hint_pep_typeargs_packed(HisSovereigntyAndRuleAndMajesty)


def _assert_hint_typeargs_packed(
    hint_typeargs_packed_actual: (
        'beartype._data.typing.datatyping.TuplePep484612646TypeArgsPacked'),
    hint_typeargs_packed_expect: (
        'beartype._data.typing.datatyping.TuplePep484612646TypeArgsPacked'),
) -> None:
    '''
    Assert that the passed actual tuple of the one or more packed type
    parameters parametrizing the subscripted or unsubscripted form of this
    generic if the passed hint is a :pep:`484`- or :pep:`585`-compliant generic
    *or* the empty tuple otherwise (e.g., if this hint is *not* such a generic)
    as returned by the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_typeargs_packed`
    getter is equal to the passed expected tuple of these type parameters.

    Parameters
    ----------
    hint_typeargs_packed_actual: TuplePep484612646TypeArgsPacked
        Actual tuple of these type parameters returned by that getter when
        passed this hint.
    hint_typeargs_packed_expect: TuplePep484612646TypeArgsPacked
        Expected tuple of these type parameters returned by that getter when
        passed this hint.
    '''
    assert isinstance(hint_typeargs_packed_actual, tuple)
    assert isinstance(hint_typeargs_packed_expect, tuple)

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep646.pep484612646typevar import (
        is_hint_pep484612646_typearg_packed)

    # ....................{ ASSERTS                        }....................
    # Assert all items of this tuple are actually packed type parameters.
    for hint_typearg in hint_typeargs_packed_actual:
        assert is_hint_pep484612646_typearg_packed(hint_typearg) is True

    # If the type parameters parametrizing this hint are known at test time,
    # assert that this getter returns only these type parameters.
    if hint_typeargs_packed_expect:
        assert hint_typeargs_packed_actual == hint_typeargs_packed_expect
    # Else, the type parameters parametrizing this hint are unknown at test
    # time. In this case, silently ignore the contents of this tuple.

# ....................{ TESTS ~ origin : type              }....................
def test_get_hint_pep_type_isinstanceable(hints_piths_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_origin_type_isinstanceable`
    getter.

    Parameters
    ----------
    hints_piths_pep_meta : List[beartype_test.a00_unit.data.hint.cls.pith.data_clshintpith.HintPepMetadata]
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
    for hint_pep_meta in hints_piths_pep_meta:
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


def test_get_hint_pep_type_isinstanceable_or_none(hints_piths_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_origin_type_isinstanceable_or_none`
    getter.

    Parameters
    ----------
    hints_piths_pep_meta : List[beartype_test.a00_unit.data.hint.cls.pith.data_clshintpith.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_origin_type_isinstanceable_or_none)
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP

    # Assert this getter returns the expected type origin for all PEP-compliant
    # type hints.
    for hint_pep_meta in hints_piths_pep_meta:
        assert get_hint_pep_origin_type_isinstanceable_or_none(
            hint_pep_meta.hint) is hint_pep_meta.isinstanceable_type

    # Assert this getter returns "None" for non-PEP-compliant type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert get_hint_pep_origin_type_isinstanceable_or_none(
            not_hint_pep) is None
