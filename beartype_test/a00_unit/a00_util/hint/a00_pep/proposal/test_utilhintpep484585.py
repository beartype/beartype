#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`484` and :pep:`585` **dual type hint utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.utilpep484585` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ kind : generic            }....................
def test_is_hint_pep484585_generic() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.utilpep484585.is_hint_pep484585_generic`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._data.hint.pep.sign.datapepsigns import HintSignGeneric
    from beartype._util.hint.pep.proposal.utilpep484585 import (
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


def test_get_hint_pep484585_generic_type_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.utilpep484585.get_hint_pep484585_generic_type_or_none`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype._data.hint.pep.sign.datapepsigns import HintSignGeneric
    from beartype._util.hint.pep.proposal.utilpep484585 import (
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
    # from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_7
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
    :func:`beartype._util.hint.pep.proposal.utilpep484585.get_hint_pep484585_generic_bases_unerased`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintPepException
    from beartype._data.hint.pep.sign.datapepsigns import HintSignGeneric
    from beartype._util.hint.pep.proposal.utilpep484585 import (
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
            assert get_hint_pep484585_generic_bases_unerased(
                not_hint_pep) is None

# ....................{ TESTS ~ kind : subclass           }....................
def test_get_hint_pep484585_subclass_superclass() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.utilpep484585.get_hint_pep484585_subclass_superclass`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype.roar import (
        BeartypeDecorHintPep484585Exception,
        BeartypeDecorHintPep585Exception,
    )
    from beartype._util.hint.pep.proposal.utilpep484585 import (
        get_hint_pep484585_subclass_superclass)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from pytest import raises
    from typing import ForwardRef, Type

    # Assert this getter returns the expected object when passed a PEP
    # 484-compliant subclass type hint subscripted by a class.
    assert get_hint_pep484585_subclass_superclass(Type[str]) is str

    # Assert this getter returns the expected object when passed a PEP
    # 484-compliant subclass type hint subscripted by a forward reference to a
    # class.
    assert get_hint_pep484585_subclass_superclass(Type['bytes']) == (
        ForwardRef('bytes'))

    # Assert this getter raises the expected exception when passed an arbitrary
    # object that is neither a PEP 484- nor 585-compliant subclass type hint.
    with raises(BeartypeDecorHintPep484585Exception):
        get_hint_pep484585_subclass_superclass('Caustically')

    # If the active Python interpreter targets Python >= 3.9 and thus supports
    # PEP 585...
    if IS_PYTHON_AT_LEAST_3_9:
        # Assert this getter returns the expected object when passed a PEP
        # 585-compliant subclass type hint subscripted by a class.
        assert get_hint_pep484585_subclass_superclass(type[bool]) is bool

        # Assert this getter returns the expected object when passed a PEP
        # 484-compliant subclass type hint subscripted by a forward reference
        # to a class.
        assert get_hint_pep484585_subclass_superclass(type['complex']) == (
            'complex')

        # Assert this getter raises the expected exception when passed a PEP
        # 585-compliant subclass type hint subscripted by *NO* classes.
        #
        # Note there intentionally exists *NO* corresponding PEP 484 test, as
        # the "typing.Type" factory already validates this to be the case.
        with raises(BeartypeDecorHintPep585Exception):
            get_hint_pep484585_subclass_superclass(type[()])

        # Assert this getter raises the expected exception when passed a PEP
        # 585-compliant subclass type hint subscripted by two or more classes.
        #
        # Note there intentionally exists *NO* corresponding PEP 484 test, as
        # the "typing.Type" factory already validates this to be the case.
        with raises(BeartypeDecorHintPep585Exception):
            get_hint_pep484585_subclass_superclass(type[int, float])

        # Assert this getter raises the expected exception when passed a PEP
        # 585-compliant subclass type hint subscripted by an object that is
        # neither a class nor a forward reference to a class.
        #
        # Note there intentionally exists *NO* corresponding PEP 484 test, as
        # the "typing.Type" factory already validates this to be the case.
        with raises(BeartypeDecorHintPep585Exception):
            get_hint_pep484585_subclass_superclass(type[
                b'Counterrevolutionary'])
