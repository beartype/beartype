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
def test_is_hint_pep484585646_tuple_variadic() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585646.is_hint_pep484585646_tuple_variadic`
    tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep484585646 import (
        is_hint_pep484585646_tuple_variadic)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11
    from typing import Tuple  # <-- intentionally import the PEP 484 variant

    # ....................{ VERSION                        }....................
    # If the active Python interpreter targets Python >= 3.11 and thus supports
    # PEP 646...
    if IS_PYTHON_AT_LEAST_3_11:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.data_pep646 import (
            tuple_fixed_str_bytes_unpacked_prefix,
            tuple_fixed_str_bytes_unpacked_subbed,
            tuple_variadic_strs_unpacked_prefix,
            tuple_variadic_strs_unpacked_subbed,
        )

        # Assert that this tester accepts a PEP 646-compliant unpacked
        # variable-length tuple hint in both prefix and subscription flavours.
        assert is_hint_pep484585646_tuple_variadic(
            tuple_variadic_strs_unpacked_prefix) is True
        assert is_hint_pep484585646_tuple_variadic(
            tuple_variadic_strs_unpacked_subbed) is True

        # Assert that this tester rejects a PEP 646-compliant unpacked
        # fixed-length tuple hint in both prefix and subscription flavours.
        assert is_hint_pep484585646_tuple_variadic(
            tuple_fixed_str_bytes_unpacked_prefix) is False
        assert is_hint_pep484585646_tuple_variadic(
            tuple_fixed_str_bytes_unpacked_subbed) is False
    # Else, the active Python interpreter targets Python <= 3.10 and thus fails
    # to support PEP 646.

    # ....................{ PASS                           }....................
    # Assert that this tester accepts a variable-length tuple hint in both PEP
    # 484 and 585 flavours.
    assert is_hint_pep484585646_tuple_variadic(Tuple[int, ...])
    assert is_hint_pep484585646_tuple_variadic(tuple[str, ...])

    # ....................{ FAIL                           }....................
    # Assert this tester rejects an arbitrary object.
    assert is_hint_pep484585646_tuple_variadic(
        "And listen'd in sharp pain for Saturn's voice.") is False


def test_is_hint_pep484585646_tuple_empty() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585646.is_hint_pep484585646_tuple_empty`
    tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep484585646 import (
        is_hint_pep484585646_tuple_empty)
    from typing import Tuple  # <-- intentionally import the PEP 484 variant

    # ....................{ PASS                           }....................
    # Assert this tester returns true for PEP 484-compliant empty tuple type
    # hints.
    assert is_hint_pep484585646_tuple_empty(Tuple[()]) is True

    # Assert this tester returns true for PEP 585-compliant empty tuple type
    # hints.
    assert is_hint_pep484585646_tuple_empty(tuple[()]) is True

    # ....................{ FAIL                           }....................
    # Assert this tester returns false for PEP 484-compliant non-empty tuple
    # type hints.
    assert is_hint_pep484585646_tuple_empty(Tuple[int, ...]) is False

    # Assert this tester returns false for PEP 585-compliant non-empty tuple
    # type hints.
    assert is_hint_pep484585646_tuple_empty(tuple[int, ...]) is False

    # Assert this tester returns false for arbitrary objects.
    assert is_hint_pep484585646_tuple_empty(
        "Groan'd for the old allegiance once more,") is False
