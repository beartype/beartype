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

import argparse, functools, sys

# ....................{ ASSERTERS                         }....................
def _assert_objects_type(cls: type, *objects: object) -> None:
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


def _assert_tuple(types: tuple) -> None:
    '''
    Assert each item of the passed tuple to be a type.

    Parameters
    ----------
    types : tuple
        Tuple of arbitrary objects to be validated.
    '''

    # Assert that this tuple actually is.
    assert isinstance(types, tuple)

    # Assert that each item of this tuple is a type.
    for item in types:
        assert isinstance(item, type)

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

    # Class defining all possible class-specific callables, including...
    class WeHaveFedOurSeaForAThousandYears(object):
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

    # Instance of this class.
    lord_god_we_ha_paid_in_full = WeHaveFedOurSeaForAThousandYears()

    # Test "AnyType".
    _assert_objects_type(cave.AnyType, object())

    # Test "NoneType".
    _assert_objects_type(cave.NoneType, None)

    # Test "ClassType".
    _assert_objects_type(cave.ClassType, WeHaveFedOurSeaForAThousandYears)

    # Test "UnavailableType". By definition, no objects of this type exist;
    # ergo, we only test that this type is actually a type.
    _assert_objects_type(cave.UnavailableType)

    # Test "FileType".
    with open(__file__, 'r') as (
        by_the_bones_about_the_wayside_ye_shall_come_to_your_own):
        _assert_objects_type(
            cave.FileType,
            by_the_bones_about_the_wayside_ye_shall_come_to_your_own)

    # Test "ModuleType".
    _assert_objects_type(cave.ModuleType, sys.modules[__name__])

    # Test "CallableCType".
    _assert_objects_type(cave.CallableCType, id)

    # Test "CallablePartialType".
    _assert_objects_type(
        cave.CallablePartialType, functools.partial(divmod, 2))

    # Test "FunctionType". Since many types not commonly thought of as
    # functions are ambiguously implemented as functions, explicitly test...
    def we_were_dreamers_dreaming_greatly_in_the_man_stifled_town(): pass
    _assert_objects_type(
        cave.FunctionType,
        # Standard function.
        we_were_dreamers_dreaming_greatly_in_the_man_stifled_town,
        # Lambda function.
        lambda: None,
        # Unbound instance method.
        WeHaveFedOurSeaForAThousandYears.and_she_calls_us_still_unfed,
        # Static method accessed on a class.
        WeHaveFedOurSeaForAThousandYears.but_marks_our_english_dead,
        # Static method accessed on an instance.
             lord_god_we_ha_paid_in_full.but_marks_our_english_dead,
    )

    # Test "MethodBoundInstanceOrClassType". Since instance and class methods
    # types are both ambiguously implemented as bound methods depending on
    # context, explicitly test...
    _assert_objects_type(
        cave.MethodBoundInstanceOrClassType,
        # Bound instance method.
        lord_god_we_ha_paid_in_full.and_she_calls_us_still_unfed,
        # Bound class method accessed on a class.
        WeHaveFedOurSeaForAThousandYears.though_theres_never_a_wave_of_all_her_waves,
        # Bound class method accessed on an instance.
             lord_god_we_ha_paid_in_full.though_theres_never_a_wave_of_all_her_waves,
        )

    # Test "ArgParserType".
    arg_parser = argparse.ArgumentParser()
    _assert_objects_type(cave.ArgParserType, arg_parser)

    # Test "ArgSubparsersType".
    _assert_objects_type(cave.ArgSubparsersType, arg_parser.add_subparsers())

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

    # Test "UnavailableTypes".
    _assert_tuple(cave.UnavailableTypes)
    assert cave.UnavailableTypes == ()
