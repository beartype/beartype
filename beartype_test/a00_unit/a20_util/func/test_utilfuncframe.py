#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Call stack utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.utilfuncframe` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_get_func_stack_frame() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncframe.get_frame` attribute.
    '''

    # Defer heavyweight imports.
    from beartype._util.func.utilfuncframe import get_frame

    # Assert this attribute is a callable under both CPython and PyPy.
    assert callable(get_frame) is True
