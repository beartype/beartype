#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python interpreter** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.py.utilpyinterpreter` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                    }....................
def test_is_py_pypy() -> None:
    '''
    Test the :func:`beartype._util.py.utilpyinterpreter.is_py_pypy` tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.py.utilpyinterpreter import is_py_pypy

    # Assert this tester returns a boolean.
    IS_PY_PYPY = is_py_pypy()
    assert isinstance(IS_PY_PYPY, bool)
