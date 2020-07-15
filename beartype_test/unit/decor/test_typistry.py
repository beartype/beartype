#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartypistry unit tests.**

This submodule unit tests the :attr:`beartype._decor.typistry.bear_typistry`
singleton.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import pytest

# ....................{ TESTS                             }....................
def test_typistry_pass() -> None:
    '''
    Test edge cases accepted by the
    :attr:`beartype._decor.typistry.bear_typistry` singleton.
    '''

    # Defer heavyweight imports
    from beartype.cave import AnyType, FunctionTypes, NoneType
    from beartype._decor._typistry import bear_typistry, register_type
    from beartype._util.utilobj import get_object_name_qualified

    # Assert that types are registrable via a trivial function call.
    register_type(AnyType)
    assert bear_typistry.get(get_object_name_qualified(AnyType)) is AnyType

    # Assert that types are also registrable via dictionary syntax.
    bear_typistry[get_object_name_qualified(NoneType)] = NoneType
    assert bear_typistry.get(get_object_name_qualified(NoneType)) is NoneType

    # Assert that tuples are also registrable via dictionary syntax.
    bear_typistry['beartype.cave.FunctionTypes'] = FunctionTypes
    assert bear_typistry.get('beartype.cave.FunctionTypes') is FunctionTypes


def test_typistry_fail() -> None:
    '''
    Test edge cases rejected by the
    :attr:`beartype._decor.typistry.bear_typistry` singleton.
    '''

    # Defer heavyweight imports
    from beartype.roar import (
        BeartypeDecorHintValueNonPepException,
        _BeartypeCallBeartypistryException,
    )
    from beartype._decor._typistry import bear_typistry, register_type

    # Assert that non-types are *NOT* registrable via the same function.
    with pytest.raises(_BeartypeCallBeartypistryException):
        register_type((
            'The best lack all conviction,',
            'while the worst',
            'Are full of passionate intensity',
        ))

    # Assert that unhashable objects are *NOT* registrable.
    with pytest.raises(TypeError):
        bear_typistry['Turning.and.turning.in.the.widening.gyre'] = {
            'The falcon cannot hear the falconer;': (
                'Things fall apart; the centre cannot hold;'),
        }

    # Assert that forward references are *NOT* registrable.
    with pytest.raises(BeartypeDecorHintValueNonPepException):
        bear_typistry['Mere.anarchy.is.loosed.upon.the.world'] = (
            'The blood-dimmed tide is loosed, and everywhere')

    # Assert that arbitrary objects are also *NOT* registrable.
    with pytest.raises(BeartypeDecorHintValueNonPepException):
        bear_typistry['The.ceremony.of.innocence.is.drowned'] = 0xDEADBEEF

    # Assert that beartypistry keys that are *NOT* strings are rejected.
    with pytest.raises(_BeartypeCallBeartypistryException):
        bear_typistry[(
            'And what rough beast, its hour come round at last,',)] = (
            'Slouches towards Bethlehem to be born?',)
