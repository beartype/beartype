#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-compliant type hint tester** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.utilpeptest` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ TESTS                             }....................
# Fine-grained tests are intentionally performed *BEFORE* coarse-grained tests,
# dramatically improving readability of test failures.

# ....................{ TESTS ~ kind : generic            }....................
def test_is_hint_pep_generic() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep_generic` tester.
    '''

    # Defer heavyweight imports.
    from beartype._data.hint.pep.sign.datapepsigns import HintSignGeneric
    from beartype._util.hint.pep.utilpeptest import is_hint_pep_generic
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)

    # Assert this tester:
    # * Accepts generic PEP 484-compliant generics.
    # * Rejects concrete PEP-compliant type hints.
    for hint_pep_meta in HINTS_PEP_META:
        assert is_hint_pep_generic(hint_pep_meta.hint) is (
            hint_pep_meta.pep_sign is HintSignGeneric)

    # Assert this tester rejects non-PEP-compliant type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert is_hint_pep_generic(not_hint_pep) is False

# ....................{ TESTS ~ kind : typevar            }....................
def test_is_hint_pep_typevar() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep_typevar`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilpeptest import is_hint_pep_typevar
    from beartype_test.a00_unit.data.hint.pep.proposal.data_pep484 import T
    from typing import Optional

    # Assert that type variables are type variables.
    assert is_hint_pep_typevar(T) is True

    # Assert that "typing" types parametrized by type variables are *NOT* type
    # variables.
    assert is_hint_pep_typevar(Optional[T]) is False


def test_is_hint_pep_typevared() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep_typevared`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilpeptest import is_hint_pep_typevared
    from beartype_test.a00_unit.data.hint.data_hint import HINTS_NONPEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)

    # Assert that various "TypeVar"-centric types are correctly detected.
    for hint_pep_meta in HINTS_PEP_META:
        assert is_hint_pep_typevared(hint_pep_meta.hint) is (
            hint_pep_meta.is_typevared)

    # Assert that various "TypeVar"-agnostic types are correctly detected.
    for nonhint_pep in HINTS_NONPEP:
        assert is_hint_pep_typevared(nonhint_pep) is False

# ....................{ TESTS ~ typing                    }....................
def test_is_hint_pep_typing() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep_typing` tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilpeptest import (
        is_hint_pep_typing)
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)

    # Assert this tester accepts PEP-compliant type hints defined by the
    # "typing" module.
    for hint_pep_meta in HINTS_PEP_META:
        assert is_hint_pep_typing(hint_pep_meta.hint) is (
            hint_pep_meta.is_typing)

    # Assert this tester rejects non-PEP-compliant type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert is_hint_pep_typing(not_hint_pep) is False


def test_is_hint_pep_type_typing() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep_type_typing`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilpeptest import (
        is_hint_pep_type_typing)
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)

    # Assert this tester accepts PEP-compliant type hints defined by the
    # "typing" module.
    for hint_pep_meta in HINTS_PEP_META:
        assert is_hint_pep_type_typing(hint_pep_meta.hint) is (
            hint_pep_meta.is_type_typing)

    # Assert this tester rejects non-PEP-compliant type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert is_hint_pep_type_typing(not_hint_pep) is False

# ....................{ TESTS                             }....................
def test_is_hint_pep() -> None:
    '''
    Test the :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilpeptest import is_hint_pep
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.a00_unit.data.hint.nonpep.data_nonpep import (
        HINTS_NONPEP_META)
    from beartype_test.a00_unit.data.hint.pep.data_pep import HINTS_PEP_META

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


def test_is_hint_pep_subscripted() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep_subscripted`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilpeptest import is_hint_pep_subscripted
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)

    # Assert this tester accepts PEP-compliant subscripted type hints.
    for hint_pep_meta in HINTS_PEP_META:
        assert is_hint_pep_subscripted(hint_pep_meta.hint) is (
            hint_pep_meta.is_subscripted)

    # Assert this tester rejects non-PEP-compliant type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert is_hint_pep_subscripted(not_hint_pep) is False


#FIXME: Implement us up, please.
# def test_is_hint_pep_uncached() -> None:
#     '''
#     Test the
#     :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep_uncached`
#     tester.
#     '''
#
#     # Defer heavyweight imports.
#     from beartype._util.hint.pep.utilpeptest import is_hint_pep_uncached
#     from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
#     from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
#     from beartype_test.a00_unit.data.hint.pep.data_pep import (
#         HINTS_PEP_META)
#
#     # Assert this tester accepts concrete PEP-compliant type hints.
#     for hint_pep_meta in HINTS_PEP_META:
#         # True only if we expect this hint to be non-self-cached, including.
#         is_hint_pep_uncached_expected = (
#             # If th
#             hint_pep_meta.is_pep585_builtin or
#             (
#                 IS_PYTHON_AT_LEAST_3_9 and
#                 hint_pep_meta
#             )
#         )
#
#         assert is_hint_pep_uncached(hint_pep_meta.hint) is (
#             is_hint_pep_uncached_expected)
#
#     # Assert this tester accepts non-PEP-compliant type hints. What? Look,
#     # folks. This tester should probably raise an exception when passed those
#     # sort of hints, but this tester *CANNOT* by definition be memoized, which
#     # means it needs to be fast despite being unmemoized, which means we treat
#     # *ALL* objects other than a small well-known subset of non-self-cached
#     # PEP-compliant type hints as self-cached PEP-compliant type hints. *shrug*
#     for not_hint_pep in NOT_HINTS_PEP:
#         assert is_hint_pep_uncached(not_hint_pep) is True

# ....................{ TESTS ~ supported                 }....................
def test_is_hint_pep_supported() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep_supported`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilpeptest import is_hint_pep_supported
    from beartype_test.a00_unit.data.hint.data_hint import (
        NOT_HINTS_UNHASHABLE, NOT_HINTS_PEP)
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)

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


def test_die_if_hint_pep_unsupported() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpeptest.die_if_hint_pep_unsupported`
    validator.
    '''

    # Defer heavyweight imports.
    from beartype.roar import (
        BeartypeDecorHintPepException,
        BeartypeDecorHintPepUnsupportedException,
    )
    from beartype._util.hint.pep.utilpeptest import (
        die_if_hint_pep_unsupported)
    from beartype_test.a00_unit.data.hint.data_hint import (
        NOT_HINTS_UNHASHABLE, NOT_HINTS_PEP)
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)

    # Assert this validator...
    for hint_pep_meta in HINTS_PEP_META:
        # Accepts supported PEP-compliant type hints.
        if hint_pep_meta.is_supported:
            die_if_hint_pep_unsupported(hint_pep_meta.hint)
        # Rejects unsupported PEP-compliant type hints.
        else:
            with raises(BeartypeDecorHintPepUnsupportedException):
                die_if_hint_pep_unsupported(hint_pep_meta.hint)

    # Assert this validator rejects objects that are *NOT* PEP-noncompliant.
    for not_hint_pep in NOT_HINTS_PEP:
        with raises(BeartypeDecorHintPepException):
            die_if_hint_pep_unsupported(not_hint_pep)

    # Assert this validator rejects unhashable objects.
    for non_hint_unhashable in NOT_HINTS_UNHASHABLE:
        with raises(BeartypeDecorHintPepException):
            die_if_hint_pep_unsupported(non_hint_unhashable)


def test_die_if_hint_pep_sign_unsupported() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpeptest.die_if_hint_pep_sign_unsupported`
    validator.
    '''

    # Defer heavyweight imports.
    from beartype.roar import (
        BeartypeDecorHintPepException,
        BeartypeDecorHintPepUnsupportedException,
    )
    from beartype._data.hint.pep.sign.datapepsignset import (
        HINT_SIGNS_SUPPORTED)
    from beartype._util.hint.pep.utilpeptest import (
        die_if_hint_pep_sign_unsupported)
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)

    # Assert this validator accepts all supported signs.
    for hint_sign_supported in HINT_SIGNS_SUPPORTED:
        die_if_hint_pep_sign_unsupported(hint_sign_supported)

    # For each PEP-compliant type hint, assert this validator...
    for hint_pep_meta in HINTS_PEP_META:
        # Accepts the signs of all supported PEP-compliant type hints.
        if hint_pep_meta.is_supported:
            die_if_hint_pep_sign_unsupported(hint_pep_meta.pep_sign)
        # Rejects the signs of all unsupported PEP-compliant type hints.
        else:
            with raises(BeartypeDecorHintPepUnsupportedException):
                die_if_hint_pep_sign_unsupported(hint_pep_meta.pep_sign)

    # # Assert this validator rejects non-signs.
    # with raises(BeartypeDecorHintPepException):
    #     die_if_hint_pep_sign_unsupported(object())
