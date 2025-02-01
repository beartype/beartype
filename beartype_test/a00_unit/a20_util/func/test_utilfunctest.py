#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable tester utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.utilfunctest` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
# Note that the related test_is_func_nested() unit test is intentionally defined
# in the companion "test_utilfuncscope" submodule rather than this submodule.
# Why? Convenience, mostly. That submodule defines various callables of interest
# that dramatically simplify the implementation of that unit test.

def test_is_func_lambda() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunctest.is_func_lambda` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.func.utilfunctest import is_func_lambda

    def intimations_of_immortality(): 'from Recollections of Early Childhood'

    # Assert this tester accepts pure-Python lambda functions.
    assert is_func_lambda(lambda: True) is True

    # Assert this tester rejects pure-Python non-lambda callables.
    assert is_func_lambda(intimations_of_immortality) is False

    # Assert this tester rejects C-based callables.
    assert is_func_lambda(iter) is False

# ....................{ TESTS ~ async                      }....................
def test_is_func_async() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunctest.is_func_async` tester.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.utilfunctest import is_func_async
    from beartype_test.a00_unit.data.data_type import (
        async_generator,
        async_generator_factory,
        async_coroutine,
        async_coroutine_factory,
        sync_generator,
        sync_generator_factory,
        function,
    )

    # Assert this tester accepts pure-Python coroutine callables.
    assert is_func_async(async_coroutine_factory) is True

    # Assert this tester rejects pure-Python coroutine objects.
    assert is_func_async(async_coroutine) is False

    # Assert this tester accepts pure-Python asynchronous generator callables.
    assert is_func_async(async_generator_factory) is True

    # Assert this tester rejects pure-Python asynchronous generator objects.
    assert is_func_async(async_generator) is False

    # Assert this tester rejects pure-Python synchronous generator callables.
    assert is_func_async(sync_generator_factory) is False

    # Assert this tester rejects pure-Python synchronous generator objects.
    assert is_func_async(sync_generator) is False

    # Assert this tester rejects pure-Python non-asynchronous callables.
    assert is_func_async(function) is False

    # Assert this tester rejects arbitrary non-asynchronous objects.
    assert is_func_async('To hear—an old and solemn harmony;') is False


def test_is_func_coro() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunctest.is_func_coro` function.
    '''

    # Defer test-specific imports.
    from beartype._util.func.utilfunctest import is_func_coro
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype_test.a00_unit.data.data_type import (
        async_generator,
        async_generator_factory,
        async_coroutine,
        async_coroutine_factory,
        function,
    )

    # Assert this tester accepts pure-Python coroutine callables.
    assert is_func_coro(async_coroutine_factory) is True

    # Assert this tester rejects pure-Python coroutine objects.
    assert is_func_coro(async_coroutine) is False

    # Assert this tester rejects pure-Python asynchronous generator callables.
    assert is_func_coro(async_generator_factory) is False

    # Assert this tester rejects pure-Python asynchronous generator objects.
    assert is_func_coro(async_generator) is False

    # Assert this tester rejects pure-Python non-asynchronous callables.
    assert is_func_coro(function) is False

    # Assert this tester rejects arbitrary non-asynchronous objects.
    assert is_func_coro('To hear—an old and solemn harmony;') is (
        False)


def test_is_func_async_generator() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunctest.is_func_async_generator` function.
    '''

    # Defer test-specific imports.
    from beartype._util.func.utilfunctest import is_func_async_generator
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype_test.a00_unit.data.data_type import (
        async_coroutine,
        async_coroutine_factory,
        async_generator,
        async_generator_factory,
        sync_generator,
        sync_generator_factory,
        function,
    )

    # Assert this tester accepts pure-Python asynchronous generator callables.
    assert is_func_async_generator(async_generator_factory) is True

    # Assert this tester rejects pure-Python asynchronous generator objects.
    assert is_func_async_generator(async_generator) is False

    # Assert this tester rejects pure-Python coroutine callables.
    assert is_func_async_generator(async_coroutine_factory) is False

    # Assert this tester rejects pure-Python coroutine objects.
    assert is_func_async_generator(async_coroutine) is False

    # Assert this tester rejects pure-Python synchronous generator callables.
    assert is_func_async_generator(sync_generator_factory) is False

    # Assert this tester rejects pure-Python synchronous generator objects.
    assert is_func_async_generator(sync_generator) is False

    # Assert this tester rejects pure-Python non-asynchronous callables.
    assert is_func_async_generator(function) is False

    # Assert this tester rejects arbitrary non-asynchronous objects.
    assert is_func_async_generator('To hear—an old and solemn harmony;') is (
        False)

# ....................{ TESTS ~ sync                       }....................
def test_is_func_sync_generator() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunctest.is_func_sync_generator` function.
    '''

    # Defer test-specific imports.
    from beartype._util.func.utilfunctest import is_func_sync_generator
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype_test.a00_unit.data.data_type import (
        async_coroutine,
        async_coroutine_factory,
        async_generator,
        async_generator_factory,
        sync_generator,
        sync_generator_factory,
        function,
    )

    # Assert this tester rejects pure-Python asynchronous generator callables.
    assert is_func_sync_generator(async_generator_factory) is False

    # Assert this tester rejects pure-Python asynchronous generator objects.
    assert is_func_sync_generator(async_generator) is False

    # Assert this tester rejects pure-Python coroutine callables.
    assert is_func_sync_generator(async_coroutine_factory) is False

    # Assert this tester rejects pure-Python coroutine objects.
    assert is_func_sync_generator(async_coroutine) is False

    # Assert this tester accepts pure-Python synchronous generator callables.
    assert is_func_sync_generator(sync_generator_factory) is True

    # Assert this tester accepts pure-Python synchronous generator objects.
    assert is_func_sync_generator(sync_generator) is False

    # Assert this tester rejects pure-Python non-asynchronous callables.
    assert is_func_sync_generator(function) is False

    # Assert this tester rejects arbitrary non-asynchronous objects.
    assert is_func_sync_generator('To hear—an old and solemn harmony;') is (
        False)

# ....................{ TESTS ~ descriptor : classmethod   }....................
def test_die_unless_func_classmethod() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunctest.die_unless_func_classmethod`
    validator.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.utilfunctest import die_unless_func_classmethod
    from beartype_test.a00_unit.data.data_type import (
        CALLABLES,
        Class,
    )
    from pytest import raises

    # Assert this validator accepts a class method descriptor.
    #
    # Note that class method descriptors are *ONLY* directly accessible via the
    # low-level "object.__dict__" dictionary. When accessed as class or instance
    # attributes, class methods reduce to instances of the standard
    # "beartype.cave.MethodBoundInstanceOrClassType" type.
    die_unless_func_classmethod(Class.__dict__['class_method'])

    # Assert this validator rejects *ALL* other callables.
    for some_callable in CALLABLES:
        with raises(_BeartypeUtilCallableException):
            die_unless_func_classmethod(some_callable)


def test_is_func_classmethod() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunctest.is_func_classmethod` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.func.utilfunctest import is_func_classmethod
    from beartype_test.a00_unit.data.data_type import (
        CALLABLES,
        Class,
    )

    # Assert this tester accepts a class method descriptor.
    #
    # Note that class method descriptors are *ONLY* directly accessible via the
    # low-level "object.__dict__" dictionary. When accessed as class or instance
    # attributes, class methods reduce to instances of the standard
    # "beartype.cave.MethodBoundInstanceOrClassType" type.
    assert is_func_classmethod(Class.__dict__['class_method']) is True

    # Assert this tester rejects *ALL* other callables.
    for some_callable in CALLABLES:
        assert is_func_classmethod(some_callable) is False

# ....................{ TESTS ~ descriptor : property      }....................
def test_die_unless_func_property() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunctest.die_unless_func_property`
    validator.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.utilfunctest import die_unless_func_property
    from beartype_test.a00_unit.data.data_type import (
        CALLABLES,
        Class,
    )
    from pytest import raises

    # Assert this validator accepts a property descriptor.
    #
    # Note that property descriptors are directly accessible both as class
    # attributes *AND* via the low-level "object.__dict__" dictionary. Property
    # objects are *NOT* accessible as instance attributes, for obvious reasons.
    die_unless_func_property(Class.instance_property)

    # Assert this validator rejects *ALL* other callables.
    for some_callable in CALLABLES:
        with raises(_BeartypeUtilCallableException):
            die_unless_func_property(some_callable)


def test_is_func_property() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunctest.is_func_property` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.func.utilfunctest import is_func_property
    from beartype_test.a00_unit.data.data_type import (
        CALLABLES,
        Class,
    )

    # Assert this tester accepts a property descriptor.
    #
    # Note that property descriptors are directly accessible both as class
    # attributes *AND* via the low-level "object.__dict__" dictionary. Property
    # objects are *NOT* accessible as instance attributes, for obvious reasons.
    assert is_func_property(Class.instance_property) is True

    # Assert this tester rejects *ALL* other callables.
    for some_callable in CALLABLES:
        assert is_func_property(some_callable) is False

# ....................{ TESTS ~ descriptor : staticmethod  }....................
def test_die_unless_func_staticmethod() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunctest.die_unless_func_staticmethod`
    validator.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.utilfunctest import die_unless_func_staticmethod
    from beartype_test.a00_unit.data.data_type import (
        CALLABLES,
        Class,
    )
    from pytest import raises

    # Assert this validator accepts a static method descriptor.
    #
    # Note that static method descriptors are *ONLY* directly accessible via the
    # low-level "object.__dict__" dictionary. When accessed as class or instance
    # attributes, static methods reduce to instances of the standard
    # "beartype.cave.FunctionType" type.
    die_unless_func_staticmethod(Class.__dict__['static_method'])

    # Assert this validator rejects *ALL* other callables.
    for some_callable in CALLABLES:
        with raises(_BeartypeUtilCallableException):
            die_unless_func_staticmethod(some_callable)


def test_is_func_staticmethod() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunctest.is_func_staticmethod` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.func.utilfunctest import is_func_staticmethod
    from beartype_test.a00_unit.data.data_type import (
        CALLABLES,
        Class,
    )

    # Assert this tester accepts a static method descriptor.
    #
    # Note that static method descriptors are *ONLY* directly accessible via the
    # low-level "object.__dict__" dictionary. When accessed as class or instance
    # attributes, static methods reduce to instances of the standard
    # "beartype.cave.FunctionType" type.
    assert is_func_staticmethod(Class.__dict__['static_method']) is True

    # Assert this tester rejects *ALL* other callables.
    for some_callable in CALLABLES:
        assert is_func_staticmethod(some_callable) is False

# ....................{ TESTS ~ python                     }....................
def test_die_unless_func_python() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunctest.die_unless_func_python` tester.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.utilfunctest import die_unless_func_python
    from beartype_test.a00_unit.data.data_type import CALLABLES_C
    from pytest import raises

    # Assert this validator accepts pure-Python callables.
    die_unless_func_python(lambda: True)

    # Assert this validator rejects *ALL* C-based callables.
    for callable_c in CALLABLES_C:
        with raises(_BeartypeUtilCallableException):
            die_unless_func_python(callable_c)


def test_is_func_codeobjable() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunctest.is_func_codeobjable` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.func.utilfunctest import is_func_codeobjable

    # Assert this tester accepts pure-Python callables.
    assert is_func_codeobjable(lambda: True) is True

    # Assert this tester rejects C-based callables.
    assert is_func_codeobjable(iter) is False

# ....................{ TESTS ~ nested : closure           }....................
def test_is_func_closure() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunctest.is_func_closure` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.func.utilfunctest import is_func_closure
    from beartype_test.a00_unit.data.data_type import (
        closure_factory,
        function,
    )

    # Assert this tester accepts closures.
    assert is_func_closure(closure_factory()) is True

    # Assert this tester rejects non-closure callables.
    assert is_func_closure(function) is False

# ....................{ TESTS ~ nested : wrapper           }....................
def test_is_func_wrapper() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunctest.is_func_wrapper` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.func.utilfunctest import is_func_wrapper
    from beartype_test.a00_unit.data.data_type import (
        decorator_isomorphic,
        function,
    )

    # Assert this tester accepts wrappers generated by standard decorators.
    assert is_func_wrapper(decorator_isomorphic(function)) is True

    # Assert this tester rejects non-wrapper callables.
    assert is_func_wrapper(function) is False

    # Assert this tester rejects non-wrapper non-callables.
    assert is_func_wrapper(
        'Of mouldering leaves in the waste wilderness:—') is False


def test_is_func_wrapper_isomorphic() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfunctest.is_func_wrapper_isomorphic` tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.func.utilfunctest import is_func_wrapper_isomorphic
    from beartype_test.a00_unit.data.data_type import (
        context_manager_factory,
        decorator_isomorphic,
        decorator_nonisomorphic,
        function,
        object_callable_wrapper_isomorphic,
        wrapper_isomorphic,
    )

    # ....................{ PASS                           }....................
    # Assert this tester accepts isomorphic wrapper closures.
    assert is_func_wrapper_isomorphic(context_manager_factory) is True
    assert is_func_wrapper_isomorphic(decorator_isomorphic(function)) is True

    # Assert this tester accepts isomorphic wrapper functions.
    assert is_func_wrapper_isomorphic(wrapper_isomorphic) is True

    # Assert this tester accepts isomorphic wrapper bound methods explicitly
    # decorated as such.
    assert is_func_wrapper_isomorphic(
        object_callable_wrapper_isomorphic.method_wrapper_isomorphic) is True

    # Assert this tester accepts isomorphic wrapper bound methods *NOT*
    # explicitly decorated as such when a sibling wrapper is also passed.
    assert is_func_wrapper_isomorphic(
        object_callable_wrapper_isomorphic.method_wrapper_isomorphic_implicit,
        object_callable_wrapper_isomorphic.method_wrapper_isomorphic,
    ) is True

    # Assert this tester rejects non-isomorphic wrappers.
    assert is_func_wrapper_isomorphic(
        decorator_nonisomorphic(function)) is False

    # Assert this tester rejects non-wrapper callables.
    assert is_func_wrapper_isomorphic(function) is False
