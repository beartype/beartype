#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`3119`-compliant **class-specific utility function** unit
tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.cls.pep.utilpep3119` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ raiser : isinstanceable    }....................
def test_die_unless_object_isinstanceable() -> None:
    '''
    Test the
    :func:`beartype._util.cls.pep.utilpep3119.die_unless_object_isinstanceable`
    validator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep3119Exception
    from beartype._util.cls.pep.utilpep3119 import (
        die_unless_object_isinstanceable)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10
    from beartype_test.a00_unit.data.data_type import (
        Class,
        NonIsinstanceableClass,
    )
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this raiser accepts an isinstanceable type.
    die_unless_object_isinstanceable(Class)

    # Assert this raiser accepts a tuple of isinstanceable types.
    die_unless_object_isinstanceable((Class, str))

    # ....................{ FAIL                           }....................
    # Assert this raiser raises the expected exception when passed a
    # non-isinstanceable object.
    with raises(BeartypeDecorHintPep3119Exception):
        die_unless_object_isinstanceable('Moab.')

    # Assert this raiser raises the expected exception when passed a
    # non-isinstanceable type.
    with raises(BeartypeDecorHintPep3119Exception):
        die_unless_object_isinstanceable(NonIsinstanceableClass)

    # Assert this raiser raises the expected exception when passed a tuple of
    # one isinstanceable type and one non-isinstanceable type.
    with raises(BeartypeDecorHintPep3119Exception):
        die_unless_object_isinstanceable((Class, NonIsinstanceableClass))

    # ....................{ VERSION                        }....................
    # If the active Python interpreter targets Python >= 3.10 and thus supports
    # PEP 604-compliant new unions...
    if IS_PYTHON_AT_LEAST_3_10:
        # Assert this raiser accepts a new union of isinstanceable types.
        die_unless_object_isinstanceable(Class | str)

        # Assert this raiser raises the expected exception when passed a new
        # union of one isinstanceable type and one non-isinstanceable type.
        with raises(BeartypeDecorHintPep3119Exception):
            die_unless_object_isinstanceable(Class | NonIsinstanceableClass)


def test_die_unless_type_isinstanceable() -> None:
    '''
    Test the
    :func:`beartype._util.cls.pep.utilpep3119.die_unless_type_isinstanceable`
    validator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep3119Exception
    from beartype._util.cls.pep.utilpep3119 import (
        die_unless_type_isinstanceable)
    from beartype_test.a00_unit.data.data_type import (
        Class,
        NonIsinstanceableClass,
    )
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this validator accepts an isinstanceable type.
    die_unless_type_isinstanceable(Class)

    # ....................{ FAIL                           }....................
    # Assert this validator raises the expected exception when passed a
    # non-isinstanceable type.
    with raises(BeartypeDecorHintPep3119Exception):
        die_unless_type_isinstanceable(NonIsinstanceableClass)

    # Assert this validator raises the expected exception when passed a
    # non-type.
    with raises(BeartypeDecorHintPep3119Exception):
        die_unless_type_isinstanceable('Moab.')

# ....................{ TESTS ~ raiser : issubclassable    }....................
def test_die_unless_object_issubclassable() -> None:
    '''
    Test the
    :func:`beartype._util.cls.pep.utilpep3119.die_unless_object_issubclassable`
    validator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep3119Exception
    from beartype._util.cls.pep.utilpep3119 import (
        die_unless_object_issubclassable)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10
    from beartype_test.a00_unit.data.data_type import (
        Class,
        NonIssubclassableClass,
    )
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this raiser accepts an issubclassable type.
    die_unless_object_issubclassable(Class)

    # Assert this raiser accepts a tuple of issubclassable types.
    die_unless_object_issubclassable((Class, str))

    # ....................{ FAIL                           }....................
    # Assert this raiser raises the expected exception when passed a
    # non-issubclassable object.
    with raises(BeartypeDecorHintPep3119Exception):
        die_unless_object_issubclassable('Moab.')

    # Assert this raiser raises the expected exception when passed a
    # non-issubclassable type.
    with raises(BeartypeDecorHintPep3119Exception):
        die_unless_object_issubclassable(NonIssubclassableClass)

    # Assert this raiser raises the expected exception when passed a tuple of
    # one issubclassable type and one non-issubclassable type.
    with raises(BeartypeDecorHintPep3119Exception):
        die_unless_object_issubclassable((Class, NonIssubclassableClass))

    # ....................{ VERSION                        }....................
    # If the active Python interpreter targets Python >= 3.10 and thus supports
    # PEP 604-compliant new unions...
    if IS_PYTHON_AT_LEAST_3_10:
        # Assert this raiser accepts a new union of issubclassable types.
        die_unless_object_issubclassable(Class | str)

        # Assert this raiser raises the expected exception when passed a new
        # union of one issubclassable type and one non-issubclassable type.
        with raises(BeartypeDecorHintPep3119Exception):
            die_unless_object_issubclassable(Class | NonIssubclassableClass)


def test_die_unless_type_issubclassable() -> None:
    '''
    Test the
    :func:`beartype._util.cls.pep.utilpep3119.die_unless_type_issubclassable`
    validator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep3119Exception
    from beartype._util.cls.pep.utilpep3119 import (
        die_unless_type_issubclassable)
    from beartype_test.a00_unit.data.data_type import (
        Class,
        NonIssubclassableClass,
    )
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert this validator accepts an issubclassable type.
    die_unless_type_issubclassable(Class)

    # ....................{ FAIL                           }....................
    # Assert this validator raises the expected exception when passed a
    # non-issubclassable type.
    with raises(BeartypeDecorHintPep3119Exception):
        die_unless_type_issubclassable(NonIssubclassableClass)

    # Assert this validator raises the expected exception when passed a
    # non-type.
    with raises(BeartypeDecorHintPep3119Exception):
        die_unless_type_issubclassable('Moab.')
