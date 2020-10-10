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
from typing import Generic, TypeVar

# ....................{ TESTS ~ super                     }....................
def test_get_hint_pep_generic_bases() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpepget.get_hint_pep_generic_bases`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpepget import (
        get_hint_pep_generic_bases)
    from beartype._util.hint.pep.utilhintpeptest import is_hint_pep_typing
    from beartype_test.unit.data.data_hint import (
        NOT_PEP_HINTS, PEP_HINT_TO_META,)

    # Assert this getter returns...
    for pep_hint, pep_hint_meta in PEP_HINT_TO_META.items():
        # One or more unerased pseudo-superclasses for user-defined generic
        # PEP-compliant type hints.
        if pep_hint_meta.is_generic_user:
            pep_hint_generic_bases = get_hint_pep_generic_bases(pep_hint)
            assert isinstance(pep_hint_generic_bases, tuple)
            assert bool(pep_hint_generic_bases)
        # *NO* unerased pseudo-superclasses for concrete PEP-compliant type
        # hints *NOT* defined by the "typing" module.
        elif not is_hint_pep_typing(pep_hint):
            assert get_hint_pep_generic_bases(pep_hint) == ()
        # Else, this hint is defined by the "typing" module. In this case, this
        # hint may or may not be implemented as a generic conditionally
        # depending on the current Python version -- especially under the
        # Python < 3.7.0 implementations of the "typing" module, where
        # effectively *EVERYTHING* was internally implemented as a generic.
        # While we could technically correct for this conditionality, doing so
        # would render the resulting code less maintainable for no useful gain.
        # Ergo, we quietly ignore this edge case and get on with actual coding.

    # Assert this getter returns *NO* unerased pseudo-superclasses for
    # non-"typing" hints.
    for not_pep_hint in NOT_PEP_HINTS:
        assert get_hint_pep_generic_bases(not_pep_hint) == ()


def test_get_hint_pep_typevars() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpepget.get_hint_pep_typevars`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpepget import get_hint_pep_typevars
    from beartype_test.unit.data.data_hint import (
        NOT_PEP_HINTS, PEP_HINT_TO_META,)

    # Assert this getter returns...
    for pep_hint, pep_hint_meta in PEP_HINT_TO_META.items():
        # One or more type variables for typevared PEP-compliant type hints.
        if pep_hint_meta.is_typevared:
            pep_hint_typevars = get_hint_pep_typevars(pep_hint)
            assert isinstance(pep_hint_typevars, tuple)
            assert pep_hint_typevars
        # *NO* type variables for untypevared PEP-compliant type hints.
        else:
            assert get_hint_pep_typevars(pep_hint) == ()

    # Assert this getter returns *NO* type variables for non-"typing" hints.
    for not_pep_hint in NOT_PEP_HINTS:
        assert get_hint_pep_typevars(not_pep_hint) == ()

# ....................{ TESTS ~ attr                      }....................
def test_get_hint_pep_typing_attr_pass() -> None:
    '''
    Test successful usage of the
    :func:`beartype._util.hint.pep.utilhintpepget.get_hint_pep_typing_attr`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpepget import get_hint_pep_typing_attr
    from beartype_test.unit.data.data_hint import PEP_HINT_TO_META

    # Assert this getter returns the expected argumentless "typing" attribute
    # for all PEP-compliant type hints associated with such an attribute.
    for pep_hint, pep_hint_meta in PEP_HINT_TO_META.items():
        assert get_hint_pep_typing_attr(pep_hint) == pep_hint_meta.typing_attr


def test_get_hint_pep_typing_attr_fail() -> None:
    '''
    Test unsuccessful usage of the
    :func:`beartype._util.hint.pep.utilhintpepget.get_hint_pep_typing_attr`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintPepException
    from beartype._util.hint.pep.utilhintpepget import get_hint_pep_typing_attr
    from beartype_test.unit.data.data_hint import (
        NOT_PEP_HINTS, NonPepCustomFakeTyping)

    # Assert this getter raises the expected exception for an instance of a
    # class erroneously masquerading as a "typing" class.
    with raises(AttributeError):
        get_hint_pep_typing_attr(NonPepCustomFakeTyping())

    # Assert this getter raises the expected exception for non-"typing" hints.
    for not_pep_hint in NOT_PEP_HINTS:
        with raises(BeartypeDecorHintPepException):
            get_hint_pep_typing_attr(not_pep_hint)
