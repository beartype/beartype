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
# from beartype_test.util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS ~ type                      }....................
def test_pep585() -> None:
    '''
    Test `PEP 585`_ support implemented in the :func:`beartype.beartype`
    decorator.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.proposal.utilhintpep585 import is_hint_pep585
    from beartype_test.unit.data.hint.pep.data_hintpep import HINT_PEP_TO_META

    # Assert this tester accepts only PEP 585-compliant type hints.
    for hint_pep, hint_pep_meta in HINT_PEP_TO_META.items():
        assert is_hint_pep585(hint_pep) is hint_pep_meta.is_pep585
