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

# ....................{ TESTS                              }....................
def test_frozendict() -> None:
    '''
    Test the :func:`beartype._util.kind.map.utilmapfrozen.FrozenDict`
    subclass.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeKindFrozenDictException
    from beartype._util.kind.map.utilmapfrozen import FrozenDict
    from pickle import (
        HIGHEST_PROTOCOL,
        dumps,
        loads,
    )
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Arbitrary non-empty frozen dictionaries.
    THE_POET = FrozenDict({
        'The Poet wandering on': 'through Arabie',
        'And Persia,': 'and the wild Carmanian waste,',
    })
    ITS_LONELIEST_DELL = FrozenDict({
        'Its loneliest dell,': 'where odorous plants entwine',
        'Beneath the hollow rocks': 'a natural bower,',
    })

    # Frozen dictionary containing all key-value pairs in the above two.
    BESIDE_A_SPARKLING_RIVULET = FrozenDict({
        'The Poet wandering on': 'through Arabie',
        'And Persia,': 'and the wild Carmanian waste,',
        'Its loneliest dell,': 'where odorous plants entwine',
        'Beneath the hollow rocks': 'a natural bower,',
    })

    # ....................{ PASS                           }....................
    # Assert that frozen dictionaries are hashable and preserve the same hash
    # value across consecutive hashings.
    assert hash(THE_POET) == hash(THE_POET)
    assert hash(ITS_LONELIEST_DELL) == hash(ITS_LONELIEST_DELL)

    # Assert that two different frozen dictionaries are both unequal *AND* hash
    # to different hashings.
    assert THE_POET != ITS_LONELIEST_DELL
    assert hash(THE_POET) != hash(ITS_LONELIEST_DELL)

    # Assert that the machine-readable representation of frozen dictionaries is
    # prefixed by the classname of these dictionaries followed by the key-value
    # pairs of these dictionaries.
    THE_POET_REPR = repr(THE_POET)
    assert isinstance(THE_POET_REPR, str)
    assert THE_POET_REPR.startswith(THE_POET.__class__.__name__)
    assert "'The Poet wandering on': 'through Arabie'" in THE_POET_REPR

    # Assert that pickling a frozen dictionary into a byte stream and then
    # unpickling that byte stream back into a frozen dictionary preserves that
    # dictionary as is.
    THE_POET_PICKLED = dumps(THE_POET, protocol=HIGHEST_PROTOCOL)
    THE_POET_UNPICKLED = loads(THE_POET_PICKLED)
    assert THE_POET_UNPICKLED == THE_POET

    # Assert that uniting two frozen dictionaries produces a third frozen
    # dictionary containing all key-value pairs in the first two.
    HE_STRETCHED = THE_POET | ITS_LONELIEST_DELL
    assert BESIDE_A_SPARKLING_RIVULET == HE_STRETCHED

    # Assert that the dict.fromkeys() class method behaves as expected.
    THE_POET_FROMKEYS = THE_POET.fromkeys(
        ('The Poet wandering on',), 'His languid limbs. A vision on his sleep',)
    assert THE_POET_FROMKEYS == FrozenDict({
        'The Poet wandering on': 'His languid limbs. A vision on his sleep',})

    # ....................{ FAIL                           }....................
    # Assert that that standard "dict" methods attempting to mutate the current
    # frozen dictionary raise the expected exception.
    with raises(BeartypeKindFrozenDictException):
        THE_POET["And o'er"] = 'the aërial mountains which pour down'
    with raises(BeartypeKindFrozenDictException):
        del THE_POET['The Poet wandering on']
    with raises(BeartypeKindFrozenDictException):
        THE_POET.clear()
    with raises(BeartypeKindFrozenDictException):
        THE_POET.pop('The Poet wandering on')
    with raises(BeartypeKindFrozenDictException):
        THE_POET.pop('And Persia,', 'Indus and Oxus from their icy caves,')
    with raises(BeartypeKindFrozenDictException):
        THE_POET.popitem()
    with raises(BeartypeKindFrozenDictException):
        THE_POET.setdefault('The Poet wandering on')
    with raises(BeartypeKindFrozenDictException):
        THE_POET.setdefault('In joy and exultation', 'held his way;')
    with raises(BeartypeKindFrozenDictException):
        THE_POET.update({'Till in the vale of Cashmire,': 'far within'})
