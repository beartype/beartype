#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`604` **type hint utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.utilpep604` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_is_hint_pep604() -> None:
    '''
    Test usage of the private
    :mod:`beartype._util.hint.pep.proposal.utilpep604.is_hint_pep604` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.utilpep604 import is_hint_pep604
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10

    # If the active Python interpreter targets Python >= 3.10 and thus supports
    # PEP 604...
    if IS_PYTHON_AT_LEAST_3_10:
        # Assert this tester accepts a PEP 604-compliant union. 
        assert is_hint_pep604(int | str | None) is True
    # Else, this interpreter targets Python < 3.10 and thus fails to support PEP
    # 604.

    # Assert this tester rejects an arbitrary PEP 604-noncompliant object.
    is_hint_pep604('Meet in the vale, and one majestic River,')
