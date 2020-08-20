#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype utility fixed list pool unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.cache.pool.utilcachepoollistfixed` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ TESTS ~ pool                      }....................
def test_listfixed_pool_pass() -> None:
    '''
    Test successful usage of the
    :mod:`beartype._util.cache.pool.utilcachepoollistfixed` submodule.
    '''

    # Defer heavyweight imports.
    from beartype._util.cache.pool.utilcachepoollistfixed import (
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


def test_listfixed_pool_fail() -> None:
    '''
    Test unsuccessful usage of the
    :mod:`beartype._util.cache.pool.utilcachepoollistfixed` submodule.
    '''

    # Defer heavyweight imports.
    from beartype._util.cache.pool.utilcachepoollistfixed import (
        acquire_fixed_list)
    from beartype.roar import _BeartypeUtilCachedFixedListException

    # Assert that fixed lists may only be acquired with positive integers.
    with raises(_BeartypeUtilCachedFixedListException):
        acquire_fixed_list((
            'Moloch the incomprehensible prison! Moloch the crossbone soulless',
            'jailhouse and Congress of sorrows! Moloch whose buildings are',
            'judgment! Moloch the vast stone of war! Moloch the stunned',
            'governments!',
        ))
    with raises(_BeartypeUtilCachedFixedListException):
        acquire_fixed_list(-67)

# ....................{ TESTS ~ type                      }....................
def test_listfixed_type_pass() -> None:
    '''
    Test successful usage of the
    :mod:`beartype._util.cache.pool.utilcachepoollistfixed.FixedList` type.
    '''

    # Defer heavyweight imports.
    from beartype._util.cache.pool.utilcachepoollistfixed import FixedList

    # Fixed list to be tested.
    fixed_list = FixedList(size=11)

    # Assert this list to be of the expected size.
    assert len(fixed_list) == 11

    # Assert that list slicing to an iterable of the same length succeeds.
    fixed_list[:] = (
        'Love the quick profit, the annual raise,',
        'vacation with pay. Want more',
        'of everything ready-made. Be afraid',
        'to know your neighbors and to die.',
        'And you will have a window in your head.',
        'Not even your future will be a mystery',
        'any more. Your mind will be punched in a card',
        'and shut away in a little drawer.',
        'When they want you to buy something',
        'they will call you. When they want you',
        'to die for profit they will let you know.',
    )
    assert fixed_list[ 0] == 'Love the quick profit, the annual raise,'
    assert fixed_list[10] == 'to die for profit they will let you know.'

    # Assert that list copying succeeds.
    fixed_list_copy = fixed_list.copy()
    assert isinstance(fixed_list_copy, FixedList)
    assert fixed_list_copy == fixed_list


def test_listfixed_type_fail() -> None:
    '''
    Test unsuccessful usage of the
    :mod:`beartype._util.cache.pool.utilcachepoollistfixed.FixedList` type.
    '''

    # Defer heavyweight imports.
    from beartype._util.cache.pool.utilcachepoollistfixed import FixedList
    from beartype.roar import _BeartypeUtilCachedFixedListException

    # Fixed list to be tested.
    fixed_list = FixedList(size=8)
    fixed_list[:] = (
        'Ask the questions that have no answers.',
        'Invest in the millennium. Plant sequoias.',
        'Say that your main crop is the forest',
        'that you did not plant,',
        'that you will not live to harvest.',
        'Say that the leaves are harvested',
        'when they have rotted into the mold.',
        'Call that profit. Prophesy such returns.',
    )

    # Assert that fixed lists refuse to support item deletion.
    with raises(_BeartypeUtilCachedFixedListException):
        del fixed_list[0]

    # Assert that fixed lists refuse to support in-place addition.
    with raises(_BeartypeUtilCachedFixedListException):
        fixed_list += (
            'Put your faith in the two inches of humus',
            'that will build under the trees',
            'every thousand years.',
            'Listen to carrion – put your ear',
            'close, and hear the faint chattering',
            'of the songs that are to come.',
            'Expect the end of the world. Laugh.',
            'Laughter is immeasurable. Be joyful',
            'though you have considered all the facts.',
        )

    # Assert that fixed lists refuse to support in-place multiplication.
    with raises(_BeartypeUtilCachedFixedListException):
        fixed_list *= 0xDEADBEEF

    # Assert that fixed lists refuse to support slicing to an iterable of
    # differing length.
    with raises(_BeartypeUtilCachedFixedListException):
        fixed_list[0:2] = (
            'Go with your love to the fields.',
            'Lie down in the shade. Rest your head',
            'in her lap. Swear allegiance',
            'to what is nighest your thoughts.',
            'As soon as the generals and the politicos',
            'can predict the motions of your mind,',
            'lose it. Leave it as a sign',
            'to mark the false trail, the way',
            'you didn’t go. Be like the fox',
            'who makes more tracks than necessary,',
            'some in the wrong direction.',
            'Practice resurrection.',
        )

    # Assert that fixed lists refuse to support appending.
    with raises(_BeartypeUtilCachedFixedListException):
        fixed_list.append('Love the world. Work for nothing.')

    # Assert that fixed lists refuse to support extending.
    with raises(_BeartypeUtilCachedFixedListException):
        fixed_list.extend((
            'Take all that you have and be poor.',
            'Love someone who does not deserve it.',
        ))

    # Assert that fixed lists refuse to support clearing.
    with raises(_BeartypeUtilCachedFixedListException):
        fixed_list.clear()

    # Assert that fixed lists refuse to support popping.
    with raises(_BeartypeUtilCachedFixedListException):
        fixed_list.pop()

    # Assert that fixed lists refuse to support removal.
    with raises(_BeartypeUtilCachedFixedListException):
        fixed_list.remove('Invest in the millennium. Plant sequoias.')
