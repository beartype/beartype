#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`593` **unit tests.**

This submodule unit tests :pep:`593` support implemented in the
:func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_is_hint_pep593() -> None:
    '''
    Test the :beartype._util.hint.pep.proposal.utilpep593.is_hint_pep593`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from beartype._util.hint.pep.proposal.utilpep593 import (
        is_hint_pep593)
    from typing import Optional

    # If the active Python interpreter targets at least Python >= 3.9 and thus
    # supports PEP 593, assert this tester accepts annotated type hints.
    if IS_PYTHON_AT_LEAST_3_9:
        from typing import Annotated
        assert is_hint_pep593(Annotated[Optional[str], int]) is True

    # Assert this tester rejects unannotated type hints in either case.
    assert is_hint_pep593(Optional[str]) is False
