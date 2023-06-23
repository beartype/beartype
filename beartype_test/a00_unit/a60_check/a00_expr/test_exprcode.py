#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-compliant type-checking code generator unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._check.code.codemake` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ pass : check               }....................
def test_make_check_code_decoration() -> None:
    '''
    Test the :func:`beartype._check.code.codemake.make_check_expr`
    function.
    '''

    # Defer test-specific imports.
    from beartype._check.code.codemake import make_check_expr
    from beartype._conf.confcls import BEARTYPE_CONF_DEFAULT

    # Assert this function generates identical code for identical hints and is
    # thus cached via memoization.
    assert (
        make_check_expr(str, BEARTYPE_CONF_DEFAULT) is
        make_check_expr(str, BEARTYPE_CONF_DEFAULT)
    )
