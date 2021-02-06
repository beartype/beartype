#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2021 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype class utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilcallable` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ TESTS                             }....................
def test_get_callable_fail() -> None:
    import sys
    from beartype._util.utilcallable import (
        get_callable_filename_or_placeholder)
            
    from beartype.roar import _BeartypeUtilCallableException
    
    # Copy/Paste from :mod:`types`
    def _function(): pass
    
    def _cell_factory():
        a = 1
        def f():
            nonlocal a
        return f.__closure__[0]
    
    def _generator():
        yield 1
        
    async def _coroutine(): pass
    _coroutine = _coroutine()
    _coroutine.close()  # Prevent ResourceWarning
    
    async def _async_generator():
        yield
    _async_generator = _async_generator()

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
    
def test_get_callable_filename() -> None:
    import pathlib
    import sys
    
    from beartype._util.utilcallable import get_callable_filename_or_placeholder
    from beartype.roar import _BeartypeUtilCallableException
    
    def _function():pass
    class _Class: 
        def _method(self): pass
    _test_module = pathlib

    no_err = [
                _function,      # Covers Lambda functions 
                _Class._method,
                _Class,
            ]

    # Confirm behaviour for function, method, and class Objects
    for case in no_err:
        assert (get_callable_filename_or_placeholder(case) ==
                str(pathlib.Path(__file__)))
    
    # Confirm behaviour when passed module method
    assert(get_callable_filename_or_placeholder(pathlib.Path) == 
            str(sys.modules.get(_test_module.__name__).__file__))

def test_get_callable_placeholder():
    import pathlib
    import sys

    from collections import namedtuple
    from beartype._util.utilcallable import get_callable_filename_or_placeholder
    
    Test = namedtuple('Test', ['case', 'result'])

    def _function():pass

    # Need to test for dynamically declared callable and class
    ret_placeholder = [
        Test(case = len, result = "<builtin>"),       # Built-in FunctionType 
        Test(case = [].append, result = "<builtin>"), # Built-in Method Type 
        Test(case = object.__init__, result = "<builtin>"),  # Wrapper Descriptor Type 
        Test(case = object().__str__, result = "<builtin>"), # Method Wrapper Type 
        Test(case = str.join, result = "<builtin>"),         # Method Descriptor Type 
        Test(case = dict.__dict__['fromkeys'], result = "<builtin>"), # Class Method Descriptor
        ]
    
    for test in ret_placeholder: 
        assert(get_callable_filename_or_placeholder(test.case) == test.result)
