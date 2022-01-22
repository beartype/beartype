#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator type hint-agnostic unit tests.**

This submodule unit tests high-level functionality of the
:func:`beartype.beartype` decorator independent of lower-level type hinting
concerns (e.g., PEP-compliance, PEP-noncompliance).
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ TESTS                             }....................
def test_decor_conf() -> None:
    '''
    Test coarse-grained configuration of the :func:`beartype.beartype`
    decorator by the optional ``conf`` keyword-only parameter.

    This test does *not* exercise fine-grained configuration (e.g., of
    individual type-checking strategies), which is delegated to more relevant
    tests elsewhere; rather, this test merely exercises that this decorator
    is configurable as expected from a high-level API perspective.
    '''

    # Defer heavyweight imports.
    from beartype import (
        BeartypeConf,
        BeartypeStrategy,
        beartype,
    )
    from beartype.roar import BeartypeDecorWrappeeException
    from pytest import raises

    # Assert that @beartype in configuration mode returns the default private
    # decorator when repeatedly invoked with the default configuration.
    assert (
        # Assert that the first @beartype call passed *NO* arguments internally
        # creates and returns the same default private decorator as...
        beartype() is
        # Another @beartype call passed *NO* arguments as well as...
        beartype() is
        # Another @beartype call passed the default configuration.
        beartype(conf=BeartypeConf())
    )

    # Assert that @beartype in configuration mode returns the same non-default
    # private decorator when repeatedly invoked with the same non-default
    # configuration.
    assert (
        beartype(conf=BeartypeConf(
            is_print_wrapper_code=True,
            strategy=BeartypeStrategy.On,
        )) is
        beartype(conf=BeartypeConf(
            is_print_wrapper_code=True,
            strategy=BeartypeStrategy.On,
        ))
    )

    # Assert that @beartype in configuration mode returns the identity
    # decorator unconditionally preserving all passed objects as is.
    beartype_O0 = beartype(conf=BeartypeConf(strategy=BeartypeStrategy.O0))
    assert beartype_O0(beartype) is beartype

    # Assert that @beartype raises the expected exception when passed a "conf"
    # parameter that is *NOT* a configuration.
    with raises(BeartypeDecorWrappeeException):
        beartype(conf='Within the daedal earth; lightning, and rain,')

# ....................{ TESTS ~ fail : wrappee            }....................
def test_decor_wrappee_type_fail() -> None:
    '''
    Test unsuccessful usage of the :func:`beartype.beartype` decorator for an
    **invalid wrappee** (i.e., object *not* decoratable by this decorator).
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from beartype.roar import BeartypeDecorWrappeeException
    from beartype_test.a00_unit.data.data_type import (
        CallableClass,
        Class,
    )

    # Assert that decorating an uncallable class raises the expected exception.
    with raises(BeartypeDecorWrappeeException):
        beartype(Class)

    # Assert that decorating a callable class raises the expected exception.
    with raises(BeartypeDecorWrappeeException):
        beartype(CallableClass)

    # Assert that decorating an uncallable object raises the expected
    # exception.
    with raises(BeartypeDecorWrappeeException):
        beartype(('Book of the Astronomican', 'Slaves to Darkness',))

    # Substring embedded in the messages of exceptions raised by @beartype when
    # passed uncallable descriptors created by builtin decorators.
    EXCEPTION_DESCRIPTOR_SUBSTR = 'descriptor'

    # Assert that decorating a property descriptor raises the expected
    # exception.
    with raises(BeartypeDecorWrappeeException) as exception_info:
        class WhereTheOldEarthquakeDaemon(object):
            @beartype
            @property
            def taught_her_young_ruin(self) -> str:
                return 'Ruin? Were these their toys? or did a sea'
    assert EXCEPTION_DESCRIPTOR_SUBSTR in exception_info.value.args[0]

    # Assert that decorating a class method descriptor raises the expected
    # exception.
    with raises(BeartypeDecorWrappeeException) as exception_info:
        class OrDidASeaOfFire(object):
            @beartype
            @classmethod
            def envelop_once_this_silent_snow(self) -> str:
                return 'None can reply—all seems eternal now.'
    assert EXCEPTION_DESCRIPTOR_SUBSTR in exception_info.value.args[0]

    # Assert that decorating a static method descriptor raises the expected
    # exception.
    assert EXCEPTION_DESCRIPTOR_SUBSTR in exception_info.value.args[0]
    with raises(BeartypeDecorWrappeeException) as exception_info:
        class TheWildernessHasAMysteriousTongue(object):
            @beartype
            @staticmethod
            def which_teaches_awful_doubt() -> str:
                return 'Which teaches awful doubt, or faith so mild,'
    # print(f'Ugh: {exception_info.value.args[0]}')
    assert EXCEPTION_DESCRIPTOR_SUBSTR in exception_info.value.args[0]

# ....................{ TESTS ~ fail : arg                }....................
def test_decor_arg_name_fail() -> None:
    '''
    Test unsuccessful usage of the :func:`beartype.beartype` decorator for
    callables accepting one or more **decorator-reserved parameters** (i.e.,
    parameters whose names are reserved for internal use by this decorator).
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from beartype.roar import BeartypeDecorParamNameException

    # Assert that decorating a callable accepting a reserved parameter name
    # raises the expected exception.
    with raises(BeartypeDecorParamNameException):
        @beartype
        def jokaero(weaponsmith: str, __beartype_func: str) -> str:
            return weaponsmith + __beartype_func

# ....................{ TESTS ~ fail : arg : call         }....................
def test_decor_arg_call_keyword_unknown_fail() -> None:
    '''
    Test unsuccessful usage of the :func:`beartype.beartype` decorator for
    wrapper functions passed unrecognized keyword parameters.
    '''

    # Defer heavyweight imports.
    from beartype import beartype

    # Decorated callable to be exercised.
    @beartype
    def tau(kroot: str, vespid: str) -> str:
        return kroot + vespid

    # Assert that calling this callable with an unrecognized keyword parameter
    # raises the expected exception.
    with raises(TypeError) as exception:
        tau(kroot='Greater Good', nicassar='Dhow')

    # Assert that this exception's message is that raised by the Python
    # interpreter on calling the decorated callable rather than that raised by
    # the wrapper function on type-checking that callable. This message is
    # currently stable across Python versions and thus robustly testable.
    assert str(exception.value).endswith(
        "tau() got an unexpected keyword argument 'nicassar'")
