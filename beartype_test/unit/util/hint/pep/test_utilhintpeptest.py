#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint tester utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.utilhintpeptest` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import pytest, typing

# ....................{ TESTS                             }....................
def test_die_unless_hint_pep_supported() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpeptest.die_unless_hint_pep_supported`
    validator.
    '''

    # Defer heavyweight imports.
    from beartype.roar import (
        BeartypeDecorHintPepException,
        BeartypeDecorHintPepUnsupportedException,
    )
    from beartype._util.hint.pep.utilhintpeptest import (
        die_unless_hint_pep_supported)
    from beartype_test.unit.data.data_hint import (
        NONPEP_HINTS, PEP_HINT_TO_META,)

    # For each PEP-compliant type hint and associated metadata...
    for pep_hint, pep_hint_meta in PEP_HINT_TO_META.items():
        # If this "typing" type is supported, assert that this validator does
        # *NOT* raise an exception.
        if pep_hint_meta.is_supported:
            die_unless_hint_pep_supported(pep_hint)
        # Else, this "typing" type is unsupported. In this case, assert that
        # this validator raises an exception.
        else:
            with pytest.raises(BeartypeDecorHintPepUnsupportedException):
                die_unless_hint_pep_supported(pep_hint)

    # Assert that various non-"typing" types raise exceptions.
    for nonpep_hint in NONPEP_HINTS:
        with pytest.raises(BeartypeDecorHintPepException):
            die_unless_hint_pep_supported(nonpep_hint)


def test_is_hint_pep() -> None:
    '''
    Test the :func:`beartype._util.hint.pep.utilhintpeptest.is_hint_pep`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpeptest import is_hint_pep
    from beartype_test.unit.data.data_hint import NONPEP_HINTS, PEP_HINTS

    # Assert that various "typing" types are correctly detected.
    for pep_hint in PEP_HINTS:
        assert is_hint_pep(pep_hint) is True

    # Assert that various non-"typing" types are correctly detected.
    for nonpep_hint in NONPEP_HINTS:
        assert is_hint_pep(nonpep_hint) is False

# ....................{ TESTS ~ typevar                   }....................
def test_is_hint_typing_typevar() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpeptest.is_hint_typing_typevar`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpeptest import is_hint_typing_typevar
    from beartype_test.unit.data.data_hint import T

    # Assert that type variables are type variables.
    assert is_hint_typing_typevar(T) is True

    # Assert that "typing" types parametrized by type variables are *NOT* type
    # variables.
    assert is_hint_typing_typevar(typing.List[T]) is False


def test_is_hint_typing_typevared() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpeptest.is_hint_typing_typevared`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpeptest import (
        is_hint_typing_typevared)
    from beartype_test.unit.data.data_hint import (
        PEP_HINT_TO_META, NONPEP_HINTS,)

    # Assert that various "TypeVar"-centric types are correctly detected.
    for pep_hint, pep_hint_meta in PEP_HINT_TO_META.items():
        assert is_hint_typing_typevared(pep_hint) is (
            pep_hint_meta.is_typevared)

    # Assert that various "TypeVar"-agnostic types are correctly detected.
    for nonpep_hint in NONPEP_HINTS:
        assert is_hint_typing_typevared(nonpep_hint) is False
