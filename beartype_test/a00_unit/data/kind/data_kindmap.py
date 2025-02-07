#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **dictionary data** submodule.

This submodule predefines low-level dictionary singletons exercising known edge
cases on behalf of higher-level unit test submodules.
'''

# ....................{ MAPPINGS                           }....................
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
collisions with the :data:`.THE_SONG_OF_HIAWATHA` dictionary *and* unhashable
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
  :data:`.FAREWELL_O_HIAWATHA` dictionary.
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
collisions with the :data:`.THE_SONG_OF_HIAWATHA` dictionary.
'''

# ....................{ MAPPINGS ~ merged                  }....................
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
Dictionary produced by merging the :data:`.THE_SONG_OF_HIAWATHA` and
:data:`.IN_THE_LODGE_OF_HIAWATHA` dictionaries.
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
Dictionary produced by merging the :data:`.IN_THE_LODGE_OF_HIAWATHA` and
:data:`.FAREWELL_O_HIAWATHA` dictionaries.
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
Dictionary produced by merging the :data:`.FROM_THE_BROW_OF_HIAWATHA`,
:data:`.IN_THE_LODGE_OF_HIAWATHA`, and :data:`.FAREWELL_O_HIAWATHA`
dictionaries.
'''

# ....................{ MAPPINGS ~ removed                 }....................
FAREWELL_O_HIAWATHA_MINUS_THE_SONG_OF_HIAWATHA = {
    'Thus departed': 'Hiawatha,',
    'In the purple': 'mists of evening,',
    'To the regions': 'of the home-wind,',
    'Of the Northwest-Wind,': 'Keewaydin.',
}
'''
Dictionary produced by removing all key-value pairs from the
:data:`.IN_THE_LODGE_OF_HIAWATHA` dictionary whose keys are also keys of the
the :data:`.THE_SONG_OF_HIAWATHA` dictionary.
'''
