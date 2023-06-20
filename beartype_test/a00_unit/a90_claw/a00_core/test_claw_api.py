#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **import hooks subpackage API unit tests** (i.e., unit tests exercising
that the :mod:`beartype.claw` subpackage exports the expected public attributes
with the expected types).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_claw_api() -> None:
    '''
    Test that the :mod:`beartype.claw` subpackage exports the expected public
    attributes with the expected types.
    '''

    # Defer test-specific imports.
    from beartype.claw import (
        beartype_all,
        beartype_package,
        beartype_packages,
        beartype_this_package,
        beartyping,
    )
    from beartype._util.func.utilfunctest import is_func_python

    # Tuple of all import hooks exported by the "beartype.claw" API.
    BEARTYPE_CLAW_FUNCS = (
        beartype_all,
        beartype_package,
        beartype_packages,
        beartype_this_package,
        beartyping,
    )

    # Assert that these imports are all pure-Python functions.
    for beartype_claw_func in BEARTYPE_CLAW_FUNCS:
        assert is_func_python(beartype_claw_func) is True
