#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype load-bearing JSON marshaller unit tests.**

This submodule unit tests the public :func:`beartype.loadbearing.to_json` and
:func:`beartype.loadbearing.from_json` marshallers.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from dataclasses import (
    dataclass,
    field,
)
from enum import Enum
from typing import Optional

# ....................{ DATA                               }....................
# Module-scoped test dataclasses. Unlike the sibling schema-centric test
# submodule (which locally scopes throwaway dataclasses), marshalling tests
# reuse this shared fixture data across serialization, deserialization, and
# round-trip tests.

class ThroughAllHisBulk(Enum):
    '''
    Arbitrary enumeration whose member values are all JSON-encodable.
    '''

    AN_AGONY = 'an agony'
    CREPT_GRADUAL = 'crept gradual'


@dataclass
class MortalImmortal:
    '''
    Arbitrary nested dataclass.
    '''

    from_the_feet: str
    unto_the_crown: int


@dataclass
class SlowPace(object):
    '''
    Arbitrary dataclass exercising the full currently supported hint subset.
    '''

    palsied_tongue: str
    made_his_hand: MortalImmortal
    a_vast_shade: ThroughAllHisBulk
    in_midst_of_his_own_brightness: Optional[float]
    like_the_bulk: list[int]
    of_memnons_image: tuple[str, int]
    at_the_set: tuple[float, ...] = ()
    of_sun: dict[str, bool] = field(default_factory=dict)


def _make_slow_pace() -> SlowPace:
    '''
    Arbitrary fully populated instance of the :class:`SlowPace` dataclass.
    '''

    return SlowPace(
        palsied_tongue='And all its ancient sway',
        made_his_hand=MortalImmortal(
            from_the_feet='to shine upon the sun', unto_the_crown=7),
        a_vast_shade=ThroughAllHisBulk.AN_AGONY,
        in_midst_of_his_own_brightness=0.5,
        like_the_bulk=[1, 2, 3],
        of_memnons_image=('dusk', 2),
        at_the_set=(1.0, 2.5),
        of_sun={'harp': True, 'strings': False},
    )

# ....................{ TESTS ~ serialize                  }....................
def test_to_json() -> None:
    '''
    Test the :func:`beartype.loadbearing.to_json` serializer.
    '''

    # Defer test-specific imports.
    from beartype.loadbearing import to_json
    from pytest import raises

    # Assert a fully populated instance serializes to the expected dictionary,
    # notably serializing enumeration members as their values, nested
    # dataclasses as nested objects, and tuples as arrays.
    assert to_json(_make_slow_pace()) == {
        'palsied_tongue': 'And all its ancient sway',
        'made_his_hand': {
            'from_the_feet': 'to shine upon the sun', 'unto_the_crown': 7},
        'a_vast_shade': 'an agony',
        'in_midst_of_his_own_brightness': 0.5,
        'like_the_bulk': [1, 2, 3],
        'of_memnons_image': ['dusk', 2],
        'at_the_set': [1.0, 2.5],
        'of_sun': {'harp': True, 'strings': False},
    }

    # Assert that non-instances are rejected.
    with raises(TypeError):
        to_json(SlowPace)
    with raises(TypeError):
        to_json('Sat gray-hair\'d Saturn, quiet as a stone,')


def test_to_json_violation() -> None:
    '''
    Test that the :func:`beartype.loadbearing.to_json` serializer validates
    fields against their type hints *before* serializing, failing loudly on a
    hint-violating instance rather than silently serializing JSON violating
    the corresponding :func:`beartype.loadbearing.to_json_schema` schema.

    Field assignment on dataclass instances is unchecked; a latent violation
    introduced by post-instantiation mutation would otherwise surface only at
    some arbitrarily distant deserialization (or schema validation) far from
    the code that actually introduced it.
    '''

    # Defer test-specific imports.
    from beartype.loadbearing import to_json
    from beartype.roar import BeartypeDoorHintViolation
    from pytest import raises

    # Well-formed instance of this dataclass.
    mortal_immortal = MortalImmortal(
        from_the_feet='to shine upon the sun', unto_the_crown=7)

    # Mutate a field of this instance into violating its type hint. Dataclass
    # attribute assignment is unchecked; this mutation succeeds silently.
    mortal_immortal.unto_the_crown = (  # type: ignore[assignment]
        'no longer an integer')

    # Assert that serializing this now-violating instance fails loudly.
    with raises(BeartypeDoorHintViolation):
        to_json(mortal_immortal)

# ....................{ TESTS ~ deserialize                }....................
def test_from_json() -> None:
    '''
    Test the :func:`beartype.loadbearing.from_json` deserializer against
    well-formed input.
    '''

    # Defer test-specific imports.
    from beartype.loadbearing import from_json

    # Assert a well-formed dictionary deserializes to the expected instance.
    assert from_json(SlowPace, {
        'palsied_tongue': 'And all its ancient sway',
        'made_his_hand': {
            'from_the_feet': 'to shine upon the sun', 'unto_the_crown': 7},
        'a_vast_shade': 'an agony',
        'in_midst_of_his_own_brightness': None,
        'like_the_bulk': [],
        'of_memnons_image': ['dusk', 2],
    }) == SlowPace(
        palsied_tongue='And all its ancient sway',
        made_his_hand=MortalImmortal(
            from_the_feet='to shine upon the sun', unto_the_crown=7),
        a_vast_shade=ThroughAllHisBulk.AN_AGONY,
        in_midst_of_his_own_brightness=None,
        like_the_bulk=[],
        of_memnons_image=('dusk', 2),

        # Defaulted fields intentionally omitted from the dictionary above,
        # asserting that defaults apply.
        at_the_set=(),
        of_sun={},
    )

    # Assert that fields hinted as floats additionally accept integers (JSON
    # draws *NO* distinction between "3" and "3.0"), converted to floats.
    numbered = from_json(SlowPace, {
        'palsied_tongue': 'His ancient mother',
        'made_his_hand': {'from_the_feet': 'for some comfort', 'unto_the_crown': 1},
        'a_vast_shade': 'crept gradual',
        'in_midst_of_his_own_brightness': 3,
        'like_the_bulk': [],
        'of_memnons_image': ['yet', 0],
    })
    assert numbered.in_midst_of_his_own_brightness == 3.0
    assert type(numbered.in_midst_of_his_own_brightness) is float

    # Assert that unrecognized keys are silently ignored.
    assert from_json(MortalImmortal, {
        'from_the_feet': 'to shine upon the sun',
        'unto_the_crown': 7,
        'unrecognized_key': 'is silently ignored',
    }) == MortalImmortal(
        from_the_feet='to shine upon the sun', unto_the_crown=7)


def test_from_json_invalid() -> None:
    '''
    Test the :func:`beartype.loadbearing.from_json` deserializer against
    malformed input, validating strict (non-coercive) deserialization.
    '''

    # Defer test-specific imports.
    from beartype.loadbearing import from_json
    from pytest import raises

    # Assert that non-dataclasses and non-dictionaries are rejected.
    with raises(TypeError):
        from_json('no dataclass here', {})
    with raises(TypeError):
        from_json(MortalImmortal, 'no dictionary here')

    # Assert that missing defaultless fields are rejected.
    with raises(ValueError):
        from_json(MortalImmortal, {'from_the_feet': 'alone'})

    # Assert that mistyped scalars are rejected rather than coerced.
    with raises(ValueError):
        from_json(MortalImmortal, {
            'from_the_feet': 'to shine upon the sun',
            'unto_the_crown': '7',
        })

    # Assert that booleans are *NOT* accepted as integers, avoiding the
    # standard "issubclass(bool, int)" pitfall.
    with raises(ValueError):
        from_json(MortalImmortal, {
            'from_the_feet': 'to shine upon the sun',
            'unto_the_crown': True,
        })

    # Assert that unrecognized enumeration values are rejected.
    with raises(ValueError):
        from_json(SlowPace, {
            'palsied_tongue': 'His ancient mother',
            'made_his_hand': {'from_the_feet': 'x', 'unto_the_crown': 1},
            'a_vast_shade': 'no such member value',
            'in_midst_of_his_own_brightness': None,
            'like_the_bulk': [],
            'of_memnons_image': ['yet', 0],
        })

    # Assert that fixed-length tuples of the wrong length are rejected.
    with raises(ValueError):
        from_json(SlowPace, {
            'palsied_tongue': 'His ancient mother',
            'made_his_hand': {'from_the_feet': 'x', 'unto_the_crown': 1},
            'a_vast_shade': 'an agony',
            'in_midst_of_his_own_brightness': None,
            'like_the_bulk': [],
            'of_memnons_image': ['too', 2, 'many'],
        })

# ....................{ TESTS ~ round-trip                 }....................
def test_json_round_trip() -> None:
    '''
    Test that the :func:`beartype.loadbearing.to_json` and
    :func:`beartype.loadbearing.from_json` marshallers round-trip: serializing
    an instance and deserializing the result yields an equal instance, and
    deserializing a canonical dictionary and re-serializing yields an equal
    dictionary.
    '''

    # Defer test-specific imports.
    from beartype.loadbearing import (
        from_json,
        to_json,
    )

    # Assert the instance-first round-trip preserves equality.
    slow_pace = _make_slow_pace()
    assert from_json(SlowPace, to_json(slow_pace)) == slow_pace

    # Assert the dictionary-first round-trip preserves equality. Note that
    # this dictionary intentionally supplies *ALL* fields (including
    # defaulted fields), as to_json() unconditionally serializes all fields.
    json_dict = {
        'palsied_tongue': 'And all its ancient sway',
        'made_his_hand': {
            'from_the_feet': 'to shine upon the sun', 'unto_the_crown': 7},
        'a_vast_shade': 'crept gradual',
        'in_midst_of_his_own_brightness': None,
        'like_the_bulk': [3, 2, 1],
        'of_memnons_image': ['dusk', 2],
        'at_the_set': [2.5],
        'of_sun': {'harp': False},
    }
    assert to_json(from_json(SlowPace, json_dict)) == json_dict
