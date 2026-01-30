#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-agnostic type hint tester utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.utilhinttest` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ raiser                     }....................
def test_die_unless_hint(hints_pep_meta) -> None:
    '''
    Test the :func:`beartype._util.hint.utilhinttest.die_unless_hint` raiser.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta.HintPepMetadata]
        List of type hint metadata describing sample type hints exercising edge
        cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype.roar import (
        BeartypeDecorHintNonpepException,
        BeartypeDecorHintPepUnsupportedException,
    )
    from beartype._util.hint.utilhinttest import die_unless_hint
    from beartype_test.a00_unit.data.hint.data_hint import (
        HINTS_NONPEP,
        NOT_HINTS,
    )
    from pytest import raises

    # Assert this function accepts PEP-noncompliant type hints.
    for nonhint_pep in HINTS_NONPEP:
        die_unless_hint(nonhint_pep)

    # Assert this function...
    for hint_pep_meta in hints_pep_meta:
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

# ....................{ TESTS ~ tester                     }....................
def test_is_hint(hints_pep_meta) -> None:
    '''
    Test the :func:`beartype._util.hint.utilhinttest.is_hint` tester.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.metadata.data_hintpithmeta.HintPepMetadata]
        List of type hint metadata describing sample type hints exercising edge
        cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.utilhinttest import is_hint
    from beartype_test.a00_unit.data.hint.data_hint import (
        HINTS_NONPEP,
        NOT_HINTS,
    )

    # Assert this tester accepts PEP-noncompliant type hints.
    for nonhint_pep in HINTS_NONPEP:
        assert is_hint(nonhint_pep) is True

    # Assert this tester:
    # * Accepts supported PEP-compliant type hints.
    # * Rejects unsupported PEP-compliant type hints.
    for hint_pep_meta in hints_pep_meta:
        assert is_hint(hint_pep_meta.hint) is hint_pep_meta.is_supported

    # Assert this tester rejects objects *NOT* supported as either
    # PEP-noncompliant or -compliant type hints.
    for non_hint in NOT_HINTS:
        assert is_hint(non_hint) is False
