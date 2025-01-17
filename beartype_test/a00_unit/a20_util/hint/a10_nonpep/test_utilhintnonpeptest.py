#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-noncompliant type hint utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.nonpep.utilnonpeptest` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ raiser                     }....................
def test_die_unless_hint_nonpep(not_hints_nonpep) -> None:
    '''
    Test the
    :func:`beartype._util.hint.nonpep.utilnonpeptest.die_unless_hint_nonpep`
    validator.

    Parameters
    ----------
    not_hints_nonpep : frozenset
        Frozen set of various objects that are *not* PEP-noncompliant type hints
        exercising well-known edge cases.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintNonpepException
    from beartype._util.hint.nonpep.utilnonpeptest import (
        die_unless_hint_nonpep)
    from beartype_test.a00_unit.data.hint.data_hint import (
        HINTS_NONPEP,
        NOT_HINTS_UNHASHABLE,
    )
    from pytest import raises

    # ....................{ ASSERTS                        }....................
    # Assert this function accepts PEP-noncompliant type hints.
    for hint_nonpep in HINTS_NONPEP:
        die_unless_hint_nonpep(hint_nonpep, is_forwardref_valid=True)

    # Assert this function rejects objects excepted to be rejected.
    for not_hint_nonpep in not_hints_nonpep:
        with raises(BeartypeDecorHintNonpepException):
            die_unless_hint_nonpep(
                not_hint_nonpep, is_forwardref_valid=True)

    # Assert this function rejects unhashable objects.
    for not_hint_unhashable in NOT_HINTS_UNHASHABLE:
        with raises(BeartypeDecorHintNonpepException):
            die_unless_hint_nonpep(
                not_hint_unhashable, is_forwardref_valid=True)

# ....................{ TESTS ~ tester                     }....................
def test_is_hint_nonpep(not_hints_nonpep) -> None:
    '''
    Test the
    :func:`beartype._util.hint.nonpep.utilnonpeptest.is_hint_nonpep`
    tester.

    Parameters
    ----------
    not_hints_nonpep : frozenset
        Frozen set of various objects that are *not* PEP-noncompliant type hints
        exercising well-known edge cases.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.hint.nonpep.utilnonpeptest import is_hint_nonpep
    from beartype_test.a00_unit.data.hint.data_hint import (
        HINTS_NONPEP,
        NOT_HINTS_UNHASHABLE,
    )

    # ....................{ ASSERTS                        }....................
    # Assert this function accepts PEP-noncompliant type hints.
    for hint_nonpep in HINTS_NONPEP:
        assert is_hint_nonpep(
            hint=hint_nonpep, is_forwardref_valid=True) is True

    # Assert this function rejects objects excepted to be rejected.
    for not_hint_nonpep in not_hints_nonpep:
        assert is_hint_nonpep(
            hint=not_hint_nonpep, is_forwardref_valid=True) is False

    # Assert this function rejects unhashable objects.
    for non_hint_unhashable in NOT_HINTS_UNHASHABLE:
        assert is_hint_nonpep(
            hint=non_hint_unhashable, is_forwardref_valid=True) is False


def test_is_hint_nonpep_tuple(not_hints_nonpep) -> None:
    '''
    Test the
    :func:`beartype._util.hint.nonpep.utilnonpeptest._is_hint_nonpep_tuple`
    tester.

    Parameters
    ----------
    not_hints_nonpep : frozenset
        Frozen set of various objects that are *not* PEP-noncompliant type hints
        exercising well-known edge cases.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.hint.nonpep.utilnonpeptest import _is_hint_nonpep_tuple
    from beartype_test.a00_unit.data.hint.data_hint import (
        HINTS_NONPEP,
        NOT_HINTS_UNHASHABLE,
    )

    # ....................{ ASSERTS                        }....................
    # Assert this function accepts PEP-noncompliant tuples.
    for hint_nonpep in HINTS_NONPEP:
        assert _is_hint_nonpep_tuple(hint_nonpep, True) is isinstance(
            hint_nonpep, tuple)

    # Assert this function rejects objects excepted to be rejected.
    for not_hint_nonpep in not_hints_nonpep:
        assert _is_hint_nonpep_tuple(not_hint_nonpep, True) is False

    # Assert this function rejects unhashable objects.
    for non_hint_unhashable in NOT_HINTS_UNHASHABLE:
        assert _is_hint_nonpep_tuple(non_hint_unhashable, True) is False
