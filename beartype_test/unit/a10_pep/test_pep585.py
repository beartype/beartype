#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 585`_ **unit tests.**

This submodule unit tests `PEP 585`_ support implemented in the
:func:`beartype.beartype` decorator.

.. _PEP 585:
   https://www.python.org/dev/peps/pep-0585
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from typing import Set

# ....................{ TESTS ~ type                      }....................
def test_pep585() -> None:
    '''
    Test `PEP 585`_ support implemented in the :func:`beartype.beartype`
    decorator.
    '''

    # Defer heavyweight imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from beartype._util.hint.pep.proposal.utilhintpep585 import (
        is_hint_pep585)

    # If the active Python interpreter targets at least Python >= 3.9 and thus
    # supports PEP 585, assert this function accepts PEP 585 type hints.
    if IS_PYTHON_AT_LEAST_3_9:
        assert is_hint_pep585(set[int]) is True

    # Assert this function rejects unannotated type hints in either case.
    assert is_hint_pep585(Set[int]) is False
