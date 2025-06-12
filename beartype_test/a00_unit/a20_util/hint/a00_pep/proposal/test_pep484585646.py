#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-, :pep:`585`-, and :pep:`646`-compliant **tuple type
hint utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep484585646` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_is_hint_pep484585646_tuple_empty() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585646.is_hint_pep484585646_tuple_empty`
    tester.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep484585646 import (
        is_hint_pep484585646_tuple_empty)
    from typing import Tuple  # <-- intentionally import the PEP 484 variant

    # Assert this tester returns true for PEP 484-compliant empty tuple type
    # hints.
    assert is_hint_pep484585646_tuple_empty(Tuple[()]) is True

    # Assert this tester returns false for PEP 484-compliant non-empty tuple
    # type hints.
    assert is_hint_pep484585646_tuple_empty(Tuple[int, ...]) is False

    # Assert this tester returns true for PEP 585-compliant empty tuple type
    # hints.
    assert is_hint_pep484585646_tuple_empty(tuple[()]) is True

    # Assert this tester returns false for PEP 585-compliant non-empty tuple
    # type hints.
    assert is_hint_pep484585646_tuple_empty(tuple[int, ...]) is False
