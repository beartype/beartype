#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 593`_ **unit tests.**

This submodule unit tests `PEP 593`_ support implemented in the
:func:`beartype.beartype` decorator.

.. _PEP 593:
   https://www.python.org/dev/peps/pep-0593
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from typing import List

# ....................{ TESTS ~ type                      }....................
def test_pep593() -> None:
    '''
    Test `PEP 593`_ support implemented in the :func:`beartype.beartype`
    decorator.
    '''

    # Defer heavyweight imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from beartype._util.hint.pep.proposal.utilhintpep593 import (
        is_hint_pep593)

    # If the active Python interpreter targets at least Python >= 3.9 and thus
    # supports PEP 593, assert this function accepts annotated type hints.
    if IS_PYTHON_AT_LEAST_3_9:
        from typing import Annotated
        assert is_hint_pep593(Annotated[List[str], int]) is True

    # Assert this function rejects unannotated type hints in either case.
    assert is_hint_pep593(List[str]) is False
