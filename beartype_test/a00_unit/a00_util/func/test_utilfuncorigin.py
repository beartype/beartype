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

# ....................{ TESTS ~ code                      }....................
def test_get_func_origin_code_or_none() -> None:
    '''
    Test usage of the
    :func:`beartype._util.func.utilfuncorigin.get_func_origin_code_or_none`
    function.
    '''

    # Defer test-specific imports.
    from beartype.roar import _BeartypeUtilCallableException
    from beartype._util.func.utilfuncmake import make_func
    from beartype._util.func.utilfuncorigin import get_func_origin_code_or_none

    # Arbitrary lambda function physically declared by this submodule.
    thou_dirge = lambda: 'Of the dying year, to which this closing night'

    # Arbitrary non-lambda function physically declared by this submodule.
    def will_be_the_dome():
        return 'of a vast sepulchre'

    # Arbitrary callable dynamically declared in-memory.
    of_vapours = make_func(
        func_name='vaulted_with_all_thy_congregated_might',
        func_code='''
def vaulted_with_all_thy_congregated_might():
    return 'Of vapours, from whose solid atmosphere'
''')

    # Assert this getter returns a string containing a substring contained in
    # the body of that lambda function when passed that function.
    thou_dirge_code = get_func_origin_code_or_none(thou_dirge)
    assert isinstance(thou_dirge_code, str)
    assert "'Of the dying year, " in thou_dirge_code

    # Assert this getter returns a string containing a substring contained in
    # the body of a non-lambda function when passed that function.
    will_be_the_dome_code = get_func_origin_code_or_none(will_be_the_dome)
    assert isinstance(will_be_the_dome_code, str)
    assert "'of a vast sepulchre'" in will_be_the_dome_code

    # Assert this getter returns "None" when passed a dynamically declared
    # callable.
    assert get_func_origin_code_or_none(of_vapours) is None

# ....................{ TESTS ~ label                     }....................
def test_get_func_origin_label() -> None:
    '''
    Test usage of the
    :func:`beartype._util.func.utilfuncorigin.get_func_origin_label`
    function.
    '''

    # Defer test-specific imports.
    from beartype.roar import _BeartypeUtilCallableException
    from beartype._util.func.utilfuncorigin import get_func_origin_label
    from beartype_test.a00_unit.data.data_type import (
        CALLABLES_C,
        CALLABLES_PYTHON,
        MODULE_FILENAME,
        NON_CALLABLES,
    )

    # Assert this getter returns the expected label for pure-Python callables.
    for callable_python in CALLABLES_PYTHON:
        assert get_func_origin_label(callable_python) == MODULE_FILENAME

    # Assert this getter returns the expected label for C-based callables.
    for callable_c in CALLABLES_C:
        assert get_func_origin_label(callable_c) == '<C-based>'

    # Assert this getter raises the expected exception for non-callables.
    for non_callable in NON_CALLABLES:
        with raises(_BeartypeUtilCallableException):
            get_func_origin_label(non_callable)
