#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **mapping utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.kind.utilkinddict` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ CONSTANTS                          }....................
THE_SONG_OF_HIAWATHA = {
    'By the shore': 'of Gitche Gumee',
    'By the shining': 'Big-Sea-Water',
    'At the': 'doorway of his wigwam',
    'In the': 'pleasant Summer morning',
    'Hiawatha': 'stood and waited.',
}
'''
Arbitrary dictionary to be merged.
'''


THE_SONG_OF_HIAWATHA_SINGING_IN_THE_SUNSHINE = {
    'By the shore': 'of Gitche Gumee',
    'By the shining': ['Big-Sea-Water',],
    'At the': 'doorway of his wigwam',
    'In the': ['pleasant', 'Summer morning',],
    'Hiawatha': 'stood and waited.',
    'All the air': ['was', 'full of freshness,',],
    'All the earth': 'was bright and joyous,',
    'And': ['before him,', 'through the sunshine,',],
    'Westward': 'toward the neighboring forest',
    'Passed in': ['golden swarms', 'the Ahmo,',],
    'Passed the': 'bees, the honey-makers,',
    'Burning,': ['singing', 'in the sunshine.',],
}
'''
Arbitrary dictionary to be merged, intentionally containing two key-value
collisions with the :data:`THE_SONG_OF_HIAWATHA` dictionary *and* unhashable
values.
'''


FROM_THE_BROW_OF_HIAWATHA = {
    'From the': 'brow of Hiawatha',
    'Gone was': 'every trace of sorrow,',
    'As the fog': 'from off the water,',
    'As the mist': 'from off the meadow.',
}
'''
Arbitrary dictionary to be merged, intentionally containing neither key nor
key-value collisions with any other global dictionary.
'''


IN_THE_LODGE_OF_HIAWATHA = {
    'I am': 'going, O Nokomis,',
    'On a': 'long and distant journey,',
    'To the portals': 'of the Sunset,',
    'To the regions': 'of the home-wind,',
    'Of the Northwest-Wind,': 'Keewaydin.',
}
'''
Arbitrary dictionary to be merged, intentionally containing:

* No key-value collisions with the :data:`THE_SONG_OF_HIAWATHA` dictionary.
* Two key collisions but *no* key-value collisions with the
  :data:`FAREWELL_O_HIAWATHA` dictionary.
'''


FAREWELL_O_HIAWATHA = {
    'Thus departed': 'Hiawatha,',
    'Hiawatha': 'the Beloved,',
    'In the': 'glory of the sunset,',
    'In the purple': 'mists of evening,',
    'To the regions': 'of the home-wind,',
    'Of the Northwest-Wind,': 'Keewaydin.',
}
'''
Arbitrary dictionary to be merged, intentionally containing two key-value
collisions with the :data:`THE_SONG_OF_HIAWATHA` dictionary.
'''


THE_SONG_OF_HIAWATHA_IN_THE_LODGE_OF_HIAWATHA = {
    'By the shore': 'of Gitche Gumee',
    'By the shining': 'Big-Sea-Water',
    'At the': 'doorway of his wigwam',
    'In the': 'pleasant Summer morning',
    'Hiawatha': 'stood and waited.',
    'I am': 'going, O Nokomis,',
    'On a': 'long and distant journey,',
    'To the portals': 'of the Sunset,',
    'To the regions': 'of the home-wind,',
    'Of the Northwest-Wind,': 'Keewaydin.',
}
'''
Dictionary produced by merging the :data:`THE_SONG_OF_HIAWATHA` and
:data:`IN_THE_LODGE_OF_HIAWATHA` dictionaries.
'''


IN_THE_LODGE_OF_HIAWATHA_FAREWELL_O_HIAWATHA = {
    'I am': 'going, O Nokomis,',
    'On a': 'long and distant journey,',
    'To the portals': 'of the Sunset,',
    'To the regions': 'of the home-wind,',
    'Of the Northwest-Wind,': 'Keewaydin.',
    'Thus departed': 'Hiawatha,',
    'Hiawatha': 'the Beloved,',
    'In the': 'glory of the sunset,',
    'In the purple': 'mists of evening,',
}
'''
Dictionary produced by merging the :data:`IN_THE_LODGE_OF_HIAWATHA` and
:data:`FAREWELL_O_HIAWATHA` dictionaries.
'''


FROM_THE_BROW_OF_HIAWATHA_IN_THE_LODGE_OF_HIAWATHA_FAREWELL_O_HIAWATHA = {
    'From the': 'brow of Hiawatha',
    'Gone was': 'every trace of sorrow,',
    'As the fog': 'from off the water,',
    'As the mist': 'from off the meadow.',
    'I am': 'going, O Nokomis,',
    'On a': 'long and distant journey,',
    'To the portals': 'of the Sunset,',
    'To the regions': 'of the home-wind,',
    'Of the Northwest-Wind,': 'Keewaydin.',
    'Thus departed': 'Hiawatha,',
    'Hiawatha': 'the Beloved,',
    'In the': 'glory of the sunset,',
    'In the purple': 'mists of evening,',
}
'''
Dictionary produced by merging the :data:`FROM_THE_BROW_OF_HIAWATHA`,
:data:`IN_THE_LODGE_OF_HIAWATHA`, and :data:`FAREWELL_O_HIAWATHA` dictionaries.
'''

# ....................{ TESTS ~ validators                 }....................
def test_die_if_mappings_two_items_collide() -> None:
    '''
    Test the
    :func:`beartype._util.kind.utilkinddict.die_if_mappings_two_items_collide`
    validator.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilMappingException
    from beartype._util.kind.utilkinddict import (
        die_if_mappings_two_items_collide)

    # Assert this validator raises the expected exception when passed two
    # non-empty mappings containing one or more key-value collisions whose
    # values are all hashable.
    with raises(_BeartypeUtilMappingException):
        die_if_mappings_two_items_collide(
            THE_SONG_OF_HIAWATHA, FAREWELL_O_HIAWATHA)
    with raises(_BeartypeUtilMappingException):
        die_if_mappings_two_items_collide(
            FAREWELL_O_HIAWATHA, THE_SONG_OF_HIAWATHA)

    # Assert this validator raises the expected exception when passed two
    # non-empty mappings containing one or more key-value collisions such that
    # some values of the second mapping are unhashable.
    with raises(_BeartypeUtilMappingException):
        die_if_mappings_two_items_collide(
            THE_SONG_OF_HIAWATHA, THE_SONG_OF_HIAWATHA_SINGING_IN_THE_SUNSHINE)

# ....................{ TESTS ~ testers                    }....................
def test_is_mapping_keys_all() -> None:
    '''
    Test the
    :func:`beartype._util.kind.utilkinddict.is_mapping_keys_all` tester.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilMappingException
    from beartype._util.kind.utilkinddict import is_mapping_keys_all

    # Assert this tester returns true when passed a mapping containing all keys
    # in the passed set.
    assert is_mapping_keys_all(
        mapping=THE_SONG_OF_HIAWATHA_SINGING_IN_THE_SUNSHINE,
        keys=THE_SONG_OF_HIAWATHA.keys(),
    ) is True

    # Assert this tester returns false when passed a mapping *NOT* containing
    # all keys in the passed set.
    assert is_mapping_keys_all(
        mapping=THE_SONG_OF_HIAWATHA_SINGING_IN_THE_SUNSHINE,
        keys=THE_SONG_OF_HIAWATHA.keys() | {'As the mist',},
    ) is False


def test_is_mapping_keys_any() -> None:
    '''
    Test the
    :func:`beartype._util.kind.utilkinddict.is_mapping_keys_any` tester.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilMappingException
    from beartype._util.kind.utilkinddict import is_mapping_keys_any

    # Assert this tester returns true when passed a mapping containing any key
    # in the passed set.
    assert is_mapping_keys_any(
        mapping=FAREWELL_O_HIAWATHA,
        keys={'Thus departed', 'By the shore', 'To the portals'},
    ) is True

    # Assert this tester returns false when passed a mapping containing *NO* key
    # in the passed set.
    assert is_mapping_keys_any(
        mapping=FAREWELL_O_HIAWATHA,
        keys={'By the shore', 'To the portals'},
    ) is False

# ....................{ TESTS ~ updaters                   }....................
def test_update_mapping() -> None:
    '''
    Test the :func:`beartype._util.kind.utilkinddict.update_mapping` function.
    '''

    # Defer test-specific imports.
    from beartype._util.kind.utilkinddict import update_mapping

    # Shallow copies of arbitrary mappings to be modified below.
    farewell_o_hiawatha = FAREWELL_O_HIAWATHA.copy()
    the_song_of_hiawatha = THE_SONG_OF_HIAWATHA.copy()

    # Assert this updater preserves this mapping when updated from an empty
    # mapping.
    update_mapping(farewell_o_hiawatha, {})
    assert farewell_o_hiawatha == FAREWELL_O_HIAWATHA

    # Assert this updater updates this mapping as expected when updating from a
    # non-empty mapping containing no key or key-value collisions.
    update_mapping(the_song_of_hiawatha, IN_THE_LODGE_OF_HIAWATHA)
    assert the_song_of_hiawatha == (
        THE_SONG_OF_HIAWATHA_IN_THE_LODGE_OF_HIAWATHA)

    # Assert this updater updates this mapping as expected when updating from a
    # non-empty mapping containing multiple key but no key-value collisions.
    update_mapping(farewell_o_hiawatha, IN_THE_LODGE_OF_HIAWATHA)
    assert farewell_o_hiawatha == IN_THE_LODGE_OF_HIAWATHA_FAREWELL_O_HIAWATHA

# ....................{ TESTS ~ mergers                    }....................
def test_merge_mappings_two() -> None:
    '''
    Test the :func:`beartype._util.kind.utilkinddict.merge_mappings` function
    passed exactly two mappings.
    '''

    # Defer test-specific imports.
    from beartype._util.kind.utilkinddict import merge_mappings

    # Assert this function merges two empty mappings into a new empty mapping.
    assert merge_mappings({}, {}) == {}

    # Assert this function merges a non-empty mapping and an empty mapping into
    # the same non-empty mapping.
    assert merge_mappings(THE_SONG_OF_HIAWATHA, {}) == THE_SONG_OF_HIAWATHA
    assert merge_mappings({}, THE_SONG_OF_HIAWATHA) == THE_SONG_OF_HIAWATHA

    # Assert this function merges two non-empty mappings containing no key or
    # key-value collisions into the expected mapping.
    assert merge_mappings(THE_SONG_OF_HIAWATHA, IN_THE_LODGE_OF_HIAWATHA) == (
        THE_SONG_OF_HIAWATHA_IN_THE_LODGE_OF_HIAWATHA)
    assert merge_mappings(IN_THE_LODGE_OF_HIAWATHA, THE_SONG_OF_HIAWATHA) == (
        THE_SONG_OF_HIAWATHA_IN_THE_LODGE_OF_HIAWATHA)

    # Assert this function merges two non-empty mappings containing multiple
    # key but no key-value collisions into the expected mapping.
    assert merge_mappings(IN_THE_LODGE_OF_HIAWATHA, FAREWELL_O_HIAWATHA) == (
        IN_THE_LODGE_OF_HIAWATHA_FAREWELL_O_HIAWATHA)
    assert merge_mappings(FAREWELL_O_HIAWATHA, IN_THE_LODGE_OF_HIAWATHA) == (
        IN_THE_LODGE_OF_HIAWATHA_FAREWELL_O_HIAWATHA)


def test_merge_mappings_three() -> None:
    '''
    Test the :func:`beartype._util.kind.utilkinddict.merge_mappings` function
    passed exactly three mappings.
    '''

    # Defer test-specific imports.
    from beartype._util.kind.utilkinddict import merge_mappings

    # Assert this function merges three empty mappings into a new empty
    # mapping.
    assert merge_mappings({}, {}, {}) == {}

    # Assert this function merges a non-empty mapping and two empty mappings
    # into the same non-empty mapping.
    assert merge_mappings(THE_SONG_OF_HIAWATHA, {}, {}) == THE_SONG_OF_HIAWATHA
    assert merge_mappings({}, THE_SONG_OF_HIAWATHA, {}) == THE_SONG_OF_HIAWATHA
    assert merge_mappings({}, {}, THE_SONG_OF_HIAWATHA) == THE_SONG_OF_HIAWATHA

    # Assert this function merges two non-empty mappings containing multiple
    # key collisions but no key-value collisions and another non-empty mapping
    # containing neither key nor key-value collisions into the expected
    # mapping.
    assert merge_mappings(
        FROM_THE_BROW_OF_HIAWATHA,
        IN_THE_LODGE_OF_HIAWATHA,
        FAREWELL_O_HIAWATHA,
    ) == (
        FROM_THE_BROW_OF_HIAWATHA_IN_THE_LODGE_OF_HIAWATHA_FAREWELL_O_HIAWATHA)
