#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype load-bearing API unit tests.**

This submodule unit tests the public :mod:`beartype.loadbearing` subpackage.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ scalar                     }....................
def test_to_json_schema_scalars() -> None:
    '''
    Test the :func:`beartype.loadbearing.to_json_schema` translator against a
    dataclass hinted by scalar types, additionally validating that defaulted
    fields are omitted from the ``"required"`` list.
    '''

    # Defer test-specific imports.
    from beartype.loadbearing import to_json_schema
    from dataclasses import dataclass, field

    @dataclass
    class DeepInTheShadySadnessOfAVale:
        far_sunken: str
        from_the_healthy_breath_of_morn: int
        grey_haired_saturn: float
        quiet_as_a_stone: bool = True
        still_as_the_silence: list[str] = field(default_factory=list)

    # Assert this dataclass translates to the expected schema.
    assert to_json_schema(DeepInTheShadySadnessOfAVale) == {
        'title': 'DeepInTheShadySadnessOfAVale',
        'type': 'object',
        'properties': {
            'far_sunken': {'type': 'string'},
            'from_the_healthy_breath_of_morn': {'type': 'integer'},
            'grey_haired_saturn': {'type': 'number'},
            'quiet_as_a_stone': {'type': 'boolean'},
            'still_as_the_silence': {
                'type': 'array', 'items': {'type': 'string'}},
        },
        'required': [
            'far_sunken',
            'from_the_healthy_breath_of_morn',
            'grey_haired_saturn',
        ],
    }

# ....................{ TESTS ~ union                      }....................
def test_to_json_schema_union() -> None:
    '''
    Test the :func:`beartype.loadbearing.to_json_schema` translator against
    dataclasses hinted by optionals and unions.
    '''

    # Defer test-specific imports.
    from beartype.loadbearing import to_json_schema
    from dataclasses import dataclass
    from typing import (
        Optional,
        Union,
    )

    @dataclass
    class UponTheSoddenGround:
        his_old_right_hand: Optional[str]
        nerveless_listless_dead: Union[int, float]

    # Schema translated from this dataclass.
    schema = to_json_schema(UponTheSoddenGround)

    # Assert both unions translated to "anyOf" schemas. Note that the ordering
    # of "anyOf" members is *NOT* asserted, as "beartype.door" reserves the
    # right to normalize the ordering of union child hints.
    his_old_right_hand = schema['properties']['his_old_right_hand']
    assert sorted(
        any_of['type'] for any_of in his_old_right_hand['anyOf']) == [
        'null', 'string']

    nerveless = schema['properties']['nerveless_listless_dead']
    assert sorted(any_of['type'] for any_of in nerveless['anyOf']) == [
        'integer', 'number']

    # Assert both defaultless fields are required.
    assert schema['required'] == [
        'his_old_right_hand', 'nerveless_listless_dead']

# ....................{ TESTS ~ literal : enum             }....................
def test_to_json_schema_literal() -> None:
    '''
    Test the :func:`beartype.loadbearing.to_json_schema` translator against a
    dataclass hinted by :obj:`typing.Literal` hints.
    '''

    # Defer test-specific imports.
    from beartype.loadbearing import to_json_schema
    from dataclasses import dataclass
    from typing import Literal

    @dataclass
    class NoStirOfAir:
        was_there: Literal['Not so much life as on a summer\'s day']
        robs_not: Literal['one light seed', 'from the feather\'d grass', 42]

    # Schema translated from this dataclass.
    schema = to_json_schema(NoStirOfAir)

    # Assert the single-literal hint translated to a "const" schema.
    assert schema['properties']['was_there'] == {
        'const': "Not so much life as on a summer's day"}

    # Assert the multi-literal hint translated to an "enum" schema.
    assert schema['properties']['robs_not'] == {
        'enum': ['one light seed', "from the feather'd grass", 42]}


def test_to_json_schema_enum() -> None:
    '''
    Test the :func:`beartype.loadbearing.to_json_schema` translator against a
    dataclass hinted by an :class:`enum.Enum` subclass.
    '''

    # Defer test-specific imports.
    from beartype.loadbearing import to_json_schema
    from dataclasses import dataclass
    from enum import Enum

    class ForestOnForest(Enum):
        HUNG_ABOUT_HIS_HEAD = 'hung about his head'
        LIKE_CLOUD_ON_CLOUD = 'like cloud on cloud'

    @dataclass
    class ShadyVale:
        canopy: ForestOnForest

    # Assert this enumeration translated to an "enum" schema over the *VALUES*
    # (rather than names) of all enumeration members.
    assert to_json_schema(ShadyVale)['properties']['canopy'] == {
        'title': 'ForestOnForest',
        'enum': ['hung about his head', 'like cloud on cloud'],
    }

# ....................{ TESTS ~ container                  }....................
def test_to_json_schema_containers() -> None:
    '''
    Test the :func:`beartype.loadbearing.to_json_schema` translator against a
    dataclass hinted by subscripted container hints.
    '''

    # Defer test-specific imports.
    from beartype.loadbearing import to_json_schema
    from dataclasses import dataclass
    from typing import Any

    @dataclass
    class AlongTheMarginSand:
        large_footmarks: dict[str, int]
        went_no_further: set[str]
        than_where_his_feet: tuple[str, int]
        had_stray_d: tuple[float, ...]
        and_slept: Any

    # Schema translated from this dataclass.
    schema = to_json_schema(AlongTheMarginSand)
    properties = schema['properties']

    # Assert each container hint translated as expected.
    assert properties['large_footmarks'] == {
        'type': 'object', 'additionalProperties': {'type': 'integer'}}
    assert properties['went_no_further'] == {
        'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True}
    assert properties['than_where_his_feet'] == {
        'type': 'array',
        'prefixItems': [{'type': 'string'}, {'type': 'integer'}],
        'minItems': 2,
        'maxItems': 2,
    }
    assert properties['had_stray_d'] == {
        'type': 'array', 'items': {'type': 'number'}}

    # Assert "typing.Any" translated to the vacuously true schema.
    assert properties['and_slept'] == {}

# ....................{ TESTS ~ nest                       }....................
def test_to_json_schema_nested() -> None:
    '''
    Test the :func:`beartype.loadbearing.to_json_schema` translator against a
    dataclass nesting another dataclass.
    '''

    # Defer test-specific imports.
    from beartype.loadbearing import to_json_schema
    from dataclasses import dataclass

    @dataclass
    class VoicelessStream:
        still_deadened_more: str

    @dataclass
    class ByReasonOfHisFallenDivinity:
        a_stream_went: VoicelessStream

    # Assert the nested dataclass translated to an inline "object" subschema.
    assert to_json_schema(ByReasonOfHisFallenDivinity) == {
        'title': 'ByReasonOfHisFallenDivinity',
        'type': 'object',
        'properties': {
            'a_stream_went': {
                'title': 'VoicelessStream',
                'type': 'object',
                'properties': {
                    'still_deadened_more': {'type': 'string'},
                },
                'required': ['still_deadened_more'],
            },
        },
        'required': ['a_stream_went'],
    }

# ....................{ TESTS ~ fail                       }....................
def test_to_json_schema_unsupported() -> None:
    '''
    Test that the :func:`beartype.loadbearing.to_json_schema` translator raises
    the expected exceptions when passed unsupported objects, validating that
    unsupported hints fail loudly rather than degrading silently.
    '''

    # Defer test-specific imports.
    from beartype.loadbearing import to_json_schema
    from collections.abc import Callable
    from dataclasses import dataclass
    from pytest import raises

    # Assert that non-dataclasses are rejected.
    with raises(TypeError):
        to_json_schema('But where the dead leaf fell, there did it rest.')

    # Assert that a currently untranslatable hint (e.g., a callable) is
    # rejected loudly.
    @dataclass
    class APlaceBeyondOurMemory:
        listener: Callable[[], None]

    with raises(NotImplementedError):
        to_json_schema(APlaceBeyondOurMemory)

    # Assert that dictionaries keyed by non-strings are rejected loudly, as
    # JSON object keys are *ALWAYS* strings.
    @dataclass
    class SpiritedSighs:
        keyed_wrongly: dict[int, str]

    with raises(NotImplementedError):
        to_json_schema(SpiritedSighs)


def test_to_json_schema_recursive() -> None:
    '''
    Test that the :func:`beartype.loadbearing.to_json_schema` translator raises
    the expected exception when passed a recursive dataclass, which this
    proof-of-concept intentionally does *not* yet support.
    '''

    # Defer test-specific imports.
    from beartype.loadbearing import to_json_schema
    from dataclasses import dataclass
    from pytest import raises

    @dataclass
    class OnJuttingBoughs:
        the_frost: 'OnJuttingBoughs'

    # Monkey-patch this locally defined dataclass into module scope, enabling
    # the stringified self-referential hint above to be resolved by
    # typing.get_type_hints() against this module's namespace.
    globals()['OnJuttingBoughs'] = OnJuttingBoughs

    # Assert that this recursive dataclass is rejected loudly.
    with raises(NotImplementedError):
        to_json_schema(OnJuttingBoughs)
