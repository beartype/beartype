#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`563` unit tests.

This submodule unit tests the public :func:`beartype.peps.resolve_pep563`
function.
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
        BeartypePep563Exception,
    )
    from beartype_test.a00_unit.data.pep.pep563.data_pep563_resolve import (
        ToAvariceOrPride,
        their_starry_domes,
    )
    from pytest import raises

    # .....................{ LOCALS                        }....................
    # Arbitrary instance of the generic accepted by the function called below.
    numberless_and_immeasurable_halls = ToAvariceOrPride()

    # .....................{ PASS                          }....................
    # Assert that this function unsuccessfully raises the expected exception
    # *BEFORE* resolving all PEP 563-postponed type hints annotating this
    # function.
    with raises(BeartypeCallHintForwardRefException):
        their_starry_domes(numberless_and_immeasurable_halls)

    # Resolve all PEP 563-postponed type hints annotating this function.
    resolve_pep563(their_starry_domes)

    # Assert that this function successfully accepts and returns this instance.
    assert their_starry_domes(numberless_and_immeasurable_halls) is (
        numberless_and_immeasurable_halls)

    # .....................{ FAIL                          }....................
    # Assert that this resolver raises the expected exception when passed an
    # uncallable object.
    with raises(BeartypePep563Exception):
        resolve_pep563('Mont Blanc yet gleams on high:—the power is there,')
