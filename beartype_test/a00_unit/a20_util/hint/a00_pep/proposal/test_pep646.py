#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`646` **type hint utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep646` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_is_pep646_hint_tuple_unpacked() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep646.is_pep646_hint_tuple_unpacked`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep646 import (
        is_pep646_hint_tuple_unpacked)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11

    # ....................{ VERSION                        }....................
    # If the active Python interpreter targets Python >= 3.11 and thus supports
    # PEP 646...
    if IS_PYTHON_AT_LEAST_3_11:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.data_pep646 import (
            unit_test_is_pep646_hint_tuple_unpacked)

        # Perform this test.
        unit_test_is_pep646_hint_tuple_unpacked()
    # Else, the active Python interpreter targets Python <= 3.10 and thus fails
    # to support PEP 646.

    # ....................{ FAIL                           }....................
    # Assert this tester rejects PEP 484- and 585-compliant tuple type hints of
    # both fixed- and variable-length variants.
    assert is_pep646_hint_tuple_unpacked(tuple[int, ...]) is False
    assert is_pep646_hint_tuple_unpacked(tuple[bool, int, float]) is False

    # Assert this tester rejects unrelated arbitrary objects.
    assert is_pep646_hint_tuple_unpacked(
        'The Titans fierce, self-hid, or prison-bound,') is False
