#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2021 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype callable utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.func.utilfunc` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.mark.pytskip import skip_if_pypy
from pytest import raises

# ....................{ DATA                              }....................
#FIXME: Shift into a new "beartype_test.a00_unit.data.data_type" submodule for
#general-purpose reuse throughout unit tests.

def _function():
    '''
    Arbitrary function.
    '''

    pass


class _Class:
    '''
    Arbitrary class defining an arbitrary method.
    '''

    def _method(self):
        '''Arbitrary method.'''

        pass


def _cell_factory():
    '''
    Arbitrary closure factory function.
    '''

    a = 1
    def f():
        nonlocal a
    return f.__closure__[0]

def _generator():
    '''
    Arbitrary generator factory function.
    '''

    yield 1


async def _coroutine():
    '''
    Arbitrary coroutine factory function.
    '''

    pass

_coroutine = _coroutine()
_coroutine.close()  # Prevent ResourceWarning


async def _async_generator():
    '''
    Arbitrary asynchronous generator factory function.
    '''

    yield

_async_generator = _async_generator()

# ....................{ TESTS ~ filename                  }....................
def test_get_callable_filename_or_placeholder_pass_filename() -> None:
    '''
    Test successful usage of the
    :func:`beartype._util.func.utilfunc.get_callable_filename_or_placeholder`
    function returning absolute filenames.
    '''

    # Defer test-specific imports.
    import pathlib
    from beartype.roar import _BeartypeUtilCallableException
    from beartype._util.func.utilfunc import (
        get_callable_filename_or_placeholder)
    from beartype._util.py.utilpyinterpreter import IS_PYPY

    # Tuple of all pure-Python callables to be tested.
    CALLABLES_PYTHON = (_function, _Class._method)

    # Assert for pure-Python callables...
    for callable_python in CALLABLES_PYTHON:
        assert get_callable_filename_or_placeholder(callable_python) == (
            # If the current interpreter is PyPy, that PyPy internally reduced
            # this pure-Python callable to a C-based callable;
            '<C-based>' if IS_PYPY else
            # Else, that CPython preserved this pure-Python callable as is.
            str(pathlib.Path(__file__))
        )

    # Assert this function returns the expected filename for a class.
    assert get_callable_filename_or_placeholder(_Class) == str(
        pathlib.Path(__file__))

    # Assert this function returns the expected filename for a module function.
    assert get_callable_filename_or_placeholder(pathlib.Path) == (
        pathlib.__file__)


def test_get_callable_filename_or_placeholder_pass_placeholder() -> None:
    '''
    Test successful usage of the
    :func:`beartype._util.func.utilfunc.get_callable_filename_or_placeholder`
    function returning placeholder strings.
    '''

    # Defer test-specific imports.
    from collections import namedtuple
    from beartype._util.func.utilfunc import (
        get_callable_filename_or_placeholder)

    #FIXME: Nice! Let's globalize this into the module namespace and then reuse
    #this approach in the
    #test_get_callable_filename_or_placeholder_pass_filename() test as well,
    #where it should simplify things nicely.
    Test = namedtuple('Test', ['case', 'result'])

    # Need to test for dynamically declared callable and class.
    ret_placeholder = [
        Test(case=len, result = "<C-based>"),       # Built-in FunctionType
        Test(case=[].append, result = "<C-based>"), # Built-in Method Type
        Test(case=object.__init__, result = "<C-based>"),  # Wrapper Descriptor Type
        Test(case=object().__str__, result = "<C-based>"), # Method Wrapper Type
        Test(case=str.join, result = "<C-based>"),         # Method Descriptor Type

        #FIXME: *UGH.* This probably should be callable under PyPy 3.6, but
        #it's not, which is why we've currently disabled this. That's clearly a
        #PyPy bug. Uncomment this *AFTER* we drop support for PyPy 3.6 (and any
        #newer PyPy versions also failing to implement this properly). We
        #should probably also consider filing an upstream issue with PyPy,
        #because this is non-ideal and non-orthogonal behaviour with CPython.
        # Test(case=dict.__dict__['fromkeys'], result = "<C-based>"), # Class Method Descriptor
    ]

    for test in ret_placeholder:
        assert(get_callable_filename_or_placeholder(test.case) == test.result)


def test_get_callable_filename_or_placeholder_fail() -> None:
    '''
    Test unsuccessful usage of the
    :func:`beartype._util.func.utilfunc.get_callable_filename_or_placeholder`
    function.
    '''

    # Defer test-specific imports.
    import sys
    from beartype.roar import _BeartypeUtilCallableException
    from beartype._util.func.utilfunc import (
        get_callable_filename_or_placeholder)

    try:
        raise TypeError
    except TypeError:
        _trace_back = sys.exc_info()[2]

    throw_err = [
        _function.__code__, # CodeType
        type.__dict__,      # Mapping Proxy Type
        sys.implementation, # Simple Namespace Type
        _cell_factory(),    # Cell Type
        _generator(),
        _coroutine,
        _async_generator,
        _trace_back,
        _trace_back.tb_frame,
    ]

    for case in throw_err:
        with raises(_BeartypeUtilCallableException):
            get_callable_filename_or_placeholder(case)
