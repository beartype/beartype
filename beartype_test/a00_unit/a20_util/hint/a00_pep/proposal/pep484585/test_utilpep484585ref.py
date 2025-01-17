#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484` and :pep:`585` **forward reference type hint utility
unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep484585.pep484585ref` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ getter                     }....................
def test_get_hint_pep484585_ref_names() -> None:
    '''
    Test
    :func:`beartype._util.hint.pep.proposal.pep484585.pep484585ref.get_hint_pep484585_ref_names`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintForwardRefException
    from beartype.typing import ForwardRef
    from beartype._util.hint.pep.proposal.pep484585.pep484585ref import (
        get_hint_pep484585_ref_names)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Arbitrary absolute forward references defined as strings.
    ALAS_ALAS = 'He_overleaps.the.bounds'
    BREATH_AND = 'Were.limbs_and.breath_and'

    # Arbitrary absolute forward reference defined as a non-string.
    BEING_INTERTWINED = ForwardRef(BREATH_AND)

    # Arbitrary fully-qualified names of a hypothetical module.
    OF_DIM_SLEEP = 'In_the.wide.pathless_desert'

    # Arbitrary relative forward reference defined as a string.
    THUS_TREACHEROUSLY = 'Lost_lost_for_ever_lost'

    # ....................{ PASS                           }....................
    # Assert this getter preserves the passed absolute forward reference as is
    # when defined as a string, regardless of whether the second passed object
    # defines the "__module__" dunder attribute.
    assert get_hint_pep484585_ref_names(ALAS_ALAS) == (None, ALAS_ALAS)

    # Assert this getter preserves the passed absolute forward reference as is
    # when defined as a non-string, regardless of whether the second passed
    # object defines the "__module__" dunder attribute.
    assert get_hint_pep484585_ref_names(BEING_INTERTWINED) == (None, BREATH_AND)

    # If the active Python interpreter targets >= Python 3.10, then this
    # typing.ForwardRef.__init__() method accepts an additional optional
    # "module: Optional[str] = None" parameter preserving the fully-qualified
    # names of the module to which the passed unqualified basenames is relative.
    # In this case...
    if IS_PYTHON_AT_LEAST_3_10:
        # Arbitrary relative forward reference defined as a non-string relative
        # to the fully-qualified names of a hypothetical module.
        BEAUTIFUL_SHAPE = ForwardRef(THUS_TREACHEROUSLY, module=OF_DIM_SLEEP)

        # Arbitrary absolute forward reference defined as a non-string relative
        # to the fully-qualified names of a hypothetical module.
        #
        # Note that this exercises an edge case. Technically, passing both an
        # absolute forward reference *AND* a module names is a non-sequitur.
        # Pragmatically, the ForwardRef.__init__() method blindly permits
        # callers to do just that. Ergo, @beartype *MUST* guard against this.
        DARK_GATE_OF_DEATH = ForwardRef(ALAS_ALAS, module=OF_DIM_SLEEP)

        # Assert this getter canonicalizes the passed relative forward reference
        # against the fully-qualified names of the module with which this
        # reference was instantiated when defined as a non-string.
        assert get_hint_pep484585_ref_names(BEAUTIFUL_SHAPE) == (
            OF_DIM_SLEEP, THUS_TREACHEROUSLY)

        # Assert this getter preserves the passed absolute forward reference as
        # is *WITHOUT* canonicalizing this reference against the fully-qualified
        # names of the module with which this reference was instantiated when
        # defined as a non-string.
        assert get_hint_pep484585_ref_names(DARK_GATE_OF_DEATH) == (
            OF_DIM_SLEEP, ALAS_ALAS)

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed a type hint
    # that is *NOT* a valid forward reference.
    with raises(BeartypeDecorHintForwardRefException):
        get_hint_pep484585_ref_names(
            b'Beyond the realms of dream that fleeting shade;')


def test_get_hint_pep484585_ref_names_relative_to() -> None:
    '''
    Test
    :func:`beartype._util.hint.pep.proposal.pep484585.pep484585ref.get_hint_pep484585_ref_names_relative_to`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintForwardRefException
    from beartype.typing import ForwardRef
    from beartype._util.hint.pep.proposal.pep484585.pep484585ref import (
        get_hint_pep484585_ref_names_relative_to)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10
    from beartype_test.a00_unit.data.data_type import (
        ClassModuleNameFake,
        ClassModuleNameNone,
        function_module_name_fake,
        function_module_name_none,
    )
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Fully-qualified name of the current module defining this unit test.
    THIS_MODULE_NAME = __name__

    # Arbitrary absolute forward references defined as strings.
    ALAS_ALAS = 'He_overleaps.the.bounds'
    THE_MASK_OF_ANARCHY = 'as_I.lay_asleep.in_Italy'
    WITH_GREAT_POWER_IT = 'And_with.great_power.it_forth.led_me'

    # Arbitrary absolute forward reference defined as a non-string.
    WITH_GREAT_POWER = ForwardRef(WITH_GREAT_POWER_IT)

    # Arbitrary fully-qualified names of hypothetical modules.
    CASTLEREAGH = 'He_had.a_mask.like_Castlereagh'
    OF_DIM_SLEEP = 'In_the.wide.pathless_desert'

    # Arbitrary relative forward references defined as strings.
    VERY_SMOOTH = 'Very_smooth_he_looked_yet_grim'
    THUS_TREACHEROUSLY = 'Lost_lost_for_ever_lost'

    # ....................{ CALLABLES                      }....................
    def and_pendent_mountains():
        '''
        Arbitrary function whose ``__module__`` dunder attribute is preserved as
        the fully-qualified name of this currently importable module.
        '''

        pass

    # ....................{ CLASSES                        }....................
    class OfRainbowClouds(object):
        '''
        Arbitrary class whose ``__module__`` dunder attribute is preserved as
        the fully-qualified name of this currently importable module.
        '''

        pass

    # ....................{ PASS                           }....................
    # Assert that this getter preserves an absolute forward reference in string
    # format as is.
    assert get_hint_pep484585_ref_names_relative_to(THE_MASK_OF_ANARCHY) == (
        None, THE_MASK_OF_ANARCHY)

    # Assert that this getter preserves an absolute forward reference in
    # "typing.ForwardRef" format as is.
    assert get_hint_pep484585_ref_names_relative_to(WITH_GREAT_POWER) == (
        None, WITH_GREAT_POWER_IT)

    # Assert that this getter canonicalizes a relative forward reference against
    # the "__module__" dunder attribute of a function to the expected string.
    assert get_hint_pep484585_ref_names_relative_to(
        hint=VERY_SMOOTH, func=and_pendent_mountains) == (
        THIS_MODULE_NAME, VERY_SMOOTH)

    # Assert that this getter canonicalizes a relative forward reference against
    # the "__module__" dunder attribute of a type stack to the expected string.
    assert get_hint_pep484585_ref_names_relative_to(
        hint=VERY_SMOOTH,
        cls_stack=[OfRainbowClouds],
        func=and_pendent_mountains,
    ) == (THIS_MODULE_NAME, VERY_SMOOTH)

    # Assert that this getter preserves the passed relative forward reference as
    # is when this reference is the name of a builtin type, even when passed
    # neither a class *NOR* callable.
    assert get_hint_pep484585_ref_names_relative_to('int') == (
        'builtins', 'int')

    # Assert that this getter preserves the passed relative forward reference as
    # is when this reference is the name of a builtin type, even when passed
    # a class and callable both defining the "__module__" dunder attribute to be
    # the fully-qualified names of imaginary and thus unimportable modules that
    # do *NOT* physically exist.
    assert get_hint_pep484585_ref_names_relative_to(
        hint='int',
        cls_stack=(ClassModuleNameFake,),
        func=function_module_name_fake,
    ) == ('builtins', 'int')

    # If the active Python interpreter targets >= Python 3.10, then this
    # typing.ForwardRef.__init__() method accepts an additional optional
    # "module: Optional[str] = None" parameter preserving the fully-qualified
    # name of the module to which the passed unqualified basename is relative.
    # In this case...
    if IS_PYTHON_AT_LEAST_3_10:
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
        # reference was instantiated when defined as a "typing.ForwardRef".
        assert get_hint_pep484585_ref_names_relative_to(BEAUTIFUL_SHAPE) == (
            OF_DIM_SLEEP, THUS_TREACHEROUSLY)

        # Assert this getter preserves the passed absolute forward reference as
        # is *WITHOUT* canonicalizing this reference against the fully-qualified
        # name of the module with which this reference was instantiated when
        # defined as a "typing.ForwardRef".
        assert get_hint_pep484585_ref_names_relative_to(DARK_GATE_OF_DEATH) == (
            OF_DIM_SLEEP, ALAS_ALAS)

    # ....................{ FAIL                           }....................
    # Assert that this getter raises the expected exception when passed a
    # relative forward reference and neither a class *NOR* callable.
    with raises(BeartypeDecorHintForwardRefException):
        get_hint_pep484585_ref_names_relative_to(VERY_SMOOTH)

    # Assert that this getter raises the expected exception when passed a
    # relative forward reference and a class and callable both defining the
    # "__module__" dunder attribute to be the fully-qualified names of imaginary
    # and thus unimportable modules that do *NOT* physically exist.
    with raises(BeartypeDecorHintForwardRefException):
        get_hint_pep484585_ref_names_relative_to(
            hint=VERY_SMOOTH,
            cls_stack=(ClassModuleNameFake,),
            func=function_module_name_fake,
        )

    # Assert that this getter raises the expected exception when passed a
    # relative forward reference and a class and callable both defining the
    # "__module__" dunder attribute to be "None".
    with raises(BeartypeDecorHintForwardRefException):
        get_hint_pep484585_ref_names_relative_to(
            hint=VERY_SMOOTH,
            cls_stack=(ClassModuleNameNone,),
            func=function_module_name_none,
        )

    # Assert that this getter raises the expected exception when passed a
    # relative forward reference and *ONLY* a callable defining the
    # "__module__" dunder attribute to be the fully-qualified name of an
    # imaginary and thus unimportable module that does *NOT* physically exist.
    with raises(BeartypeDecorHintForwardRefException):
        get_hint_pep484585_ref_names_relative_to(
            hint=VERY_SMOOTH, func=function_module_name_fake)

    # Assert that this getter raises the expected exception when passed a
    # relative forward reference and *ONLY* a callable defining the
    # "__module__" dunder attribute to be "None".
    with raises(BeartypeDecorHintForwardRefException):
        get_hint_pep484585_ref_names_relative_to(
            hint=VERY_SMOOTH, func=function_module_name_none)
