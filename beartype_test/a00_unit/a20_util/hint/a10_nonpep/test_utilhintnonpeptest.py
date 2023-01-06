#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-noncompliant type hint utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.nonpep.utilnonpeptest` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ TESTS ~ validator                 }....................
def test_die_unless_hint_nonpep() -> None:
    '''
    Test the
    :func:`beartype._util.hint.nonpep.utilnonpeptest.die_unless_hint_nonpep`
    validator.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintNonpepException
    from beartype._util.hint.nonpep.utilnonpeptest import (
        die_unless_hint_nonpep)
    from beartype_test.a00_unit.data.hint.data_hint import (
        NOT_HINTS_UNHASHABLE, HINTS_NONPEP, NOT_HINTS_NONPEP,)

    # Assert this function accepts PEP-noncompliant type hints.
    for hint_nonpep in HINTS_NONPEP:
        die_unless_hint_nonpep(hint_nonpep)

    # Assert this function rejects objects excepted to be rejected.
    for not_hint_nonpep in NOT_HINTS_NONPEP:
        with raises(BeartypeDecorHintNonpepException):
            die_unless_hint_nonpep(not_hint_nonpep)

    # Assert this function rejects unhashable objects.
    for not_hint_unhashable in NOT_HINTS_UNHASHABLE:
        with raises(BeartypeDecorHintNonpepException):
            die_unless_hint_nonpep(not_hint_unhashable)

# ....................{ TESTS ~ tester                    }....................
def test_is_hint_nonpep() -> None:
    '''
    Test the
    :func:`beartype._util.hint.nonpep.utilnonpeptest.is_hint_nonpep`
    tester.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.nonpep.utilnonpeptest import is_hint_nonpep
    from beartype_test.a00_unit.data.hint.data_hint import (
        NOT_HINTS_UNHASHABLE, HINTS_NONPEP, NOT_HINTS_NONPEP,)

    # Assert this function accepts PEP-noncompliant type hints.
    for hint_nonpep in HINTS_NONPEP:
        assert is_hint_nonpep(hint=hint_nonpep, is_str_valid=True) is True

    # Assert this function rejects objects excepted to be rejected.
    for not_hint_nonpep in NOT_HINTS_NONPEP:
        assert is_hint_nonpep(hint=not_hint_nonpep, is_str_valid=True) is False

    # Assert this function rejects unhashable objects.
    for non_hint_unhashable in NOT_HINTS_UNHASHABLE:
        assert is_hint_nonpep(
            hint=non_hint_unhashable, is_str_valid=True) is False


def test_is_hint_nonpep_tuple() -> None:
    '''
    Test the
    :func:`beartype._util.hint.nonpep.utilnonpeptest._is_hint_nonpep_tuple`
    tester.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.nonpep.utilnonpeptest import (
        _is_hint_nonpep_tuple)
    from beartype_test.a00_unit.data.hint.data_hint import (
        NOT_HINTS_UNHASHABLE, HINTS_NONPEP, NOT_HINTS_NONPEP,)

    # Assert this function accepts PEP-noncompliant tuples.
    for hint_nonpep in HINTS_NONPEP:
        assert _is_hint_nonpep_tuple(hint_nonpep, True) is isinstance(
            hint_nonpep, tuple)

    # Assert this function rejects objects excepted to be rejected.
    for not_hint_nonpep in NOT_HINTS_NONPEP:
        assert _is_hint_nonpep_tuple(not_hint_nonpep, True) is False

    # Assert this function rejects unhashable objects.
    for non_hint_unhashable in NOT_HINTS_UNHASHABLE:
        assert _is_hint_nonpep_tuple(non_hint_unhashable, True) is False
