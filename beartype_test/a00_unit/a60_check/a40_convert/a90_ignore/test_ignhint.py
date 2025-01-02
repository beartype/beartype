#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-agnostic type hint ignorability detection** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._check.convert._ignore.ignhint` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytmark import ignore_warnings

# ....................{ TESTS ~ raiser                     }....................
# Prevent pytest from capturing and displaying all expected non-fatal
# beartype-specific warnings emitted by this test. Urgh!
@ignore_warnings(DeprecationWarning)
def test_is_hint_sanified_ignorable(hints_pep_meta, hints_ignorable) -> None:
    '''
    Test the
    :func:`beartype._check.convert.convsanify.is_hint_sanified_ignorable`
    tester.

    Parameters
    ----------
    hints_pep_meta : tuple[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        Tuple of type hint metadata describing sample type hints exercising edge
        cases in the :mod:`beartype` codebase.
    hints_ignorable : frozenset
        Frozen set of ignorable PEP-agnostic type hints.
    '''

    # Defer test-specific imports.
    # from beartype._check.convert._ignore.ignhint import is_hint_ignorable
    from beartype._check.convert.convsanify import is_hint_sanified_ignorable
    from beartype_test.a00_unit.data.hint.data_hint import (
        HINTS_NONPEP_UNIGNORABLE)

    # Assert this tester accepts ignorable type hints.
    for hint_ignorable in hints_ignorable:
        assert is_hint_sanified_ignorable(hint_ignorable) is True

    # Assert this tester rejects unignorable PEP-noncompliant type hints.
    for hint_unignorable in HINTS_NONPEP_UNIGNORABLE:
        assert is_hint_sanified_ignorable(hint_unignorable) is False

    # Assert this tester:
    # * Accepts unignorable PEP-compliant type hints.
    # * Rejects ignorable PEP-compliant type hints.
    for hint_pep_meta in hints_pep_meta:
        assert is_hint_sanified_ignorable(hint_pep_meta.hint) is (
            hint_pep_meta.is_ignorable)
