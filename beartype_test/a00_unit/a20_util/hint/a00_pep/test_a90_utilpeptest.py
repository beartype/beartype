#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-compliant type hint tester** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.utilpeptest` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ TESTS                              }....................
# Fine-grained tests are intentionally performed *BEFORE* coarse-grained tests,
# dramatically improving readability of test failures.

# ....................{ TESTS ~ kind : typevar             }....................
def test_is_hint_pep_typevars() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep_typevars`
    tester.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.utilpeptest import is_hint_pep_typevars
    from beartype_test.a00_unit.data.hint.data_hint import HINTS_NONPEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)

    # Assert that various "TypeVar"-centric types are correctly detected.
    for hint_pep_meta in HINTS_PEP_META:
        assert is_hint_pep_typevars(hint_pep_meta.hint) is (
            hint_pep_meta.is_typevars)

    # Assert that various "TypeVar"-agnostic types are correctly detected.
    for nonhint_pep in HINTS_NONPEP:
        assert is_hint_pep_typevars(nonhint_pep) is False

# ....................{ TESTS ~ typing                     }....................
def test_is_hint_pep_typing() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep_typing` tester.
    '''

    # Defer test-specific imports.
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

    # Defer test-specific imports.
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

# ....................{ TESTS                              }....................
def test_is_hint_pep() -> None:
    '''
    Test the :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep`
    tester.
    '''

    # Defer test-specific imports.
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
        # if is_hint_pep(hint_nonpep_meta.hint) is True:
        #     from beartype._util.hint.pep.utilpepget import (
        #         get_hint_pep_sign_or_none)
        #     hint = hint_nonpep_meta.hint
        #     print(f'hint {hint} sign: {get_hint_pep_sign_or_none(hint)}')

        assert is_hint_pep(hint_nonpep_meta.hint) is False

    # Assert this tester rejects non-PEP-compliant type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert is_hint_pep(not_hint_pep) is False


def test_is_hint_pep_args() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep_args`
    tester.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.utilpeptest import is_hint_pep_args
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)

    # Assert this tester accepts PEP-compliant subscripted type hints.
    for hint_pep_meta in HINTS_PEP_META:
        assert is_hint_pep_args(hint_pep_meta.hint) is (
            hint_pep_meta.is_args)

    # Assert this tester rejects non-PEP-compliant type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert is_hint_pep_args(not_hint_pep) is False


#FIXME: Implement us up, please.
# def test_is_hint_pep_uncached() -> None:
#     '''
#     Test the
#     :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep_uncached`
#     tester.
#     '''
#
#     # Defer test-specific imports.
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

# ....................{ TESTS ~ supported                  }....................
def test_is_hint_pep_supported() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep_supported`
    tester.
    '''

    # Defer test-specific imports.
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

    # Defer test-specific imports.
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
