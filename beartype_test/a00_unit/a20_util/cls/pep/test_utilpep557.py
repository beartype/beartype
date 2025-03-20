#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`557`-compliant **class-specific utility function** unit
tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.cls.pep.clspep557` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_die_unless_type_pep557_dataclass() -> None:
    '''
    Test the
    :func:`beartype._util.cls.pep.clspep557.die_unless_type_pep557_dataclass`
    raiser.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep557Exception
    from beartype.roar._roarexc import _BeartypeUtilTypeException
    from beartype._util.cls.pep.clspep557 import (
        die_unless_type_pep557_dataclass)
    from dataclasses import dataclass
    from pytest import raises

    # ....................{ CLASSES                        }....................
    @dataclass
    class SpacesOfFireAndAllTheYawnOfHell(object):
        '''
        Arbitrary dataclass.
        '''

        pass

    # ....................{ PASS                           }....................
    # Implicitly assert that this raiser raises *NO* exception when passed a
    # dataclass type.
    die_unless_type_pep557_dataclass(SpacesOfFireAndAllTheYawnOfHell) is True

    # ....................{ FAIL                           }....................
    # Assert that this raiser raises the expected exception when passed a
    # non-dataclass type.
    with raises(BeartypeDecorHintPep557Exception):
        die_unless_type_pep557_dataclass(int)

    # Assert that this raiser raises the expected exception when passed a
    # non-type.
    with raises(_BeartypeUtilTypeException):
        die_unless_type_pep557_dataclass(
            'Spaces of fire, and all the yawn of hell.—')


def test_is_type_pep557_dataclass() -> None:
    '''
    Test the
    :func:`beartype._util.cls.pep.clspep557.is_type_pep557_dataclass` tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilTypeException
    from beartype._util.cls.pep.clspep557 import is_type_pep557_dataclass
    from dataclasses import dataclass
    from pytest import raises

    # ....................{ CLASSES                        }....................
    @dataclass
    class WhichTeachesAwfulDoubtOrFaithSoMild(object):
        '''
        Arbitrary dataclass.
        '''

        pass

    # ....................{ PASS                           }....................
    # Assert that this tester returns true when passed a dataclass type.
    assert is_type_pep557_dataclass(WhichTeachesAwfulDoubtOrFaithSoMild) is True

    # Assert that this tester returns false when passed a non-dataclass type.
    assert is_type_pep557_dataclass(str) is False

    # ....................{ FAIL                           }....................
    # Assert that this tester raises the expected exception when passed a
    # non-type.
    with raises(_BeartypeUtilTypeException):
        is_type_pep557_dataclass('The wilderness has a mysterious tongue')
