#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype callable code object utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.utilfunctest` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ TESTS                             }....................
def test_die_unless_func_python() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunctest.die_unless_func_python` function.
    '''

    # Defer heavyweight imports.
    from beartype._util.func.utilfunctest import die_unless_func_python
    from beartype.roar import _BeartypeUtilCallableException

    # Assert this validator accepts pure-Python callables.
    die_unless_func_python(lambda: True)

    # Assert this validator rejects C-based callables.
    with raises(_BeartypeUtilCallableException):
        die_unless_func_python(iter)


def test_is_func_python() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunctest.is_func_python` function.
    '''

    # Defer heavyweight imports.
    from beartype._util.func.utilfunctest import is_func_python
    from beartype.roar import _BeartypeUtilCallableException

    # Assert this tester accepts pure-Python callables.
    assert is_func_python(lambda: True) is True

    # Assert this tester rejects C-based callables.
    assert is_func_python(iter) is False
