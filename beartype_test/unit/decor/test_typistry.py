#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartypistry unit tests.**

This submodule unit tests the :attr:`beartype._decor._typistry.bear_typistry`
singleton.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import pytest

# ....................{ TESTS ~ callable : type           }....................
def test_typistry_register_type() -> None:
    '''
    Unit test the
    :func:`beartype._decor._typistry.register_typistry_type` function.
    '''

    # Defer heavyweight imports.
    from beartype.cave import AnyType
    from beartype.roar import _BeartypeDecorBeartypistryException
    from beartype._decor._typistry import bear_typistry, register_typistry_type
    from beartype_test.unit.data.data_hint import PepCustomSingleTypevared

    # Assert that types are registrable via a trivial function call.
    hint = AnyType
    hint_expr, hint_name = register_typistry_type(hint)
    assert isinstance(hint_expr, str)
    assert bear_typistry.get(hint_name) is hint

    # Assert that non-types are *NOT* registrable via the same function.
    with pytest.raises(_BeartypeDecorBeartypistryException):
        register_typistry_type((
            'The best lack all conviction,',
            'while the worst',
            'Are full of passionate intensity',
        ))

    # Assert that PEP-compliant types are *NOT* registrable via the same
    # function.
    with pytest.raises(_BeartypeDecorBeartypistryException):
        register_typistry_type(PepCustomSingleTypevared)

# ....................{ TESTS ~ callable : tuple          }....................
def test_typistry_register_tuple_pass() -> None:
    '''
    Unit test successful usage of the
    :func:`beartype._decor._typistry.register_typistry_tuple` function.
    '''

    # Defer heavyweight imports.
    from beartype.cave import CallableTypes, NoneTypeOr
    from beartype.roar import _BeartypeDecorBeartypistryException
    from beartype._decor._typistry import (
        bear_typistry, register_typistry_tuple)

    # Assert that tuples are registrable via a trivial function call.
    #
    # Note that, unlike types, tuples are internally registered under different
    # objects than their originals (e.g., to ignore both duplicates and
    # ordering) and *MUST* thus be tested by conversion to sets.
    hint = CallableTypes
    hint_expr, hint_name = register_typistry_tuple(hint)
    assert isinstance(hint_expr, str)
    assert set(bear_typistry.get(hint_name)) == set(hint)

    # Assert that tuples of one type are registrable via the same function,
    # but reduce to registering merely that type rather than that tuple.
    hint = (int,)
    hint_expr, hint_name = register_typistry_tuple(hint)
    assert isinstance(hint_expr, str)
    assert bear_typistry.get(hint_name) == int

    # Assert that tuples containing duplicate types are registrable via the
    # same function, but reduce to registering only the non-duplicate types.
    hint = (str, str, str,)
    hint_expr, hint_name = register_typistry_tuple(hint)
    assert isinstance(hint_expr, str)
    assert bear_typistry.get(hint_name) == (str,)

    # Assert that tuples guaranteed to contain *NO* duplicate types are
    # registrable via the same function.
    hint = NoneTypeOr[CallableTypes]
    hint_expr, hint_name = register_typistry_tuple(
        hint=hint, is_types_unique=True)
    assert isinstance(hint_expr, str)
    assert bear_typistry.get(hint_name) == hint

    # Assert that tuples of the same types but in different orders are
    # registrable via the same function but reduce to differing objects.
    hint_a = (int, str,)
    hint_b = (str, int,)
    _, hint_a_name = register_typistry_tuple(hint_a)
    _, hint_b_name = register_typistry_tuple(hint_b)
    assert hint_a_name != hint_b_name


def test_typistry_register_tuple_fail() -> None:
    '''
    Unit test unsuccessful usage of the
    :func:`beartype._decor._typistry.register_typistry_tuple` function.
    '''

    # Defer heavyweight imports
    from beartype.roar import _BeartypeDecorBeartypistryException
    from beartype._decor._typistry import register_typistry_tuple
    from beartype_test.unit.data.data_hint import PepCustomSingleUntypevared

    # Assert that hashable non-tuple objects are *NOT* registrable via this
    # function.
    with pytest.raises(_BeartypeDecorBeartypistryException):
        register_typistry_tuple('\n'.join((
            'I will arise and go now, and go to Innisfree,',
            'And a small cabin build there, of clay and wattles made;',
            'Nine bean-rows will I have there, a hive for the honey-bee,',
            'And live alone in the bee-loud glade.',
        )))

    # Assert that unhashable tuples are *NOT* registrable via this function.
    with pytest.raises(TypeError):
        register_typistry_tuple((
            int,
            str,
            {
                'Had': "I the heaven’s embroidered cloths,",
                'Enwrought': "with golden and silver light,",
                'The': 'blue and the dim and the dark cloths',
                'Of': 'night and light and the half-light,',
                'I': 'would spread the cloths under your feet:',
                'But': 'I, being poor, have only my dreams;',
                'I have': 'spread my dreams under your feet;',
                'Tread': 'softly because you tread on my dreams.',
            },
        ))

    # Assert that empty tuples are *NOT* registrable via this function.
    with pytest.raises(_BeartypeDecorBeartypistryException):
        register_typistry_tuple(())

    #FIXME: Currently broken. Decipher why, please. It appears likely that the
    #die_unless_hint_nonpep() validator is slightly broken. *sigh*

    # Assert that non-empty tuples containing one or more PEP-compliant types
    # are *NOT* registrable via this function.
    with pytest.raises(_BeartypeDecorBeartypistryException):
        register_typistry_tuple((int, PepCustomSingleUntypevared, str,))

# ....................{ TESTS ~ singleton                 }....................
def test_typistry_singleton_pass() -> None:
    '''
    Unit test successful usage of the
    :attr:`beartype._decor._typistry.bear_typistry` singleton.
    '''

    # Defer heavyweight imports.
    from beartype.cave import NoneType
    from beartype._decor._typistry import bear_typistry
    from beartype._util.utilobject import get_object_name_qualified

    # Assert that types are also registrable via dictionary syntax.
    hint = NoneType
    hint_name = get_object_name_qualified(hint)
    bear_typistry[hint_name] = hint
    assert bear_typistry.get(hint_name) is hint

    # Avoid asserting tuples are also registrable via dictionary syntax. While
    # they technically are, asserting so would require declaring a new
    # get_typistry_tuple_name() function, which would then require refactoring
    # the register_typistry_tuple_from_frozenset() function to call that
    # function, which would reduce performance. Moreover, since those two
    # functions would be operating on different tuple objects, it's unclear
    # whether that refactoring would even be feasible.


def test_typistry_singleton_fail() -> None:
    '''
    Unit test unsuccessful usage of the
    :attr:`beartype._decor._typistry.bear_typistry` singleton.
    '''

    # Defer heavyweight imports.
    from beartype.roar import _BeartypeDecorBeartypistryException
    from beartype._decor._typistry import bear_typistry

    # Assert that unhashable objects are *NOT* registrable.
    with pytest.raises(TypeError):
        bear_typistry['Turning.and.turning.in.the.widening.gyre'] = {
            'The falcon cannot hear the falconer;': (
                'Things fall apart; the centre cannot hold;'),
        }

    # Assert that forward references are *NOT* registrable.
    with pytest.raises(_BeartypeDecorBeartypistryException):
        bear_typistry['Mere.anarchy.is.loosed.upon.the.world'] = (
            'The blood-dimmed tide is loosed, and everywhere')

    # Assert that arbitrary objects are also *NOT* registrable.
    with pytest.raises(_BeartypeDecorBeartypistryException):
        bear_typistry['The.ceremony.of.innocence.is.drowned'] = 0xDEADBEEF

    # Assert that beartypistry keys that are *NOT* strings are rejected.
    with pytest.raises(_BeartypeDecorBeartypistryException):
        bear_typistry[(
            'And what rough beast, its hour come round at last,',)] = (
            'Slouches towards Bethlehem to be born?',)
