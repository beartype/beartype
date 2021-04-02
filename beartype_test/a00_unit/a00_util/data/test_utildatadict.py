#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **mapping utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.data.utildatadict` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ CONSTANTS                         }....................
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

# ....................{ TESTS                             }....................
def test_merge_mappings_two_pass() -> None:
    '''
    Test successful usage of the
    :func:`beartype._util.data.utildatadict.merge_mappings` function passed
    exactly two mappings.
    '''

    # Defer heavyweight imports.
    from beartype._util.data.utildatadict import merge_mappings

    # Assert this function merges two empty mappings into a new empty mapping.
    assert merge_mappings({}, {}) == {}

    # Assert this function merges a non-empty mapping and an empty mapping into
    # the same non-empty mapping.
    assert merge_mappings(THE_SONG_OF_HIAWATHA, {}) == THE_SONG_OF_HIAWATHA
    assert merge_mappings({}, THE_SONG_OF_HIAWATHA) == THE_SONG_OF_HIAWATHA

    # Assert this function merges two non-empty mappings containing no
    # key-value collisions into the expected mapping.
    assert merge_mappings(THE_SONG_OF_HIAWATHA, IN_THE_LODGE_OF_HIAWATHA) == (
        THE_SONG_OF_HIAWATHA_IN_THE_LODGE_OF_HIAWATHA)
    assert merge_mappings(IN_THE_LODGE_OF_HIAWATHA, THE_SONG_OF_HIAWATHA) == (
        THE_SONG_OF_HIAWATHA_IN_THE_LODGE_OF_HIAWATHA)

    # Assert this function merges two non-empty mappings containing multiple
    # key collisions but no key-value collisions into the expected mapping.
    assert merge_mappings(IN_THE_LODGE_OF_HIAWATHA, FAREWELL_O_HIAWATHA) == (
        IN_THE_LODGE_OF_HIAWATHA_FAREWELL_O_HIAWATHA)
    assert merge_mappings(FAREWELL_O_HIAWATHA, IN_THE_LODGE_OF_HIAWATHA) == (
        IN_THE_LODGE_OF_HIAWATHA_FAREWELL_O_HIAWATHA)


def test_merge_mappings_three_pass() -> None:
    '''
    Test successful usage of the
    :func:`beartype._util.data.utildatadict.merge_mappings` function passed
    exactly three mappings.
    '''

    # Defer heavyweight imports.
    from beartype._util.data.utildatadict import merge_mappings

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


def test_merge_mappings_fail() -> None:
    '''
    Test unsuccessful usage of the
    :func:`beartype._util.data.utildatadict.merge_mappings` function.
    '''

    # Defer heavyweight imports.
    from beartype.roar import _BeartypeUtilMappingException
    from beartype._util.data.utildatadict import merge_mappings

    # Assert this function rejects two non-empty mappings containing one or
    # more key-value collisions.
    with raises(_BeartypeUtilMappingException):
        merge_mappings(THE_SONG_OF_HIAWATHA, FAREWELL_O_HIAWATHA)
    with raises(_BeartypeUtilMappingException):
        merge_mappings(FAREWELL_O_HIAWATHA, THE_SONG_OF_HIAWATHA)

    # Assert this function rejects two non-empty mappings containing one or
    # more key-value collisions and another non-empty mapping containing no
    # key-value collisions..
    with raises(_BeartypeUtilMappingException):
        merge_mappings(
            THE_SONG_OF_HIAWATHA,
            FAREWELL_O_HIAWATHA,
            FROM_THE_BROW_OF_HIAWATHA,
        )
