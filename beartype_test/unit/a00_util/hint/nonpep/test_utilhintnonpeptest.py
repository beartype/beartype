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
    from beartype_test.unit.data.hint.data_hint import (
        NOT_HINTS_UNHASHABLE, HINTS_NONPEP, NOT_HINTS_NONPEP,)

    # Assert this function accepts PEP-noncompliant type hints.
    for nonhint_pep in HINTS_NONPEP:
        assert is_hint_nonpep(nonhint_pep) is True

    # Assert this function rejects objects excepted to be rejected.
    for non_nonhint_pep in NOT_HINTS_NONPEP:
        assert is_hint_nonpep(non_nonhint_pep) is False

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
    from beartype_test.unit.data.hint.data_hint import (
        NOT_HINTS_UNHASHABLE, HINTS_NONPEP, NOT_HINTS_NONPEP,)

    # Assert this function accepts PEP-noncompliant type hints.
    for nonhint_pep in HINTS_NONPEP:
        die_unless_hint_nonpep(nonhint_pep)

    # Assert this function rejects objects excepted to be rejected.
    for non_nonhint_pep in NOT_HINTS_NONPEP:
        with raises_uncached(BeartypeDecorHintNonPepException):
            die_unless_hint_nonpep(non_nonhint_pep)

    # Assert this function rejects unhashable objects.
    for non_hint_unhashable in NOT_HINTS_UNHASHABLE:
        with raises(TypeError):
            die_unless_hint_nonpep(non_hint_unhashable)
