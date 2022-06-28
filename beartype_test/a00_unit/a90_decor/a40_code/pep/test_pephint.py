#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-compliant type-checking code generator unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._decor._code._pep._pephint` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ pass : check              }....................
def test_pep_code_check_hint() -> None:
    '''
    Test the :func:`beartype._decor._code._pep._pephint.pep_code_check_hint`
    function.
    '''

    # Defer heavyweight imports.
    from beartype._decor._code._pep._pephint import pep_code_check_hint

    # Assert this function generates identical code for identical hints and is
    # thus cached via memoization.
    assert pep_code_check_hint(str) is pep_code_check_hint(str)
