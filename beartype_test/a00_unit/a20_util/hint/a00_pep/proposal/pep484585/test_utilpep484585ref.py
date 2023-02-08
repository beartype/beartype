#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484` and :pep:`585` **forward reference type hint utility
unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep484585.utilpep484585ref` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ kind : subclass            }....................
def test_get_hint_pep484585_forwardref_classname_relative_to_object() -> None:
    '''
    Test the ``get_hint_pep484585_forwardref_classname_relative_to_object``
    getter defined by the
    :mod:`beartype._util.hint.pep.proposal.pep484585.utilpep484585ref`
    submodule.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintForwardRefException
    from beartype._util.hint.pep.proposal.pep484.utilpep484ref import (
        HINT_PEP484_FORWARDREF_TYPE)
    from beartype._util.hint.pep.proposal.pep484585.utilpep484585ref import (
        get_hint_pep484585_forwardref_classname,
        get_hint_pep484585_forwardref_classname_relative_to_object,
    )
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Arbitrary absolute forward reference defined as a string.
    THE_MASK_OF_ANARCHY = 'as_I.lay_asleep.in_Italy'

    # Arbitrary absolute forward reference defined as a non-string.
    WITH_GREAT_POWER = HINT_PEP484_FORWARDREF_TYPE(
        'And_with.great_power.it_forth.led_me')

    # Arbitrary relative forward reference defined as a string.
    VERY_SMOOTH = 'Very_smooth_he_looked_yet_grim'

    # ....................{ CLASSES                        }....................
    class IMetMurderOnTheWay(object):
        '''
        Arbitrary class to be monkey-patched with a well-defined ``__module__``
        dunder attribute below.
        '''

    # Monkey-patch this class with a well-defined "__module__" dunder attribute.
    IMetMurderOnTheWay.__module__ = 'He_had.a_mask.like_Castlereagh'

    # ....................{ PASS                           }....................
    # Assert this getter preserves the passed absolute forward reference as is
    # when defined as a string, regardless of whether the second passed object
    # defines the "__module__" dunder attribute.
    assert get_hint_pep484585_forwardref_classname_relative_to_object(
        hint=THE_MASK_OF_ANARCHY,
        obj=b'There came a voice from over the Sea,',
    ) is THE_MASK_OF_ANARCHY

    # Assert this getter preserves the passed absolute forward reference as is
    # when defined as a non-string, regardless of whether the second passed
    # object defines the "__module__" dunder attribute.
    assert get_hint_pep484585_forwardref_classname_relative_to_object(
        hint=WITH_GREAT_POWER,
        obj=b'To walk in the visions of Poesy.',
    ) == get_hint_pep484585_forwardref_classname(WITH_GREAT_POWER)

    # Assert this getter canonicalizes the passed relative forward reference
    # against the "__module__" dunder attribute of the second passed object.
    assert get_hint_pep484585_forwardref_classname_relative_to_object(
        hint=VERY_SMOOTH, obj=IMetMurderOnTheWay) == (
        f'{IMetMurderOnTheWay.__module__}.{VERY_SMOOTH}')

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed a relative
    # forward reference and the second object does *NOT* define the "__module__"
    # dunder attribute.
    with raises(BeartypeDecorHintForwardRefException):
        get_hint_pep484585_forwardref_classname_relative_to_object(
            hint=VERY_SMOOTH,
            obj='Seven blood-hounds followed him:',
        )
