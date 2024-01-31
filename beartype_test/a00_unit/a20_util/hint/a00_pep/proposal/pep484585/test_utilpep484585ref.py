#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
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

# ....................{ TESTS ~ getter                     }....................
def test_get_hint_pep484585_ref_name() -> None:
    '''
    Test
    :func:`beartype._util.hint.pep.proposal.pep484585.utilpep484585ref.get_hint_pep484585_ref_name`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintForwardRefException
    from beartype.typing import ForwardRef
    from beartype._util.hint.pep.proposal.pep484585.utilpep484585ref import (
        get_hint_pep484585_ref_name)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Arbitrary absolute forward references defined as strings.
    ALAS_ALAS = 'He_overleaps.the.bounds'
    BREATH_AND = 'Were.limbs_and.breath_and'

    # Arbitrary absolute forward reference defined as a non-string.
    BEING_INTERTWINED = ForwardRef(BREATH_AND)

    # Arbitrary fully-qualified name of a hypothetical module.
    OF_DIM_SLEEP = 'In_the.wide.pathless_desert'

    # Arbitrary relative forward reference defined as a string.
    THUS_TREACHEROUSLY = 'Lost_lost_for_ever_lost'

    # ....................{ PASS                           }....................
    # Assert this getter preserves the passed absolute forward reference as is
    # when defined as a string, regardless of whether the second passed object
    # defines the "__module__" dunder attribute.
    assert get_hint_pep484585_ref_name(ALAS_ALAS) is ALAS_ALAS

    # Assert this getter preserves the passed absolute forward reference as is
    # when defined as a non-string, regardless of whether the second passed
    # object defines the "__module__" dunder attribute.
    assert get_hint_pep484585_ref_name(BEING_INTERTWINED) == BREATH_AND

    # If the active Python interpreter targets >= Python 3.9, then this
    # typing.ForwardRef.__init__() method accepts an additional optional
    # "module: Optional[str] = None" parameter preserving the fully-qualified
    # name of the module to which the passed unqualified basename is relative.
    # In this case...
    if IS_PYTHON_AT_LEAST_3_9:
        # Arbitrary relative forward reference defined as a non-string relative
        # to the fully-qualified name of a hypothetical module.
        BEAUTIFUL_SHAPE = ForwardRef(THUS_TREACHEROUSLY, module=OF_DIM_SLEEP)

        # Arbitrary absolute forward reference defined as a non-string relative
        # to the fully-qualified name of a hypothetical module.
        #
        # Note that this exercises an edge case. Technically, passing both an
        # absolute forward reference *AND* a module name is a non-sequitur.
        # Pragmatically, the ForwardRef.__init__() method blindly permits
        # callers to do just that. Ergo, @beartype *MUST* guard against this.
        DARK_GATE_OF_DEATH = ForwardRef(ALAS_ALAS, module=OF_DIM_SLEEP)

        # Assert this getter canonicalizes the passed relative forward reference
        # against the fully-qualified name of the module with which this
        # reference was instantiated when defined as a non-string.
        assert get_hint_pep484585_ref_name(BEAUTIFUL_SHAPE) == (
            f'{OF_DIM_SLEEP}.{THUS_TREACHEROUSLY}')

        # Assert this getter preserves the passed absolute forward reference as
        # is *WITHOUT* canonicalizing this reference against the fully-qualified
        # name of the module with which this reference was instantiated when
        # defined as a non-string.
        assert get_hint_pep484585_ref_name(DARK_GATE_OF_DEATH) == ALAS_ALAS

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed a type hint
    # that is *NOT* a valid forward reference.
    with raises(BeartypeDecorHintForwardRefException):
        get_hint_pep484585_ref_name(
            b'Beyond the realms of dream that fleeting shade;')


def test_get_hint_pep484585_ref_name_relative_to_object() -> None:
    '''
    Test
    :func:`beartype._util.hint.pep.proposal.pep484585.utilpep484585ref.get_hint_pep484585_ref_name_relative_to_object`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintForwardRefException
    from beartype.typing import ForwardRef
    from beartype._util.hint.pep.proposal.pep484585.utilpep484585ref import (
        get_hint_pep484585_ref_name,
        get_hint_pep484585_ref_name_relative_to_object,
    )
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Arbitrary absolute forward reference defined as a string.
    THE_MASK_OF_ANARCHY = 'as_I.lay_asleep.in_Italy'

    # Arbitrary absolute forward reference defined as a non-string.
    WITH_GREAT_POWER = ForwardRef('And_with.great_power.it_forth.led_me')

    # Arbitrary fully-qualified name of a hypothetical module.
    CASTLEREAGH = 'He_had.a_mask.like_Castlereagh'

    # Arbitrary relative forward reference defined as a string.
    VERY_SMOOTH = 'Very_smooth_he_looked_yet_grim'

    # ....................{ CLASSES                        }....................
    class IMetMurderOnTheWay(object):
        '''
        Arbitrary class to be monkey-patched with a well-defined ``__module__``
        dunder attribute below.
        '''

    # Monkey-patch this class with a well-defined "__module__" dunder attribute.
    IMetMurderOnTheWay.__module__ = CASTLEREAGH

    # ....................{ PASS                           }....................
    # Assert this getter preserves the passed absolute forward reference as is
    # when defined as a string, regardless of whether the second passed object
    # defines the "__module__" dunder attribute.
    assert get_hint_pep484585_ref_name_relative_to_object(
        hint=THE_MASK_OF_ANARCHY,
        obj=b'There came a voice from over the Sea,',
    ) is THE_MASK_OF_ANARCHY

    # Assert this getter preserves the passed absolute forward reference as is
    # when defined as a non-string, regardless of whether the second passed
    # object defines the "__module__" dunder attribute.
    assert get_hint_pep484585_ref_name_relative_to_object(
        hint=WITH_GREAT_POWER,
        obj=b'To walk in the visions of Poesy.',
    ) == get_hint_pep484585_ref_name(WITH_GREAT_POWER)

    # Assert this getter canonicalizes the passed relative forward reference
    # against the "__module__" dunder attribute of the second passed object.
    assert get_hint_pep484585_ref_name_relative_to_object(
        hint=VERY_SMOOTH, obj=IMetMurderOnTheWay) == (
        f'{CASTLEREAGH}.{VERY_SMOOTH}')

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed a relative
    # forward reference and the second object does *NOT* define the "__module__"
    # dunder attribute.
    with raises(BeartypeDecorHintForwardRefException):
        get_hint_pep484585_ref_name_relative_to_object(
            hint=VERY_SMOOTH,
            obj='Seven blood-hounds followed him:',
        )
