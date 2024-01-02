#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
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

# ....................{ TESTS ~ updaters                   }....................
def test_update_mapping() -> None:
    '''
    Test the :func:`beartype._util.kind.map.utilmapset.update_mapping` function.
    '''

    # Defer test-specific imports.
    from beartype._util.kind.map.utilmapset import update_mapping
    from beartype_test.a00_unit.data.kind.data_kindmap import (
        FAREWELL_O_HIAWATHA,
        IN_THE_LODGE_OF_HIAWATHA,
        IN_THE_LODGE_OF_HIAWATHA_FAREWELL_O_HIAWATHA,
        THE_SONG_OF_HIAWATHA,
        THE_SONG_OF_HIAWATHA_IN_THE_LODGE_OF_HIAWATHA,
    )

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
