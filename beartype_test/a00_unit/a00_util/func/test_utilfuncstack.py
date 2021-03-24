#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Call stack utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.utilfuncstack` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_get_func_stack_frame_getter_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncstack.get_func_stack_frame_getter_or_none` function.
    '''

    # Defer heavyweight imports.
    from beartype._util.func.utilfuncstack import (
        get_func_stack_frame_getter_or_none)

    # Assert this function returns a callable under both CPython and PyPy.
    assert callable(get_func_stack_frame_getter_or_none()) is True
