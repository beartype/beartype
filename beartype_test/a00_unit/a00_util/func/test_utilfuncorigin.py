#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype callable utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.func.utilfuncorigin` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ TESTS ~ label                     }....................
def test_get_callable_origin_label_pass_python() -> None:
    '''
    Test successful usage of the
    :func:`beartype._util.func.utilfuncorigin.get_callable_origin_label`
    function.
    '''

    # Defer test-specific imports.
    from beartype.roar import _BeartypeUtilCallableException
    from beartype._util.func.utilfuncorigin import get_callable_origin_label
    from beartype_test.a00_unit.data.data_type import (
        CALLABLES_C, CALLABLES_PYTHON, MODULE_FILENAME)

    # Assert this getter returns the expected label for pure-Python callables.
    for callable_python in CALLABLES_PYTHON:
        assert get_callable_origin_label(callable_python) == MODULE_FILENAME

    # Assert this getter returns the expected label for C-based callables.
    for callable_c in CALLABLES_C:
        assert get_callable_origin_label(callable_c) == '<C-based>'


def test_get_callable_origin_label_fail() -> None:
    '''
    Test unsuccessful usage of the
    :func:`beartype._util.func.utilfuncorigin.get_callable_origin_label`
    function.
    '''

    # Defer test-specific imports.
    from beartype.roar import _BeartypeUtilCallableException
    from beartype._util.func.utilfuncorigin import get_callable_origin_label
    from beartype_test.a00_unit.data.data_type import NON_CALLABLES

    # Assert this getter raises the expected exception for non-callables.
    for non_callable in NON_CALLABLES:
        with raises(_BeartypeUtilCallableException):
            get_callable_origin_label(non_callable)
