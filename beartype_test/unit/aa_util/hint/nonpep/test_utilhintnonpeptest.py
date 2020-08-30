#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-noncompliant type hint utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.nonpep.utilhintnonpeptest` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.pyterror import raises_uncached
from pytest import raises

# ....................{ TESTS                             }....................
def test_is_hint_nonpep() -> None:
    '''
    Test the
    :func:`beartype._util.hint.nonpep.utilhintnonpeptest.is_hint_nonpep`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.nonpep.utilhintnonpeptest import is_hint_nonpep
    from beartype_test.unit.data.data_hint import (
        NOT_HINTS_UNHASHABLE, NONPEP_HINTS, NOT_NONPEP_HINTS,)

    # Assert this function accepts PEP-noncompliant type hints.
    for nonpep_hint in NONPEP_HINTS:
        assert is_hint_nonpep(nonpep_hint) is True

    # Assert this function rejects objects excepted to be rejected.
    for non_nonpep_hint in NOT_NONPEP_HINTS:
        assert is_hint_nonpep(non_nonpep_hint) is False

    # Assert this function rejects unhashable objects.
    for non_hint_unhashable in NOT_HINTS_UNHASHABLE:
        with raises(TypeError):
            is_hint_nonpep(non_hint_unhashable)


def test_die_unless_hint_nonpep() -> None:
    '''
    Test the
    :func:`beartype._util.hint.nonpep.utilhintnonpeptest.die_unless_hint_nonpep`
    validator.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintNonPepException
    from beartype._util.hint.nonpep.utilhintnonpeptest import die_unless_hint_nonpep
    from beartype_test.unit.data.data_hint import (
        NOT_HINTS_UNHASHABLE, NONPEP_HINTS, NOT_NONPEP_HINTS,)

    # Assert this function accepts PEP-noncompliant type hints.
    for nonpep_hint in NONPEP_HINTS:
        die_unless_hint_nonpep(nonpep_hint)

    # Assert this function rejects objects excepted to be rejected.
    for non_nonpep_hint in NOT_NONPEP_HINTS:
        with raises_uncached(BeartypeDecorHintNonPepException):
            die_unless_hint_nonpep(non_nonpep_hint)

    # Assert this function rejects unhashable objects.
    for non_hint_unhashable in NOT_HINTS_UNHASHABLE:
        with raises(TypeError):
            die_unless_hint_nonpep(non_hint_unhashable)
