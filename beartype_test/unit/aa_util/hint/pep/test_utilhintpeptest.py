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
import typing
# from beartype_test.util.pyterror import raises_uncached
from pytest import raises

# ....................{ TESTS                             }....................
def test_is_hint_pep() -> None:
    '''
    Test the :func:`beartype._util.hint.pep.utilhintpeptest.is_hint_pep`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpeptest import is_hint_pep
    from beartype_test.unit.data.data_hint import NOT_PEP_HINTS, PEP_HINTS

    # Assert that various "typing" types are correctly detected.
    for pep_hint in PEP_HINTS:
        assert is_hint_pep(pep_hint) is True

    # Assert that various non-"typing" types are correctly detected.
    for not_pep_hint in NOT_PEP_HINTS:
        assert is_hint_pep(not_pep_hint) is False


def test_is_hint_pep_generic() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpeptest.is_hint_pep_generic_user` tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpeptest import is_hint_pep_generic_user
    from beartype_test.unit.data.data_hint import (
        NOT_PEP_HINTS, PEP_HINT_TO_META)

    # Assert this tester:
    # * Accepts generic PEP-compliant type hints.
    # * Rejects concrete PEP-compliant type hints.
    for pep_hint, pep_hint_meta in PEP_HINT_TO_META.items():
        assert is_hint_pep_generic_user(pep_hint) is pep_hint_meta.is_generic_user

    # Assert this tester rejects non-"typing" types.
    for not_pep_hint in NOT_PEP_HINTS:
        assert is_hint_pep_generic_user(not_pep_hint) is False


def test_is_hint_pep_typing() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpeptest.is_hint_pep_typing` tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpeptest import is_hint_pep_typing
    from beartype_test.unit.data.data_hint import (
        NOT_PEP_HINTS, PEP_HINT_TO_META)

    # Assert this tester accepts concrete PEP-compliant type hints.
    #
    # Ideally, we would also assert this tester to rejects generic
    # PEP-compliant type hints. Although most generics are instances of
    # user-defined classes defined in non-"typing" modules, a small subset are
    # stdlib classes defined in the "typing" module (e.g., "typing.IO"). Let's
    # avoid rendering this any more fragile than we have.
    for pep_hint, pep_hint_meta in PEP_HINT_TO_META.items():
        if not pep_hint_meta.is_generic_user:
            assert is_hint_pep_typing(pep_hint) is True

    # Assert this tester rejects non-"typing" types.
    for not_pep_hint in NOT_PEP_HINTS:
        assert is_hint_pep_typing(not_pep_hint) is False

# ....................{ TESTS ~ supported                 }....................
def test_is_hint_pep_supported() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpeptest.is_hint_pep_supported`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpeptest import is_hint_pep_supported
    from beartype_test.unit.data.data_hint import (
        NOT_HINTS_UNHASHABLE, NOT_PEP_HINTS, PEP_HINT_TO_META,)

    # Assert this tester:
    # * Accepts supported PEP-compliant type hints.
    # * Rejects unsupported PEP-compliant type hints.
    for pep_hint, pep_hint_meta in PEP_HINT_TO_META.items():
        assert is_hint_pep_supported(pep_hint) is pep_hint_meta.is_supported

    # Assert this tester rejects objects that are *NOT* PEP-noncompliant.
    for not_pep_hint in NOT_PEP_HINTS:
        assert is_hint_pep_supported(not_pep_hint) is False

    # Assert this tester rejects unhashable objects.
    for non_hint_unhashable in NOT_HINTS_UNHASHABLE:
        with raises(TypeError):
            is_hint_pep_supported(non_hint_unhashable)


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
        NOT_HINTS_UNHASHABLE, NOT_PEP_HINTS, PEP_HINT_TO_META,)

    # Assert this tester...
    for pep_hint, pep_hint_meta in PEP_HINT_TO_META.items():
        # Accepts supported PEP-compliant type hints.
        if pep_hint_meta.is_supported:
            die_unless_hint_pep_supported(pep_hint)
        # Rejects unsupported PEP-compliant type hints.
        else:
            with raises(BeartypeDecorHintPepUnsupportedException):
                die_unless_hint_pep_supported(pep_hint)

    # Assert this tester rejects objects that are *NOT* PEP-noncompliant.
    for not_pep_hint in NOT_PEP_HINTS:
        with raises(BeartypeDecorHintPepException):
            die_unless_hint_pep_supported(not_pep_hint)

    # Assert this tester rejects unhashable objects.
    for non_hint_unhashable in NOT_HINTS_UNHASHABLE:
        with raises(TypeError):
            die_unless_hint_pep_supported(non_hint_unhashable)


def test_die_unless_hint_pep_typing_attr_supported() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpeptest.die_unless_hint_pep_typing_attr_supported`
    validator.
    '''

    # Defer heavyweight imports.
    from beartype.roar import (
        BeartypeDecorHintPepException,
        BeartypeDecorHintPepUnsupportedException,
    )
    from beartype._util.hint.pep.utilhintpeptest import (
        die_unless_hint_pep_typing_attr_supported)
    from beartype._util.hint.pep.utilhintpepdata import TYPING_ATTRS_SUPPORTED
    from beartype_test.unit.data.data_hint import NOT_PEP_HINTS, PEP_HINTS

    # Assert this tester accepts all supported argumentless "typing"
    # attributes.
    for typing_attrs_supported in TYPING_ATTRS_SUPPORTED:
        die_unless_hint_pep_typing_attr_supported(typing_attrs_supported)

    # Assert this tester rejects PEP-compliant type hints that are *NOT*
    # supported argumentless "typing" attributes.
    for pep_hint in PEP_HINTS:
        if pep_hint not in TYPING_ATTRS_SUPPORTED:
            with raises(BeartypeDecorHintPepUnsupportedException):
                die_unless_hint_pep_typing_attr_supported(pep_hint)

    # Assert this tester rejects objects that are *NOT* PEP-noncompliant.
    for not_pep_hint in NOT_PEP_HINTS:
        with raises(BeartypeDecorHintPepException):
            die_unless_hint_pep_typing_attr_supported(not_pep_hint)

# ....................{ TESTS ~ typevar                   }....................
def test_is_hint_typing_typevar() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpeptest.is_hint_pep_typevar`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpeptest import is_hint_pep_typevar
    from beartype_test.unit.data.data_hint import T

    # Assert that type variables are type variables.
    assert is_hint_pep_typevar(T) is True

    # Assert that "typing" types parametrized by type variables are *NOT* type
    # variables.
    assert is_hint_pep_typevar(typing.List[T]) is False


def test_is_hint_typing_typevared() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpeptest.is_hint_pep_typevared`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpeptest import (
        is_hint_pep_typevared)
    from beartype_test.unit.data.data_hint import (
        PEP_HINT_TO_META, NONPEP_HINTS,)

    # Assert that various "TypeVar"-centric types are correctly detected.
    for pep_hint, pep_hint_meta in PEP_HINT_TO_META.items():
        assert is_hint_pep_typevared(pep_hint) is (
            pep_hint_meta.is_typevared)

    # Assert that various "TypeVar"-agnostic types are correctly detected.
    for nonpep_hint in NONPEP_HINTS:
        assert is_hint_pep_typevared(nonpep_hint) is False
