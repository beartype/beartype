#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype utility fixed list pool unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.cache.list.utillistfixedpool` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import pytest

# ....................{ TESTS                             }....................
def test_fixedlist_pass() -> None:
    '''
    Test successful usage of the
    :mod:`beartype._util.cache.list.utillistfixedpool` class.
    '''

    # Defer heavyweight imports.
    from beartype._util.cache.list.utillistfixedpool import (
        acquire_fixed_list, release_fixed_list)

    # Acquire a fixed list of some length.
    moloch_solitude_filth = acquire_fixed_list(size=3)

    # Initialize this list.
    moloch_solitude_filth[:] = (
        'Moloch! Solitude! Filth! Ugliness! Ashcans and unobtainable dollars!',
        'Children screaming under the stairways! Boys sobbing in armies! Old',
        'men weeping in the parks!',
    )

    # Acquire another fixed list of the same length.
    moloch_whose = acquire_fixed_list(size=3)

    # Initialize this list.
    moloch_whose[:] = (
        'Moloch whose mind is pure machinery! Moloch whose blood is running',
        'money! Moloch whose fingers are ten armies! Moloch whose breast is a',
        'cannibal dynamo! Moloch whose ear is a smoking tomb!',
    )

    # Assert the contents of these lists to still be as expected.
    assert moloch_solitude_filth[0] == (
        'Moloch! Solitude! Filth! Ugliness! Ashcans and unobtainable dollars!')
    assert moloch_whose[-1] == (
        'cannibal dynamo! Moloch whose ear is a smoking tomb!')

    # Release these lists.
    release_fixed_list(moloch_solitude_filth)
    release_fixed_list(moloch_whose)


def test_fixedlist_fail() -> None:
    '''
    Test unsuccessful usage of the
    :mod:`beartype._util.cache.list.utillistfixedpool` class.
    '''

    # Defer heavyweight imports.
    from beartype._util.cache.list.utillistfixedpool import acquire_fixed_list
    from beartype.roar import _BeartypeFixedListException

    # Assert that fixed lists may only be acquired with positive integers.
    with pytest.raises(_BeartypeFixedListException):
        acquire_fixed_list((
            'Moloch the incomprehensible prison! Moloch the crossbone soulless',
            'jailhouse and Congress of sorrows! Moloch whose buildings are',
            'judgment! Moloch the vast stone of war! Moloch the stunned',
            'governments!',
        ))
    with pytest.raises(_BeartypeFixedListException):
        acquire_fixed_list(-67)
