#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Callable wrapper utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.utilfuncwrap` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ all                        }....................
def test_unwrap_func_all() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncwrap.unwrap_func_all` function.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.func.utilfuncwrap import unwrap_func_all
    from functools import wraps

    # ....................{ CALLABLES                      }....................
    def in_a_station_of_the_metro_line_two():
        '''
        Arbitrary wrappee callable.
        '''

        return 'Petals on a wet, black bough.'


    @wraps(in_a_station_of_the_metro_line_two)
    def in_a_station_of_the_metro():
        '''
        Arbitrary wrapper callable.
        '''

        return (
            'THE apparition of these faces in the crowd;\n' +
            in_a_station_of_the_metro_line_two()
        )

    # ....................{ ASSERTS                        }....................
    # Assert this function returns unwrapped callables unmodified.
    assert unwrap_func_all(in_a_station_of_the_metro_line_two) is (
        in_a_station_of_the_metro_line_two)
    assert unwrap_func_all(iter) is iter

    # Assert this function returns wrapper callables unwrapped.
    assert unwrap_func_all(in_a_station_of_the_metro) is (
        in_a_station_of_the_metro_line_two)


def test_unwrap_func_all_isomorphic() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncwrap.unwrap_func_all_isomorphic` function.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.func.utilfuncwrap import unwrap_func_all_isomorphic
    from beartype_test.a00_unit.data.data_type import (
        function_wrappee,
        function_wrapper_nonisomarphic,
        function_wrapper_isomarphic,
        function_wrapper_isomarphic_args,
        function_wrapper_isomarphic_kwargs,
        object_callable_wrapper_isomorphic,
    )

    # ....................{ ASSERTS                        }....................
    # Assert this function returns unwrapped callables unmodified.
    assert unwrap_func_all_isomorphic(function_wrappee) is function_wrappee
    assert unwrap_func_all_isomorphic(iter) is iter

    # Assert this function returns non-isomorphic wrapper callables unmodified.
    assert unwrap_func_all_isomorphic(function_wrapper_nonisomarphic) is (
        function_wrapper_nonisomarphic)

    # Assert this function unwraps isomorphic wrapper callables.
    assert unwrap_func_all_isomorphic(function_wrapper_isomarphic) is (
        function_wrapper_nonisomarphic)
    assert unwrap_func_all_isomorphic(function_wrapper_isomarphic_args) is (
        function_wrapper_nonisomarphic)
    assert unwrap_func_all_isomorphic(function_wrapper_isomarphic_kwargs) is (
        function_wrapper_nonisomarphic)

    # Assert this function unwraps wrapper pseudo-callables.
    object_callable_wrapper_isomorphic_unwrapped = unwrap_func_all_isomorphic(
        func=object_callable_wrapper_isomorphic.__call__,
        wrapper=object_callable_wrapper_isomorphic,
    )
    assert object_callable_wrapper_isomorphic_unwrapped is (
        function_wrapper_nonisomarphic)

# ....................{ TESTS ~ descriptor                 }....................
def test_unwrap_func_class_or_static_method_once() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncwrap.unwrap_func_class_or_static_method_once`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableWrapperException
    from beartype._util.func.utilfuncwrap import (
        unwrap_func_class_or_static_method_once)
    from beartype_test.a00_unit.data.data_type import CALLABLES
    from pytest import raises

    # ....................{ CALLABLES                      }....................
    def never_to_be_reclaimed() -> str:
        '''
        Arbitrary pure-Python function.
        '''

        return 'The dwelling-place'


    def becomes_its_spoil() -> str:
        '''
        Arbitrary pure-Python function.
        '''

        return 'The dwelling-place'

    # ....................{ CLASSES                        }....................
    class TheLimitsOfTheDeadAndLivingWorld(object):
        '''
        Arbitrary pure-Python class defining a class method wrapping the
        pure-Python function defined above.
        '''

        of_insects_beasts_and_birds = classmethod(never_to_be_reclaimed)


    class TheirFoodAndTheirRetreatForEverGone(object):
        '''
        Arbitrary pure-Python static defining a static method wrapping the
        pure-Python function defined above.
        '''

        so_much_of_life_and_joy_is_lost = staticmethod(becomes_its_spoil)

    # ....................{ PASS                           }....................
    # Assert this getter returns the expected wrappee when passed a class method
    # descriptor.
    #
    # Note that class method descriptors are *ONLY* directly accessible via the
    # low-level "object.__dict__" dictionary. When accessed as class or instance
    # attributes, class methods reduce to instances of the standard
    # "beartype.cave.MethodBoundInstanceOrClassType" type.
    class_method = TheLimitsOfTheDeadAndLivingWorld.__dict__[
        'of_insects_beasts_and_birds']
    class_method_wrappee = unwrap_func_class_or_static_method_once(class_method)
    assert class_method_wrappee is never_to_be_reclaimed

    # Assert this getter returns the expected wrappee when passed a static
    # method descriptor.
    #
    # Note that static method descriptors are *ONLY* directly accessible via the
    # low-level "object.__dict__" dictionary. When accessed as static or
    # instance attributes, static methods reduce to instances of the standard
    # "beartype.cave.MethodBoundInstanceOrClassType" type.
    static_method = TheirFoodAndTheirRetreatForEverGone.__dict__[
        'so_much_of_life_and_joy_is_lost']
    static_method_wrappee = unwrap_func_class_or_static_method_once(
        static_method)
    assert static_method_wrappee is becomes_its_spoil

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed an object
    # that is *NOT* a static method descriptor.
    for some_callable in CALLABLES:
        with raises(_BeartypeUtilCallableWrapperException):
            unwrap_func_class_or_static_method_once(some_callable)


def test_unwrap_func_classmethod_once() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncwrap.unwrap_func_classmethod_once`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableWrapperException
    from beartype._util.func.utilfuncwrap import unwrap_func_classmethod_once
    from beartype_test.a00_unit.data.data_type import CALLABLES
    from pytest import raises

    # ....................{ LOCALS                         }....................
    def never_to_be_reclaimed() -> str:
        '''
        Arbitrary pure-Python function.
        '''

        return 'The dwelling-place'


    class TheLimitsOfTheDeadAndLivingWorld(object):
        '''
        Arbitrary pure-Python class defining a class method wrapping the
        pure-Python function defined above.
        '''

        of_insects_beasts_and_birds = classmethod(never_to_be_reclaimed)

    # ....................{ PASS                           }....................
    # Assert this getter returns the expected wrappee when passed a class method
    # descriptor.
    #
    # Note that class method descriptors are *ONLY* directly accessible via the
    # low-level "object.__dict__" dictionary. When accessed as class or instance
    # attributes, class methods reduce to instances of the standard
    # "beartype.cave.MethodBoundInstanceOrClassType" type.
    class_method = TheLimitsOfTheDeadAndLivingWorld.__dict__[
        'of_insects_beasts_and_birds']
    class_method_wrappee = unwrap_func_classmethod_once(class_method)
    assert class_method_wrappee is never_to_be_reclaimed

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed an object
    # that is *NOT* a class method descriptor.
    for some_callable in CALLABLES:
        with raises(_BeartypeUtilCallableWrapperException):
            unwrap_func_classmethod_once(some_callable)


def test_unwrap_func_staticmethod_once() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncwrap.unwrap_func_staticmethod_once`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableWrapperException
    from beartype._util.func.utilfuncwrap import unwrap_func_staticmethod_once
    from beartype_test.a00_unit.data.data_type import CALLABLES
    from pytest import raises

    # ....................{ LOCALS                         }....................
    def becomes_its_spoil() -> str:
        '''
        Arbitrary pure-Python function.
        '''

        return 'The dwelling-place'

    class TheirFoodAndTheirRetreatForEverGone(object):
        '''
        Arbitrary pure-Python static defining a static method wrapping the
        pure-Python function defined above.
        '''

        so_much_of_life_and_joy_is_lost = staticmethod(becomes_its_spoil)

    # ....................{ PASS                           }....................
    # Assert this getter returns the expected wrappee when passed a static method
    # descriptor.
    #
    # Note that static method descriptors are *ONLY* directly accessible via the
    # low-level "object.__dict__" dictionary. When accessed as static or instance
    # attributes, static methods reduce to instances of the standard
    # "beartype.cave.MethodBoundInstanceOrClassType" type.
    static_method = TheirFoodAndTheirRetreatForEverGone.__dict__[
        'so_much_of_life_and_joy_is_lost']
    static_method_wrappee = unwrap_func_staticmethod_once(static_method)
    assert static_method_wrappee is becomes_its_spoil

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed an object
    # that is *NOT* a static method descriptor.
    for some_callable in CALLABLES:
        with raises(_BeartypeUtilCallableWrapperException):
            unwrap_func_staticmethod_once(some_callable)
