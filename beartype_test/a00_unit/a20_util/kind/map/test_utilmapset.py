#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **dictionary mutator** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.kind.map.utilmapset` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ mergers                    }....................
def test_merge_mappings_two() -> None:
    '''
    Test the :func:`beartype._util.kind.map.utilmapset.merge_mappings` function
    passed exactly two mappings.
    '''

    # Defer test-specific imports.
    from beartype._util.kind.map.utilmapset import merge_mappings
    from beartype_test.a00_unit.data.kind.data_kindmap import (
        FAREWELL_O_HIAWATHA,
        IN_THE_LODGE_OF_HIAWATHA,
        IN_THE_LODGE_OF_HIAWATHA_FAREWELL_O_HIAWATHA,
        THE_SONG_OF_HIAWATHA,
        THE_SONG_OF_HIAWATHA_IN_THE_LODGE_OF_HIAWATHA,
    )

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
    Test the :func:`beartype._util.kind.map.utilmapset.merge_mappings` function
    passed exactly three mappings.
    '''

    # Defer test-specific imports.
    from beartype._util.kind.map.utilmapset import merge_mappings
    from beartype_test.a00_unit.data.kind.data_kindmap import (
        FAREWELL_O_HIAWATHA,
        FROM_THE_BROW_OF_HIAWATHA,
        FROM_THE_BROW_OF_HIAWATHA_IN_THE_LODGE_OF_HIAWATHA_FAREWELL_O_HIAWATHA,
        IN_THE_LODGE_OF_HIAWATHA,
        THE_SONG_OF_HIAWATHA,
    )

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

# ....................{ TESTS ~ removers                   }....................
def test_remove_mapping_keys() -> None:
    '''
    Test the :func:`beartype._util.kind.map.utilmapset.remove_mapping_keys`
    function.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.kind.map.utilmapset import remove_mapping_keys
    from beartype_test.a00_unit.data.kind.data_kindmap import (
        FAREWELL_O_HIAWATHA,
        FAREWELL_O_HIAWATHA_MINUS_THE_SONG_OF_HIAWATHA,
        FROM_THE_BROW_OF_HIAWATHA,
        THE_SONG_OF_HIAWATHA,
    )

    # ....................{ LOCALS                         }....................
    # Shallow copies of arbitrary mappings to be modified below.
    farewell_o_hiawatha = FAREWELL_O_HIAWATHA.copy()

    # ....................{ ASSERTS                        }....................
    # Assert this remover preserves this mapping as is when removing from an
    # empty set.
    remove_mapping_keys(farewell_o_hiawatha, set())
    assert farewell_o_hiawatha == FAREWELL_O_HIAWATHA

    # Assert this remover preserves this mapping as is when removing from a
    # non-empty set containing *NO* keys of this mapping.
    remove_mapping_keys(farewell_o_hiawatha, FROM_THE_BROW_OF_HIAWATHA.keys())
    assert farewell_o_hiawatha == FAREWELL_O_HIAWATHA

    # Assert this remover removes all key-value pairs from this mapping that are
    # items of this non-empty set.
    remove_mapping_keys(farewell_o_hiawatha, THE_SONG_OF_HIAWATHA.keys())
    assert farewell_o_hiawatha == FAREWELL_O_HIAWATHA_MINUS_THE_SONG_OF_HIAWATHA

# ....................{ TESTS ~ updaters                   }....................
def test_update_mapping() -> None:
    '''
    Test the :func:`beartype._util.kind.map.utilmapset.update_mapping` function.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.kind.map.utilmapset import update_mapping
    from beartype_test.a00_unit.data.kind.data_kindmap import (
        FAREWELL_O_HIAWATHA,
        IN_THE_LODGE_OF_HIAWATHA,
        IN_THE_LODGE_OF_HIAWATHA_FAREWELL_O_HIAWATHA,
        THE_SONG_OF_HIAWATHA,
        THE_SONG_OF_HIAWATHA_IN_THE_LODGE_OF_HIAWATHA,
    )

    # ....................{ LOCALS                         }....................
    # Shallow copies of arbitrary mappings to be modified below.
    farewell_o_hiawatha = FAREWELL_O_HIAWATHA.copy()
    the_song_of_hiawatha = THE_SONG_OF_HIAWATHA.copy()

    # ....................{ ASSERTS                        }....................
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


def test_update_mapping_keys() -> None:
    '''
    Test the :func:`beartype._util.kind.map.utilmapset.update_mapping_keys`
    function.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.kind.map.utilmapset import update_mapping_keys

    # ....................{ LOCALS                         }....................
    # Arbitrary dictionary, initialized to the empty dictionary.
    spreading_a_shade = {}

    # ....................{ ASSERTS                        }....................
    # Assert that this function when passed *NO* keys preserves the passed
    # dictionary as is.
    update_mapping_keys(mapping=spreading_a_shade, keys=())
    assert spreading_a_shade == {}

    # Assert that this function when passed just one key adds a new key-value
    # pair to the passed dictionary mapping this key to the "None" singleton.
    update_mapping_keys(mapping=spreading_a_shade, keys=(
        "the Naiad 'mid her reeds.",))
    assert spreading_a_shade == {"the Naiad 'mid her reeds.": None}

    # Assert that this function when passed two or more keys adds new key-value
    # pairs to the passed dictionary mapping these keys to the "None" singleton.
    update_mapping_keys(mapping=spreading_a_shade, keys=(
        "Press'd her cold finger",
        'closer to her lips.',
    ))
    assert spreading_a_shade == {
        "the Naiad 'mid her reeds.": None,
        "Press'd her cold finger": None,
        'closer to her lips.': None,
    }
