#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype module utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.py.utilpymodule` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# from pytest import raises

# ....................{ TESTS                             }....................
def test_import_module_attr() -> None:
    '''
    Test the :func:`beartype._util.py.utilpymodule.import_module_attr`
    function.
    '''

    # Defer heavyweight imports.
    from beartype._util.py.utilpymodule import import_module_attr
