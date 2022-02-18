#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
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
        BeartypeDecorHintNonpepException,
        BeartypeDecorHintPepUnsupportedException,
    )
    from beartype._util.hint.utilhinttest import die_unless_hint
    from beartype_test.a00_unit.data.hint.data_hint import (
        NOT_HINTS, HINTS_NONPEP)
    from beartype_test.a00_unit.data.hint.pep.data_pep import (
        HINTS_PEP_META)

    # Assert this function accepts PEP-noncompliant type hints.
    for nonhint_pep in HINTS_NONPEP:
        die_unless_hint(nonhint_pep)

    # Assert this function...
    for hint_pep_meta in HINTS_PEP_META:
        # Accepts supported PEP-compliant type hints.
        if hint_pep_meta.is_supported:
            die_unless_hint(hint_pep_meta.hint)
        # Rejects unsupported PEP-compliant type hints.
        else:
            with raises(BeartypeDecorHintPepUnsupportedException):
                die_unless_hint(hint_pep_meta.hint)

    # Assert this function rejects objects *NOT* supported as either
    # PEP-noncompliant or -compliant type hints.
    for non_hint in NOT_HINTS:
        with raises(BeartypeDecorHintNonpepException):
            die_unless_hint(non_hint)


def test_is_hint() -> None:
    '''
    Test the :func:`beartype._util.hint.utilhinttest.is_hint` tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.utilhinttest import is_hint
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS, HINTS_NONPEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import HINTS_PEP_META

    # Assert this function accepts PEP-noncompliant type hints.
    for nonhint_pep in HINTS_NONPEP:
        assert is_hint(nonhint_pep) is True

    # Assert this function:
    # * Accepts supported PEP-compliant type hints.
    # * Rejects unsupported PEP-compliant type hints.
    for hint_pep_meta in HINTS_PEP_META:
        assert is_hint(hint_pep_meta.hint) is hint_pep_meta.is_supported

    # Assert this function rejects objects *NOT* supported as either
    # PEP-noncompliant or -compliant type hints.
    for non_hint in NOT_HINTS:
        assert is_hint(non_hint) is False


# Prevent pytest from capturing and displaying all expected non-fatal
# beartype-specific warnings emitted by the is_hint_ignorable() tester.
# @ignore_warnings(BeartypeDecorHintPepIgnorableDeepWarning)
def test_is_hint_ignorable() -> None:
    '''
    Test the :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.utilhinttest import is_hint_ignorable
    from beartype_test.a00_unit.data.hint.data_hint import (
        HINTS_IGNORABLE,
        HINTS_NONPEP_UNIGNORABLE,
    )
    from beartype_test.a00_unit.data.hint.pep.data_pep import HINTS_PEP_META

    # Assert this function accepts ignorable type hints.
    for hint_ignorable in HINTS_IGNORABLE:
        assert is_hint_ignorable(hint_ignorable) is True

    # Assert this function rejects unignorable PEP-noncompliant type hints.
    for hint_unignorable in HINTS_NONPEP_UNIGNORABLE:
        assert is_hint_ignorable(hint_unignorable) is False

    # Assert this function:
    # * Accepts unignorable PEP-compliant type hints.
    # * Rejects ignorable PEP-compliant type hints.
    for hint_pep_meta in HINTS_PEP_META:
        assert is_hint_ignorable(hint_pep_meta.hint) is (
            hint_pep_meta.is_ignorable)
