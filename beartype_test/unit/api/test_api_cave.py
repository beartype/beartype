#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype cave API unit tests.**

This submodule unit tests the public API of the :mod:`beartype.cave` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import argparse, functools, re, sys, weakref
from collections import deque

# ....................{ TODO                              }....................
#FIXME: Unit test the following types, which remain untested for the initial
#0.1.0 release due to non-trivialities with asynchronous testing:
#* "AsyncGeneratorCType".
#* "AsyncCoroutineCType".
#* "AsyncCTypes".

# ....................{ GLOBALS                           }....................
_THE_SONG_OF_THE_DEAD = [
    'Hear now the Song of the Dead -- in the North by the torn berg-edges --',
    'They that look still to the Pole, asleep by their hide-stripped sledges.',
    'Song of the Dead in the South -- in the sun by their skeleton horses,',
    'Where the warrigal whimpers and bays through the dust',
    'of the sear river-courses.',
]

# ....................{ FUNCTIONS                         }....................
# Test vanilla function.
def _we_were_dreamers_dreaming_greatly_in_the_man_stifled_town(): pass

# Test generator function.
def _we_yearned_beyond_the_sky_line_where_the_strange_roads_go_down(): yield

# ....................{ CLASSES                           }....................
# Test class defining all possible class-specific callables, including...
class _WeHaveFedOurSeaForAThousandYears(object):
    # Instance method.
    def and_she_calls_us_still_unfed(self): pass

    # Class method.
    @classmethod
    def though_theres_never_a_wave_of_all_her_waves(cls): pass

    # Static method.
    @staticmethod
    def but_marks_our_english_dead(): pass

    # Property getter method.
    @property
    def we_have_strawed_our_best_to_the_weeds_unrest(self): pass

    # Property setter method.
    @we_have_strawed_our_best_to_the_weeds_unrest.setter
    def we_have_strawed_our_best_to_the_weeds_unrest(
        self, to_the_shark_and_the_sheering_gull):
        pass

# ....................{ ASSERTERS                         }....................
def _assert_type_objects(cls: type, *objects: object) -> None:
    '''
    Assert all passed objects to be instances of the passed type.

    Parameters
    ----------
    cls : type
        Type to validate these objects to be instances of.
    objects : tuple
        Tuple of all objects to be validated as instances of this type.
    '''

    # Assert that this type actually is.
    assert isinstance(cls, type)

    # Assert these objects to all be instances of this type.
    for obj in objects:
        assert isinstance(obj, cls)


def _assert_tuple_objects(clses: tuple, *objects: object) -> None:
    '''
    Assert all passed objects to be instances of one or more types contained in
    the passed tuple.

    Parameters
    ----------
    clses : tuple
        Tuple of types to validate these objects to be instances of.
    objects : tuple
        Tuple of all objects to be validated as instances of these types.
    '''

    # Assert that this tuple actually is.
    assert isinstance(clses, tuple)

    # Assert all items of this tuple to be types.
    for cls in clses:
        assert isinstance(cls, type)

    # Assert these objects to all be instances of this type.
    for obj in objects:
        assert isinstance(obj, clses)

# ....................{ TESTS ~ types                     }....................
def test_api_cave_types_core() -> None:
    '''
    Test all **core simple types** (i.e., types unconditionally published for
    *all* supported Python versions regardless of the importability of optional
    third-party dependencies) published by the :mod:`beartype.cave` submodule.
    '''

    # Import this submodule. For each core simple type published by this
    # submodule type, assert below that:
    #
    # * This type is a simple type.
    # * An object expected to be of this type is of this type.
    from beartype import cave

    # Instance of this class.
    lord_god_we_ha_paid_in_full = _WeHaveFedOurSeaForAThousandYears()

    # Test "AnyType".
    _assert_type_objects(cave.AnyType, object())

    # Test "NoneType".
    _assert_type_objects(cave.NoneType, None)

    # Test "ClassType".
    _assert_type_objects(cave.ClassType, _WeHaveFedOurSeaForAThousandYears)

    # Test "UnavailableType". By definition, no objects of this type exist;
    # ergo, we only test that this type is actually a type.
    _assert_type_objects(cave.UnavailableType)

    # Test "FileType".
    with open(__file__, 'r') as (
        by_the_bones_about_the_wayside_ye_shall_come_to_your_own):
        _assert_type_objects(
            cave.FileType,
            by_the_bones_about_the_wayside_ye_shall_come_to_your_own)

    # Test "ModuleType".
    _assert_type_objects(cave.ModuleType, sys.modules[__name__])

    # Test "FunctionOrMethodCType".
    _assert_type_objects(cave.FunctionOrMethodCType, id)

    # Test "CallablePartialType".
    _assert_type_objects(
        cave.CallablePartialType, functools.partial(divmod, 2))

    # Test "FunctionType". Since many types not commonly thought of as
    # functions are ambiguously implemented as functions, explicitly test...
    _assert_type_objects(
        cave.FunctionType,
        # Standard function.
        _we_were_dreamers_dreaming_greatly_in_the_man_stifled_town,
        # Lambda function.
        lambda: None,
        # Unbound instance method.
        _WeHaveFedOurSeaForAThousandYears.and_she_calls_us_still_unfed,
        # Static method accessed on a class.
        _WeHaveFedOurSeaForAThousandYears.but_marks_our_english_dead,
        # Static method accessed on an instance.
        lord_god_we_ha_paid_in_full.but_marks_our_english_dead,
    )

    # Test "MethodBoundInstanceOrClassType". Since instance and class methods
    # types are both ambiguously implemented as bound methods depending on
    # context, explicitly test...
    _assert_type_objects(
        cave.MethodBoundInstanceOrClassType,
        # Bound instance method.
        lord_god_we_ha_paid_in_full.and_she_calls_us_still_unfed,
        # Bound class method accessed on a class.
        _WeHaveFedOurSeaForAThousandYears.though_theres_never_a_wave_of_all_her_waves,
        # Bound class method accessed on an instance.
        lord_god_we_ha_paid_in_full.though_theres_never_a_wave_of_all_her_waves,
    )

    # Test "MethodBoundInstanceDunderCType".
    _assert_type_objects(cave.MethodBoundInstanceDunderCType, ''.__add__)

    # Test "MethodUnboundClassCType".
    _assert_type_objects(
        cave.MethodUnboundClassCType, dict.__dict__['fromkeys'])

    # Test "MethodUnboundInstanceDunderCType".
    _assert_type_objects(cave.MethodUnboundInstanceDunderCType, str.__add__)

    # Test "MethodUnboundInstanceNondunderCType".
    _assert_type_objects(cave.MethodUnboundInstanceNondunderCType, str.upper)

    # Test "MethodDecoratorClassType". Note that instances of this type are
    # *ONLY* accessible with the low-level "object.__dict__" dictionary.
    _assert_type_objects(
        cave.MethodDecoratorClassType,
        _WeHaveFedOurSeaForAThousandYears.__dict__[
            'though_theres_never_a_wave_of_all_her_waves'])

    # Test "MethodDecoratorPropertyType".
    _assert_type_objects(
        cave.MethodDecoratorPropertyType,
        _WeHaveFedOurSeaForAThousandYears.we_have_strawed_our_best_to_the_weeds_unrest)

    # Test "MethodDecoratorStaticType". Note that instances of this type are
    # *ONLY* accessible with the low-level "object.__dict__" dictionary.
    _assert_type_objects(
        cave.MethodDecoratorStaticType,
        _WeHaveFedOurSeaForAThousandYears.__dict__[
            'but_marks_our_english_dead'])

    #FIXME: Also test a class implementing "collections.abc.Generator" by
    #subclassing "_WeHaveFedOurSeaForAThousandYears" from this class and
    #implementing the requisite abstract methods.

    # Test "GeneratorType" by explicitly testing...
    came_the_whisper_came_the_vision_came_the_power_with_the_need = (
        _we_yearned_beyond_the_sky_line_where_the_strange_roads_go_down())
    _assert_type_objects(
        cave.GeneratorType,
        # Generator function return object.
        came_the_whisper_came_the_vision_came_the_power_with_the_need,
        # Generator comprehension.
         (l33t for l33t in range(0x1CEB00DA, 0xC00010FF)),
    )

    # Test "GeneratorCType".
    _assert_type_objects(
        cave.GeneratorCType,
        came_the_whisper_came_the_vision_came_the_power_with_the_need)

    # Test "WeakRefCType" by explicitly testing...
    _assert_type_objects(
        cave.WeakRefCType,
        # Weak non-method references.
        weakref.ref(_we_were_dreamers_dreaming_greatly_in_the_man_stifled_town),
        # Weak method references.
        weakref.WeakMethod(lord_god_we_ha_paid_in_full.and_she_calls_us_still_unfed),
    )

    # Test "IterableType".
    _assert_type_objects(cave.IterableType, _THE_SONG_OF_THE_DEAD)

    # Test "IteratorType".
    _assert_type_objects(cave.IteratorType, iter(_THE_SONG_OF_THE_DEAD))

    # Test "QueueType".
    _assert_type_objects(cave.QueueType, deque(_THE_SONG_OF_THE_DEAD))

    # Test "SetType".
    _assert_type_objects(cave.SetType, set(_THE_SONG_OF_THE_DEAD))

    # Test "SizedType".
    _assert_type_objects(cave.SizedType, _THE_SONG_OF_THE_DEAD)

    # Test "ArgParserType".
    arg_parser = argparse.ArgumentParser()
    _assert_type_objects(cave.ArgParserType, arg_parser)

    # Test "ArgSubparsersType".
    _assert_type_objects(cave.ArgSubparsersType, arg_parser.add_subparsers())

# ....................{ TESTS ~ tuples                    }....................
def test_api_cave_tuples_core() -> None:
    '''
    Test all **core tuple types** (i.e., tuples of types unconditionally
    published for *all* supported Python versions regardless of the
    importability of optional third-party dependencies) published by the
    :mod:`beartype.cave` submodule.
    '''

    # Import this submodule. For each core tuple type published by this
    # submodule type, assert below that:
    #
    # * This tuple contains only simple types.
    # * One or more objects expected to be of one or more types in this tuple
    #   are of these types.
    from beartype import cave

    # Test "UnavailableTypes". By definition, no objects of these types exist;
    # ergo, we only test that this tuple is simply an empty tuple.
    _assert_tuple_objects(cave.UnavailableTypes)
    assert cave.UnavailableTypes == ()
