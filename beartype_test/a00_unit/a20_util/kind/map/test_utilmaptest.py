#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **dictionary tester** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.kind.map.utilmaptest` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ validators                 }....................
def test_die_if_mappings_two_items_collide() -> None:
    '''
    Test the
    :func:`beartype._util.kind.map.utilmaptest.die_if_mappings_two_items_collide`
    validator.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilMappingException
    from beartype._util.kind.map.utilmaptest import (
        die_if_mappings_two_items_collide)
    from beartype_test.a00_unit.data.kind.data_kindmap import (
        FAREWELL_O_HIAWATHA,
        THE_SONG_OF_HIAWATHA,
        THE_SONG_OF_HIAWATHA_SINGING_IN_THE_SUNSHINE,
    )
    from pytest import raises

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
    :func:`beartype._util.kind.map.utilmaptest.is_mapping_keys_all` tester.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilMappingException
    from beartype._util.kind.map.utilmaptest import is_mapping_keys_all
    from beartype_test.a00_unit.data.kind.data_kindmap import (
        THE_SONG_OF_HIAWATHA,
        THE_SONG_OF_HIAWATHA_SINGING_IN_THE_SUNSHINE,
    )

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
    :func:`beartype._util.kind.map.utilmaptest.is_mapping_keys_any` tester.
    '''

    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilMappingException
    from beartype._util.kind.map.utilmaptest import is_mapping_keys_any
    from beartype_test.a00_unit.data.kind.data_kindmap import (
        FAREWELL_O_HIAWATHA)

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
