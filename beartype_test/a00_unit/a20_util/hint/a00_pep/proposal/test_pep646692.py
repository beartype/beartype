#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`646` and :pep:`692` **type hint utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep646692` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_is_hint_pep646_tuple_unpacked_prefix() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep646692.is_hint_pep646_tuple_unpacked_prefix`
    tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep646692 import (
        is_hint_pep646_tuple_unpacked_prefix,
        make_hint_pep646_tuple_unpacked_prefix,
    )
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11

    # ....................{ VERSION                        }....................
    # If the active Python interpreter targets Python >= 3.11 and thus supports
    # PEP 646...
    if IS_PYTHON_AT_LEAST_3_11:
        # PEP 646-compliant unpacked child tuple hint subscripted by arbitrary
        # child child hints.
        hint_pep646_tuple_unpacked = make_hint_pep646_tuple_unpacked_prefix(
            (int, float))

        # Assert this tester accepts this hint.
        assert is_hint_pep646_tuple_unpacked_prefix(
            hint_pep646_tuple_unpacked) is True
    # Else, the active Python interpreter targets Python <= 3.10 and thus fails
    # to support PEP 646.

    # ....................{ FAIL                           }....................
    # Assert this tester rejects PEP 484- and 585-compliant tuple type hints of
    # both fixed- and variable-length variants.
    assert is_hint_pep646_tuple_unpacked_prefix(tuple[int, ...]) is False
    assert is_hint_pep646_tuple_unpacked_prefix(tuple[bool, int, float]) is False

    # Assert this tester rejects unrelated arbitrary objects.
    assert is_hint_pep646_tuple_unpacked_prefix(
        'The Titans fierce, self-hid, or prison-bound,') is False
