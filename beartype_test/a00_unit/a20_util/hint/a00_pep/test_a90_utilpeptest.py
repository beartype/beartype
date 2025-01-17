#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
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

# ....................{ TESTS                              }....................
# Fine-grained tests are intentionally performed *BEFORE* coarse-grained tests,
# dramatically improving readability of test failures.

# ....................{ TESTS ~ typing                     }....................
def test_is_hint_pep_typing(hints_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep_typing` tester.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.utilpeptest import (
        is_hint_pep_typing)
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP

    # Assert this tester accepts PEP-compliant type hints defined by the
    # "typing" module.
    for hint_pep_meta in hints_pep_meta:
        assert is_hint_pep_typing(hint_pep_meta.hint) is (
            hint_pep_meta.is_typing)

    # Assert this tester rejects non-PEP-compliant type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert is_hint_pep_typing(not_hint_pep) is False


def test_is_hint_pep_type_typing(hints_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep_type_typing`
    tester.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.utilpeptest import (
        is_hint_pep_type_typing)
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP

    # Assert this tester accepts PEP-compliant type hints defined by the
    # "typing" module.
    for hint_pep_meta in hints_pep_meta:
        assert is_hint_pep_type_typing(hint_pep_meta.hint) is (
            hint_pep_meta.is_type_typing)

    # Assert this tester rejects non-PEP-compliant type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert is_hint_pep_type_typing(not_hint_pep) is False

# ....................{ TESTS                              }....................
def test_is_hint_pep(hints_pep_meta, hints_nonpep_meta) -> None:
    '''
    Test the :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep`
    tester.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    hints_nonpep_meta : Tuple[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintNonpepMetadata]
        Tuple of PEP-noncompliant type hint metadata describing PEP-noncompliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.utilpeptest import is_hint_pep
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP

    # Assert this tester accepts PEP-compliant type hints.
    for hint_pep_meta in hints_pep_meta:
        assert is_hint_pep(hint_pep_meta.hint) is True

    # Assert this tester rejects PEP-noncompliant type hints implemented by the
    # "typing" module as normal types indistinguishable from non-"typing" types
    # and thus effectively non-PEP-compliant for all practical intents.
    for hint_nonpep_meta in hints_nonpep_meta:
        assert is_hint_pep(hint_nonpep_meta.hint) is False

    # Assert this tester rejects non-PEP-compliant type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        assert is_hint_pep(not_hint_pep) is False


def test_is_hint_pep_subscripted(hints_pep_meta, hints_nonpep_meta) -> None:
    '''
    Test the :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep_subscripted`
    tester.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    hints_nonpep_meta : Tuple[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintNonpepMetadata]
        Tuple of PEP-noncompliant type hint metadata describing PEP-noncompliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.utilpeptest import is_hint_pep_subscripted
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP

    # Assert this tester:
    # * Accepts all subscripted PEP-compliant type hints.
    # * Rejects all unsubscripted PEP-compliant type hints.
    for hint_pep_meta in hints_pep_meta:
        assert is_hint_pep_subscripted(hint_pep_meta.hint) is (
            hint_pep_meta.is_args)

    # Assert this tester rejects PEP-noncompliant type hints implemented by the
    # "typing" module as normal types indistinguishable from non-"typing" types
    # and thus effectively non-PEP-compliant for all practical intents.
    for hint_nonpep_meta in hints_nonpep_meta:
        assert is_hint_pep_subscripted(hint_nonpep_meta.hint) is False

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
#             hint_pep_meta.is_pep585_builtin_subscripted or
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
def test_is_hint_pep_supported(hints_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep_supported`
    tester.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.utilpeptest import is_hint_pep_supported
    from beartype_test.a00_unit.data.hint.data_hint import (
        NOT_HINTS_PEP,
        NOT_HINTS_UNHASHABLE,
    )

    # Assert this tester:
    # * Accepts supported PEP-compliant type hints.
    # * Rejects unsupported PEP-compliant type hints.
    for hint_pep_meta in hints_pep_meta:
        assert is_hint_pep_supported(hint_pep_meta.hint) is (
            hint_pep_meta.is_supported)

    # Assert this tester rejects objects that are *NOT* PEP-noncompliant.
    for not_hint_pep in NOT_HINTS_PEP:
        assert is_hint_pep_supported(not_hint_pep) is False

    # Assert this tester rejects unhashable objects.
    for non_hint_unhashable in NOT_HINTS_UNHASHABLE:
        assert is_hint_pep_supported(non_hint_unhashable) is False


def test_die_if_hint_pep_unsupported(hints_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilpeptest.die_if_hint_pep_unsupported`
    validator.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        List of PEP-compliant type hint metadata describing sample PEP-compliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
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
    from pytest import raises

    # Assert this validator...
    for hint_pep_meta in hints_pep_meta:
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
