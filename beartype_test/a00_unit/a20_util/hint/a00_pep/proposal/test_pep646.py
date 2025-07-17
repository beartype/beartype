#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`646` **type hint utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep646692` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_is_hint_pep646_unpacked_tuple() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep646692.is_hint_pep646_unpacked_tuple`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep646692 import (
        is_hint_pep646_unpacked_tuple)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11

    # ....................{ VERSION                        }....................
    # If the active Python interpreter targets Python >= 3.11 and thus supports
    # PEP 646...
    if IS_PYTHON_AT_LEAST_3_11:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.data_pep646 import (
            unit_test_is_hint_pep646_unpacked_tuple)

        # Perform this test.
        unit_test_is_hint_pep646_unpacked_tuple()
    # Else, the active Python interpreter targets Python <= 3.10 and thus fails
    # to support PEP 646.

    # ....................{ FAIL                           }....................
    # Assert this tester rejects PEP 484- and 585-compliant tuple type hints of
    # both fixed- and variable-length variants.
    assert is_hint_pep646_unpacked_tuple(tuple[int, ...]) is False
    assert is_hint_pep646_unpacked_tuple(tuple[bool, int, float]) is False

    # Assert this tester rejects unrelated arbitrary objects.
    assert is_hint_pep646_unpacked_tuple(
        'The Titans fierce, self-hid, or prison-bound,') is False
