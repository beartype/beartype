#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable tester utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.utilfunctest` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ descriptor                 }....................
def test_get_func_classmethod_wrappee() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncget.get_func_classmethod_wrappee`
    getter.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.utilfuncget import get_func_classmethod_wrappee
    from beartype_test.a00_unit.data.data_type import CALLABLES
    from pytest import raises

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

    # Assert this getter returns the expected wrappee when passed a class method
    # descriptor.
    #
    # Note that class method descriptors are *ONLY* directly accessible via the
    # low-level "object.__dict__" dictionary. When accessed as class or instance
    # attributes, class methods reduce to instances of the standard
    # "beartype.cave.MethodBoundInstanceOrClassType" type.
    class_method = TheLimitsOfTheDeadAndLivingWorld.__dict__[
        'of_insects_beasts_and_birds']
    class_method_wrappee = get_func_classmethod_wrappee(class_method)
    assert class_method_wrappee is never_to_be_reclaimed

    # Assert this getter raises the expected exception when passed an object
    # that is *NOT* a class method descriptor.
    for some_callable in CALLABLES:
        with raises(_BeartypeUtilCallableException):
            get_func_classmethod_wrappee(some_callable)


def test_get_func_staticmethod_wrappee() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncget.get_func_staticmethod_wrappee`
    getter.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.utilfuncget import get_func_staticmethod_wrappee
    from beartype_test.a00_unit.data.data_type import CALLABLES
    from pytest import raises

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

    # Assert this getter returns the expected wrappee when passed a static method
    # descriptor.
    #
    # Note that static method descriptors are *ONLY* directly accessible via the
    # low-level "object.__dict__" dictionary. When accessed as static or instance
    # attributes, static methods reduce to instances of the standard
    # "beartype.cave.MethodBoundInstanceOrClassType" type.
    static_method = TheirFoodAndTheirRetreatForEverGone.__dict__[
        'so_much_of_life_and_joy_is_lost']
    static_method_wrappee = get_func_staticmethod_wrappee(static_method)
    assert static_method_wrappee is becomes_its_spoil

    # Assert this getter raises the expected exception when passed an object
    # that is *NOT* a static method descriptor.
    for some_callable in CALLABLES:
        with raises(_BeartypeUtilCallableException):
            get_func_staticmethod_wrappee(some_callable)
