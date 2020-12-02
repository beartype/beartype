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
from pytest import raises
from typing import Generic, List

# ....................{ TESTS                             }....................
def test_is_hint_pep() -> None:
    '''
    Test the :func:`beartype._util.hint.pep.utilhintpeptest.is_hint_pep`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpeptest import is_hint_pep
    from beartype_test.unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.unit.data.hint.nonpep.data_hintnonpep import (
        HINTS_NONPEP_META)
    from beartype_test.unit.data.hint.pep.data_hintpep import HINTS_PEP_META

    # Assert this tester accepts PEP-compliant type hints.
    for hint_pep_meta in HINTS_PEP_META:
        assert is_hint_pep(hint_pep_meta.hint) is True

    # Assert this tester rejects PEP-noncompliant type hints implemented by the
    # "typing" module as normal types indistinguishable from non-"typing" types
    # and thus effectively non-PEP-compliant for all practical intents.
    for hint_nonpep_meta in HINTS_NONPEP_META:
        assert is_hint_pep(hint_nonpep_meta.hint) is False

    # Assert this tester rejects non-PEP-compliant type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert is_hint_pep(not_hint_pep) is False


def test_is_hint_pep_typing() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpeptest.is_hint_pep_class_typing`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpeptest import is_hint_pep_class_typing
    from beartype_test.unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.unit.data.hint.pep.data_hintpep import HINTS_PEP_META

    # Assert this tester accepts concrete PEP-compliant type hints.
    for hint_pep_meta in HINTS_PEP_META:
        assert is_hint_pep_class_typing(hint_pep_meta.hint) is (
            hint_pep_meta.is_typing)

    # Assert this tester rejects non-"typing" types.
    for not_hint_pep in NOT_HINTS_PEP:
        assert is_hint_pep_class_typing(not_hint_pep) is False

# ....................{ TESTS ~ supported                 }....................
def test_is_hint_pep_supported() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpeptest.is_hint_pep_supported`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpeptest import is_hint_pep_supported
    from beartype_test.unit.data.hint.data_hint import (
        NOT_HINTS_UNHASHABLE, NOT_HINTS_PEP)
    from beartype_test.unit.data.hint.pep.data_hintpep import HINTS_PEP_META

    # Assert this tester:
    # * Accepts supported PEP-compliant type hints.
    # * Rejects unsupported PEP-compliant type hints.
    for hint_pep_meta in HINTS_PEP_META:
        assert is_hint_pep_supported(hint_pep_meta.hint) is (
            hint_pep_meta.is_supported)

    # Assert this tester rejects objects that are *NOT* PEP-noncompliant.
    for not_hint_pep in NOT_HINTS_PEP:
        assert is_hint_pep_supported(not_hint_pep) is False

    # Assert this tester rejects unhashable objects.
    for non_hint_unhashable in NOT_HINTS_UNHASHABLE:
        assert is_hint_pep_supported(non_hint_unhashable) is False


def test_die_unless_hint_pep_supported() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpeptest.die_if_hint_pep_unsupported`
    validator.
    '''

    # Defer heavyweight imports.
    from beartype.roar import (
        BeartypeDecorHintPepException,
        BeartypeDecorHintPepUnsupportedException,
    )
    from beartype._util.hint.pep.utilhintpeptest import (
        die_if_hint_pep_unsupported)
    from beartype_test.unit.data.hint.data_hint import (
        NOT_HINTS_UNHASHABLE, NOT_HINTS_PEP)
    from beartype_test.unit.data.hint.pep.data_hintpep import HINTS_PEP_META

    # Assert this tester...
    for hint_pep_meta in HINTS_PEP_META:
        # Accepts supported PEP-compliant type hints.
        if hint_pep_meta.is_supported:
            die_if_hint_pep_unsupported(hint_pep_meta.hint)
        # Rejects unsupported PEP-compliant type hints.
        else:
            with raises(BeartypeDecorHintPepUnsupportedException):
                die_if_hint_pep_unsupported(hint_pep_meta.hint)

    # Assert this tester rejects objects that are *NOT* PEP-noncompliant.
    for not_hint_pep in NOT_HINTS_PEP:
        with raises(BeartypeDecorHintPepException):
            die_if_hint_pep_unsupported(not_hint_pep)

    # Assert this tester rejects unhashable objects.
    for non_hint_unhashable in NOT_HINTS_UNHASHABLE:
        with raises(BeartypeDecorHintPepException):
            die_if_hint_pep_unsupported(non_hint_unhashable)


def test_die_unless_hint_pep_sign_supported() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpeptest.die_if_hint_pep_sign_unsupported`
    validator.
    '''

    # Defer heavyweight imports.
    from beartype.roar import (
        BeartypeDecorHintPepException,
        BeartypeDecorHintPepUnsupportedException,
    )
    from beartype._util.hint.pep.utilhintpeptest import (
        die_if_hint_pep_sign_unsupported)
    from beartype._util.hint.data.pep.utilhintdatapep import (
        HINT_PEP_SIGNS_SUPPORTED)
    from beartype_test.unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.unit.data.hint.pep.data_hintpep import (
        HINTS_PEP_HASHABLE)

    # Assert this tester accepts all supported signs.
    for pep_signs_supported in HINT_PEP_SIGNS_SUPPORTED:
        die_if_hint_pep_sign_unsupported(pep_signs_supported)

    # Assert this tester rejects PEP-compliant type hints that are *NOT*
    # supported signs.
    for hint_pep in HINTS_PEP_HASHABLE:
        if hint_pep not in HINT_PEP_SIGNS_SUPPORTED:
            with raises(BeartypeDecorHintPepUnsupportedException):
                die_if_hint_pep_sign_unsupported(hint_pep)

    # Assert this tester rejects objects that are neither PEP-noncompliant
    # *NOR* supported signs. Examples of objects that are PEP-noncompliant but
    # also supported signs include *ALL* PEP 585-compliant type origins under
    # Python >= 3.9 (e.g., "dict", "list", "collections.abc.Sequence").
    for not_hint_pep in NOT_HINTS_PEP:
        if not_hint_pep not in HINT_PEP_SIGNS_SUPPORTED:
            with raises(BeartypeDecorHintPepException):
                die_if_hint_pep_sign_unsupported(not_hint_pep)

# ....................{ TESTS ~ subtype : generic         }....................
def test_is_hint_pep484_generic() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpeptest.is_hint_pep_generic`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpeptest import is_hint_pep_generic
    from beartype_test.unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.unit.data.hint.pep.data_hintpep import HINTS_PEP_META

    # Assert this tester:
    # * Accepts generic PEP 484-compliant generics.
    # * Rejects concrete PEP-compliant type hints.
    for hint_pep_meta in HINTS_PEP_META:
        assert is_hint_pep_generic(hint_pep_meta.hint) is (
            hint_pep_meta.pep_sign is Generic)

    # Assert this tester rejects non-"typing" types.
    for not_hint_pep in NOT_HINTS_PEP:
        assert is_hint_pep_generic(not_hint_pep) is False

# ....................{ TESTS ~ subtype : typevar         }....................
def test_is_hint_typing_typevar() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpeptest.is_hint_pep_typevar`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpeptest import is_hint_pep_typevar
    from beartype_test.unit.data.hint.pep.proposal.data_hintpep484 import T

    # Assert that type variables are type variables.
    assert is_hint_pep_typevar(T) is True

    # Assert that "typing" types parametrized by type variables are *NOT* type
    # variables.
    assert is_hint_pep_typevar(List[T]) is False


def test_is_hint_typing_typevared() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpeptest.is_hint_pep_typevared`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpeptest import is_hint_pep_typevared
    from beartype_test.unit.data.hint.data_hint import HINTS_NONPEP
    from beartype_test.unit.data.hint.pep.data_hintpep import HINTS_PEP_META

    # Assert that various "TypeVar"-centric types are correctly detected.
    for hint_pep_meta in HINTS_PEP_META:
        assert is_hint_pep_typevared(hint_pep_meta.hint) is (
            hint_pep_meta.is_typevared)

    # Assert that various "TypeVar"-agnostic types are correctly detected.
    for nonhint_pep in HINTS_NONPEP:
        assert is_hint_pep_typevared(nonhint_pep) is False
