#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-compliant type-checking code generator unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._check.expr.exprcode` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ pass : check               }....................
def test_make_check_code_decoration() -> None:
    '''
    Test the :func:`beartype._check.expr.exprcode.make_check_expr`
    function.
    '''

    # Defer heavyweight imports.
    from beartype._check.expr.exprcode import make_check_expr

    # Assert this function generates identical code for identical hints and is
    # thus cached via memoization.
    assert make_check_expr(str) is make_check_expr(str)
