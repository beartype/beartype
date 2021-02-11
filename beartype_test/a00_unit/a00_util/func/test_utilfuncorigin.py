#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2021 by Cecil Curry.
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
        Class, function, MODULE_FILENAME)

    # Tuple of all pure-Python callables to be tested.
    CALLABLES_PYTHON = (function, Class, Class.instance_method)

    # Tuple of all C-based callables.
    CALLABLES_C = (
        len,              # Built-in FunctionType
        [].append,        # Built-in Method Type
        object.__init__,  # Wrapper Descriptor Type
        object().__str__, # Method Wrapper Type
        str.join,         # Method Descriptor Type

        #FIXME: *UGH.* This probably should be callable under PyPy 3.6, but
        #it's not, which is why we've currently disabled this. That's clearly a
        #PyPy bug. Uncomment this *AFTER* we drop support for PyPy 3.6 (and any
        #newer PyPy versions also failing to implement this properly). We
        #should probably also consider filing an upstream issue with PyPy,
        #because this is non-ideal and non-orthogonal behaviour with CPython.
        #dict.__dict__['fromkeys'],
    )

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
    import sys
    from beartype.roar import _BeartypeUtilCallableException
    from beartype._util.func.utilfuncorigin import (
        get_callable_origin_label)
    from beartype_test.a00_unit.data.data_type import (
        async_generator,
        closure_cell_factory,
        coroutine,
        function,
        generator_factory,
    )

    try:
        raise TypeError
    except TypeError:
        traceback = sys.exc_info()[2]

    # Tuple of callable-like non-callable objects.
    NON_CALLABLES = (
        function.__code__, # CodeType
        type.__dict__,      # Mapping Proxy Type
        sys.implementation, # Simple Namespace Type
        async_generator,
        closure_cell_factory(),    # Cell Type
        coroutine,
        generator_factory(),
        traceback,
        traceback.tb_frame,
    )

    # Assert this getter raises the expected exception for non-callables.
    for non_callable in NON_CALLABLES:
        with raises(_BeartypeUtilCallableException):
            get_callable_origin_label(non_callable)
