#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`3119`-compliant **class-specific utility function** unit
tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.cls.pep.utilpep3119` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_die_unless_type_isinstanceable() -> None:
    '''
    Test the
    :func:`beartype._util.cls.pep.utilpep3119.die_unless_type_isinstanceable`
    validator.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep3119Exception
    from beartype._util.cls.pep.utilpep3119 import (
        die_unless_type_isinstanceable)
    from beartype_test.a00_unit.data.data_type import (
        Class,
        NonIsinstanceableClass,
    )
    from pytest import raises

    # Assert this validator accepts an isinstanceable type.
    die_unless_type_isinstanceable(Class)

    # Assert this validator raises the expected exception when passed a
    # non-isinstanceable type.
    with raises(BeartypeDecorHintPep3119Exception):
        die_unless_type_isinstanceable(NonIsinstanceableClass)

    # Assert this validator raises the expected exception when passed a
    # non-type.
    with raises(BeartypeDecorHintPep3119Exception):
        die_unless_type_isinstanceable('Moab.')


def test_die_unless_type_issubclassable() -> None:
    '''
    Test the
    :func:`beartype._util.cls.pep.utilpep3119.die_unless_type_issubclassable`
    validator.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep3119Exception
    from beartype._util.cls.pep.utilpep3119 import (
        die_unless_type_issubclassable)
    from beartype_test.a00_unit.data.data_type import (
        Class,
        NonIssubclassableClass,
    )
    from pytest import raises

    # Assert this validator accepts an issubclassable type.
    die_unless_type_issubclassable(Class)

    # Assert this validator raises the expected exception when passed a
    # non-issubclassable type.
    with raises(BeartypeDecorHintPep3119Exception):
        die_unless_type_issubclassable(NonIssubclassableClass)

    # Assert this validator raises the expected exception when passed a
    # non-type.
    with raises(BeartypeDecorHintPep3119Exception):
        die_unless_type_issubclassable('Moab.')
