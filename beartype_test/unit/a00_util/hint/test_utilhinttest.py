#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-agnostic type hint tester utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.utilhinttest` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# from beartype.roar import BeartypeDecorHintPepIgnorableDeepWarning
# from beartype_test.util.mark.pytmark import ignore_warnings
from pytest import raises

# ....................{ TESTS                             }....................
def test_die_unless_hint() -> None:
    '''
    Test the :func:`beartype._util.hint.utilhinttest.die_unless_hint`
    validator.
    '''

    # Defer heavyweight imports.
    from beartype.roar import (
        BeartypeDecorHintNonPepException,
        BeartypeDecorHintPepUnsupportedException,
    )
    from beartype._util.hint.utilhinttest import die_unless_hint
    from beartype_test.unit.data.hint.data_hint import (
        NOT_HINTS_UNHASHABLE,
        NOT_HINTS_HASHABLE,
        HINTS_NONPEP,
    )
    from beartype_test.unit.data.hint.pep.data_hintpep import HINT_PEP_TO_META

    # Assert this function accepts PEP-noncompliant type hints.
    for nonhint_pep in HINTS_NONPEP:
        die_unless_hint(nonhint_pep)

    # Assert this function...
    for hint_pep, hint_pep_meta in HINT_PEP_TO_META.items():
        # Accepts supported PEP-compliant type hints.
        if hint_pep_meta.is_supported:
            die_unless_hint(hint_pep)
        # Rejects unsupported PEP-compliant type hints.
        else:
            with raises(BeartypeDecorHintPepUnsupportedException):
                die_unless_hint(hint_pep)

    # Assert this function rejects objects that are neither PEP-noncompliant
    # type hints nor supported PEP-compliant type hints.
    for non_hint_hashable in NOT_HINTS_HASHABLE:
        with raises(BeartypeDecorHintNonPepException):
            die_unless_hint(non_hint_hashable)

    # Assert this function rejects unhashable objects.
    for non_hint_unhashable in NOT_HINTS_UNHASHABLE:
        with raises(TypeError):
            die_unless_hint(non_hint_unhashable)


def test_is_hint() -> None:
    '''
    Test the :func:`beartype._util.hint.utilhinttest.is_hint` tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.utilhinttest import is_hint
    from beartype_test.unit.data.hint.data_hint import (
        NOT_HINTS_UNHASHABLE,
        NOT_HINTS_HASHABLE,
        HINTS_NONPEP,
    )
    from beartype_test.unit.data.hint.pep.data_hintpep import HINT_PEP_TO_META

    # Assert this function accepts PEP-noncompliant type hints.
    for nonhint_pep in HINTS_NONPEP:
        assert is_hint(nonhint_pep) is True

    # Assert this function:
    # * Accepts supported PEP-compliant type hints.
    # * Rejects unsupported PEP-compliant type hints.
    for hint_pep, hint_pep_meta in HINT_PEP_TO_META.items():
        assert is_hint(hint_pep) is hint_pep_meta.is_supported

    # Assert this function rejects objects that are neither PEP-noncompliant
    # type hints *NOR* supported PEP-compliant type hints.
    for non_hint_hashable in NOT_HINTS_HASHABLE:
        assert is_hint(non_hint_hashable) is False

    # Assert this function rejects unhashable objects.
    for non_hint_unhashable in NOT_HINTS_UNHASHABLE:
        with raises(TypeError):
            is_hint(non_hint_unhashable)


# Prevent pytest from capturing and displaying all expected non-fatal
# beartype-specific warnings emitted by the is_hint_ignorable() tester.
# @ignore_warnings(BeartypeDecorHintPepIgnorableDeepWarning)
def test_is_hint_ignorable() -> None:
    '''
    Test the :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.utilhinttest import is_hint_ignorable
    from beartype_test.unit.data.hint.data_hint import (
        HINTS_IGNORABLE,
        HINTS_NONPEP_UNIGNORABLE,
    )
    from beartype_test.unit.data.hint.pep.data_hintpep import HINT_PEP_TO_META

    # Assert this function accepts ignorable type hints.
    for hint_ignorable in HINTS_IGNORABLE:
        assert is_hint_ignorable(hint_ignorable) is True

    # Assert this function rejects unignorable PEP-noncompliant type hints.
    for hint_unignorable in HINTS_NONPEP_UNIGNORABLE:
        assert is_hint_ignorable(hint_unignorable) is False

    # Assert this function:
    # * Accepts unignorable PEP-compliant type hints.
    # * Rejects ignorable PEP-compliant type hints.
    for hint_pep, hint_pep_meta in HINT_PEP_TO_META.items():
        assert is_hint_ignorable(hint_pep) is hint_pep_meta.is_ignorable
