#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`563` **unit tests.**

This submodule unit tests the public :func:`beartype.peps.resolve_pep563`
function, which internally leverages the :mod:`beartype.door` subpackage to
validate itself and is thus intentionally deferred to this DOOR-specific test
subpackage.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# .....................{ TESTS                             }....................
def test_resolve_pep563() -> None:
    '''
    Test the :func:`beartype.peps.resolve_pep563` resolver.
    '''

    # .....................{ IMPORTS                       }....................
    # Defer test-specific imports.
    from beartype.peps import resolve_pep563
    from beartype.roar import (
        BeartypeCallHintForwardRefException,
        BeartypeDecorHintForwardRefException,
        BeartypePep563Exception,
    )
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_MOST_3_13
    from beartype_test.a00_unit.data.pep.pep563.data_pep563_resolve import (
        ToAvariceOrPride,
        FrequentWith,
        their_starry_domes,
    )
    from pytest import raises

    # .....................{ LOCALS                        }....................
    # Arbitrary instance of the generic accepted by the function called below.
    numberless_and_immeasurable_halls = ToAvariceOrPride()

    # Arbitrary instance of the class defining various problematic methods
    # called below.
    and_thrones_radiant_with_chrysolite = FrequentWith()

    # .....................{ FAIL                          }....................
    # Assert that this function unsuccessfully raises the expected exception
    # *BEFORE* resolving all PEP 563-postponed type hints annotating these
    # callables.
    with raises(BeartypeDecorHintForwardRefException):
        their_starry_domes(numberless_and_immeasurable_halls)
    with raises(BeartypeDecorHintForwardRefException):
        and_thrones_radiant_with_chrysolite.until_the_doves(
            numberless_and_immeasurable_halls)
    with raises(BeartypeDecorHintForwardRefException):
        and_thrones_radiant_with_chrysolite.crystal_column(
            'Nor had that scene of ampler majesty')

    # .....................{ PASS                          }....................
    # Resolve all PEP 563-postponed type hints annotating these callables.
    resolve_pep563(their_starry_domes)
    resolve_pep563(FrequentWith.until_the_doves)
    resolve_pep563(FrequentWith.crystal_column)

    # Assert that this function successfully accepts and returns this instance.
    assert their_starry_domes(numberless_and_immeasurable_halls) is (
        numberless_and_immeasurable_halls)

    # Assert that this method successfully accepts and returns this string.
    assert FrequentWith.until_the_doves(numberless_and_immeasurable_halls) is (
        numberless_and_immeasurable_halls)

    # .....................{ FAIL ~ more                   }....................
    # Assert that this resolver raises the expected exception when passed an
    # uncallable object.
    with raises(BeartypePep563Exception):
        resolve_pep563('Mont Blanc yet gleams on high:—the power is there,')

    # Assert that this method unsuccessfully raises the excepted exception, due
    # to being annotated by a missing forward reference.
    with raises(BeartypeCallHintForwardRefException):
        and_thrones_radiant_with_chrysolite.crystal_column(
            'Than gems or gold, the varying roof of heaven')
