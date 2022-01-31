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
    from pytest import raises

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
    from pytest import raises

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
    from pytest import raises

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
