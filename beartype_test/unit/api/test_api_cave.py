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
from beartype_test.util.mark.pytskip import (
    skip_if_pypy,
    skip_if_python_version_less_than,
    skip_unless_module,
)
from collections import deque
from collections.abc import Iterable
from decimal import Decimal
from enum import Enum
from fractions import Fraction
from pytest import raises

# ....................{ TODO                              }....................
#FIXME: Unit test the following types, which remain untested for the initial
#0.1.0 release due to non-trivialities with asynchronous testing:
#* "AsyncGeneratorCType".
#* "AsyncCoroutineCType".
#* "AsyncCTypes".

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

# Test enumeration class.
class _AsTheDeerBreaksAsTheSteerBreaksFromTheHerdWhereTheyGraze(Enum):
    IN_THE_FAITH_OF_LITTLE_CHILDREN_WE_WENT_ON_OUR_WAYS = 1
    THEN_THE_WOOD_FAILED = 2
    THEN_THE_FOOD_FAILED = 3
    THEN_THE_LAST_WATER_DRIED = 4
    IN_THE_FAITH_OF_LITTLE_CHILDREN_WE_LAY_DOWN_AND_DIED = 5

# ....................{ FUNCTIONS                         }....................
# Test vanilla function.
def _we_were_dreamers_dreaming_greatly_in_the_man_stifled_town(): pass

# Test generator function.
def _we_yearned_beyond_the_sky_line_where_the_strange_roads_go_down(): yield

# ....................{ GLOBALS                           }....................
# Test user-defined class instance.
_LORD_GOD_WE_HA_PAID_IN_FULL = _WeHaveFedOurSeaForAThousandYears()

# Test user-defined Unicode string.
_THE_PHANTOM_RICKSHAW = (
    'More men are killed by overwork '
    'than the importance of the world justifies.'
)

# ....................{ GLOBALS ~ generator               }....................
# Test generator function return type.
_CAME_THE_WHISPER_CAME_THE_VISION_CAME_THE_POWER_WITH_THE_NEED = (
    _we_yearned_beyond_the_sky_line_where_the_strange_roads_go_down())

# Test generator comprehension.
_TILL_THE_SOUL_THAT_IS_NOT_MANS_SOUL_WAS_LENT_US_TO_LEAD = (
    l33t for l33t in range(0x1CEB00DA, 0xC00010FF))

# ....................{ GLOBALS ~ container               }....................
# Test mutable sequence.
_THE_SONG_OF_THE_DEAD = [
    'Hear now the Song of the Dead -- in the North by the torn berg-edges --',
    'They that look still to the Pole, asleep by their hide-stripped sledges.',
    'Song of the Dead in the South -- in the sun by their skeleton horses,',
    'Where the warrigal whimpers and bays through the dust',
    'of the sear river-courses.',
]

# Test mutable mapping.
_EPITAPHS_OF_THE_WAR = {
    'COMMON FORM': (
        'If any question why we died,',
        'Tell them, because our fathers lied.',
    ),
    'A DEAD STATESMAN': (
        'I could not dig: I dared not rob:',
        'Therefore I lied to please the mob.',
        'Now all my lies are proved untrue',
        'And I must face the men I slew.',
        'What tale shall serve me here among',
        'Mine angry and defrauded young?',
    ),
}

# Test double-ended queue.
_RECESSIONAL = deque((
    'For heathen heart that puts her trust',
    '  in reeking tube and iron shard--',
    'All valiant dust that builds on dust,',
    '  and guarding, calls not Thee to guard,',
    'For frantic boast and foolish word--',
    'Thy mercy on Thy People, Lord!',
))

# ....................{ GLOBALS ~ regex                   }....................
# Test regular expression compiled object.
_IN_THE_SAND_DRIFT_ON_THE_VELDT_SIDE_IN_THE_FERN_SCRUB_WE_LAY = re.compile(
    r'\b[Ff]ollow after\b')

# Test regular expression match object.
_THAT_OUR_SONS_MIGHT_FOLLOW_AFTER_BY_THE_BONES_ON_THE_WAY = re.match(
    _IN_THE_SAND_DRIFT_ON_THE_VELDT_SIDE_IN_THE_FERN_SCRUB_WE_LAY,
    'Follow after -- follow after! We have watered the root,')

# ....................{ ASSERTERS                         }....................
def _assert_types_objects(types: Iterable, *objects: object) -> None:
    '''
    Assert all passed objects to be instances of all types contained in the
    passed iterable of such types.

    Parameters
    ----------
    types : Iterable[type]
        Iterable of types to validate these objects to be instances of.
    objects : tuple
        Tuple of all objects to be validated as instances of these types.
    '''

    # Assert that this iterable of types actually is.
    assert isinstance(types, Iterable)

    # For each type in this iterable, assert these objects to all be instances
    # of this type.
    for cls in types:
        _assert_type_objects(cls, *objects)


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

# ....................{ ASSERTERS ~ tuple                 }....................
def _assert_tuples_objects(tuples: Iterable, *objects: object) -> None:
    '''
    Assert all passed objects to be instances of one or more types contained in
    each tuple in the passed iterable of such tuples.

    Parameters
    ----------
    tuples : Iterable[tuples]
        Iterable of tuples of types to validate these objects to be instances
        of.
    objects : tuple
        Tuple of all objects to be validated as instances of these types.
    '''

    # Assert that this iterable of tuples actually is.
    assert isinstance(tuples, Iterable)

    # For each tuple in this iterable, assert these objects to all be instances
    # of one or more types contained in this tuple.
    for types in tuples:
        _assert_tuple_objects(types, *objects)


def _assert_tuple_objects(types: tuple, *objects: object) -> None:
    '''
    Assert all passed objects to be instances of one or more types contained in
    the passed tuple.

    Parameters
    ----------
    types : tuple
        Tuple of types to validate these objects to be instances of.
    objects : tuple
        Tuple of all objects to be validated as instances of these types.
    '''

    # Assert that this tuple actually is.
    assert isinstance(types, tuple)

    # Assert all items of this tuple to be types.
    for cls in types:
        assert isinstance(cls, type)

    # Assert these objects to all be instances of this type.
    for obj in objects:
        assert isinstance(obj, types)

# ....................{ TESTS ~ type                      }....................
def test_api_cave_type_core() -> None:
    '''
    Test all **core simple types** (i.e., types unconditionally published for
    *all* supported Python versions regardless of the importability of optional
    third-party dependencies) published by the :mod:`beartype.cave` submodule.
    '''

    # Defer heavyweight imports. For each simple type published by the beartype
    # cave, assert below that:
    # * This type is a simple type.
    # * An object expected to be of this type is of this type.
    from beartype import cave

    # Test "UnavailableType". By definition, no objects of this type exist;
    # ergo, we only test that this type is actually a type.
    _assert_type_objects(cave.UnavailableType)

    # Test "AnyType".
    _assert_type_objects(cave.AnyType, object())

    # Test "NoneType".
    _assert_type_objects(cave.NoneType, None)

    # Test "ClassType".
    _assert_type_objects(cave.ClassType, _WeHaveFedOurSeaForAThousandYears)

    # Test "FileType".
    with open(__file__, 'r') as (
        by_the_bones_about_the_wayside_ye_shall_come_to_your_own):
        _assert_type_objects(
            cave.FileType,
            by_the_bones_about_the_wayside_ye_shall_come_to_your_own)

    # Test "ModuleType".
    _assert_type_objects(cave.ModuleType, sys.modules[__name__])

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
        _LORD_GOD_WE_HA_PAID_IN_FULL.but_marks_our_english_dead,
    )

    # Test "FunctionOrMethodCType" against an unbound C-based function.
    #
    # Note that testing this type against a bound C-based instance non-dunder
    # method is PyPy-incompatible and *MUST* thus be deferred to the
    # test_api_cave_types_core_nonpypy() unit test.
    _assert_type_objects(cave.FunctionOrMethodCType, id)

    # Test "MethodBoundInstanceOrClassType" against...
    _assert_type_objects(
        cave.MethodBoundInstanceOrClassType,
        # Bound instance method.
        _LORD_GOD_WE_HA_PAID_IN_FULL.and_she_calls_us_still_unfed,
        # Bound class method accessed on a class.
        _WeHaveFedOurSeaForAThousandYears.though_theres_never_a_wave_of_all_her_waves,
        # Bound class method accessed on an instance.
        _LORD_GOD_WE_HA_PAID_IN_FULL.though_theres_never_a_wave_of_all_her_waves,
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

    # Test "GeneratorType" against...
    _assert_type_objects(
        cave.GeneratorType,
        # Generator function return object.
        _CAME_THE_WHISPER_CAME_THE_VISION_CAME_THE_POWER_WITH_THE_NEED,
        # Generator comprehension.
        _TILL_THE_SOUL_THAT_IS_NOT_MANS_SOUL_WAS_LENT_US_TO_LEAD,
    )

    # Test "GeneratorCType".
    _assert_type_objects(
        cave.GeneratorCType,
        _CAME_THE_WHISPER_CAME_THE_VISION_CAME_THE_POWER_WITH_THE_NEED)

    # Test "WeakRefCType" against...
    _assert_type_objects(
        cave.WeakRefCType,
        # Weak non-method reference.
        weakref.ref(_we_were_dreamers_dreaming_greatly_in_the_man_stifled_town),
        # Weak method reference.
        weakref.WeakMethod(
            _LORD_GOD_WE_HA_PAID_IN_FULL.and_she_calls_us_still_unfed),
    )

    # Test "ContainerType", "SizedType", "IterableType", and "SequenceType"
    # against...
    _assert_types_objects(
        {
            cave.ContainerType,
            cave.SizedType,
            cave.IterableType,
            cave.SequenceType,
        },
        # Immutable sequence.
        _EPITAPHS_OF_THE_WAR['COMMON FORM'],
        # Mutable sequence.
        _THE_SONG_OF_THE_DEAD,
        # Double-ended queue.
        _RECESSIONAL,
    )

    # Test "SequenceMutableType" against...
    _assert_type_objects(
        cave.SequenceMutableType,
        # Mutable sequence.
        _THE_SONG_OF_THE_DEAD,
        # Double-ended queue.
        _RECESSIONAL,
    )

    # Test "ContainerType", "MappingType", and "MappingMutableType" against...
    _assert_types_objects(
        {
            cave.ContainerType,
            cave.MappingType,
            cave.MappingMutableType,
        },
        # Mutable mapping.
        _EPITAPHS_OF_THE_WAR,
    )

    # Test "IteratorType".
    _assert_type_objects(cave.IteratorType, iter(_THE_SONG_OF_THE_DEAD))

    # Test "QueueType".
    _assert_type_objects(cave.QueueType, _RECESSIONAL)

    # Test "SetType" against...
    _assert_type_objects(
        cave.SetType,
        # Immutable set.
        frozenset(_THE_SONG_OF_THE_DEAD),
        # Mutable set.
        set(_THE_SONG_OF_THE_DEAD),
    )

    # Test "HashableType".
    _assert_type_objects(cave.HashableType, _THE_SONG_OF_THE_DEAD[0])

    # Test "EnumType".
    _assert_type_objects(
        cave.EnumType,
        _AsTheDeerBreaksAsTheSteerBreaksFromTheHerdWhereTheyGraze)

    # Test "EnumMemberType".
    _assert_type_objects(
        cave.EnumMemberType,
        _AsTheDeerBreaksAsTheSteerBreaksFromTheHerdWhereTheyGraze.THEN_THE_WOOD_FAILED)

    # Test "BoolType."
    _assert_type_objects(cave.BoolType, False, True)

    # Test "StrType".
    _assert_type_objects(cave.StrType, _THE_PHANTOM_RICKSHAW)

    # Test "NumberType", "IntOrFloatType", and ""IntType"
    # against...
    _assert_types_objects(
        {
            cave.NumberType,
            cave.IntOrFloatType,
            cave.IntType,
        },
        # Integer.
        0xCAFED00D,
    )

    # Test "NumberType" and "IntOrFloatType" against...
    _assert_types_objects(
        {
            cave.NumberType,
            cave.IntOrFloatType,
        },
        # Float.
        1.1851851851851851,
        # Stdlib fraction.
        Fraction(32, 27),
    )

    #FIXME: Test builtin complex numbers here as well.
    # Test "NumberType" against...
    _assert_type_objects(
        cave.NumberType,
        # Stdlib decimal, which oddly only satisfies "numbers.Number". *sigh*
        Decimal('0.1428571428571428571428571429'),
    )

    # Test "ArgParserType".
    arg_parser = argparse.ArgumentParser()
    _assert_type_objects(cave.ArgParserType, arg_parser)

    # Test "ArgSubparsersType".
    _assert_type_objects(cave.ArgSubparsersType, arg_parser.add_subparsers())

    # Test "RegexCompiledType".
    _assert_type_objects(
        cave.RegexCompiledType,
        _IN_THE_SAND_DRIFT_ON_THE_VELDT_SIDE_IN_THE_FERN_SCRUB_WE_LAY)

    # Test "RegexMatchType".
    _assert_type_objects(
        cave.RegexMatchType,
        _THAT_OUR_SONS_MIGHT_FOLLOW_AFTER_BY_THE_BONES_ON_THE_WAY)


# ....................{ TESTS ~ type : skip               }....................
@skip_if_pypy()
def test_api_cave_type_core_nonpypy() -> None:
    '''
    Test all core simple types published by the :mod:`beartype.cave` submodule
    requiring the active Python interpreter to *not* be PyPy where this is the
    case *or* reduce to a noop otherwise.
    '''

    # Import this submodule.
    from beartype import cave

    # Test "FunctionOrMethodCType" against a bound C-based instance non-dunder
    # method. Under PyPy, this method is a regular pure-Python bound method.
    _assert_type_objects(
        cave.FunctionOrMethodCType,
        _IN_THE_SAND_DRIFT_ON_THE_VELDT_SIDE_IN_THE_FERN_SCRUB_WE_LAY.sub)


@skip_if_python_version_less_than('3.6.0')
def test_api_cave_type_core_python_3_6_0_or_newer() -> None:
    '''
    Test all core simple types published by the :mod:`beartype.cave` submodule
    requiring the active Python interpreter version to be at least 3.6.0 where
    this is the case *or* reduce to a noop otherwise.
    '''

    # Import this submodule.
    from beartype import cave

    # Test "CollectionType".
    _assert_type_objects(cave.CollectionType, _THE_SONG_OF_THE_DEAD)

# ....................{ TESTS ~ tuple                     }....................
def test_api_cave_tuple_core() -> None:
    '''
    Test all **core tuple types** (i.e., tuples of types unconditionally
    published for *all* supported Python versions regardless of the
    importability of optional third-party dependencies) published by the
    :mod:`beartype.cave` submodule.
    '''

    # Defer heavyweight imports. For each tuple type published by the beartype
    # cave, assert below that:
    # * This tuple contains only simple types.
    # * One or more objects expected to be of one or more types in this tuple
    #   are of these types.
    from beartype import cave

    # Test "UnavailableTypes". By definition, no objects of these types exist;
    # ergo, we only test that this tuple is simply an empty tuple.
    _assert_tuple_objects(cave.UnavailableTypes)
    assert cave.UnavailableTypes == ()

    # Test "ModuleOrStrTypes" against...
    _assert_tuple_objects(
        cave.ModuleOrStrTypes,
        # Module object.
        sys.modules[__name__],
        # Arbitrary string.
        'beartype',
    )

    # Test "TestableTypes" against...
    _assert_tuple_objects(
        cave.TestableTypes,
        # User-defined class.
        _WeHaveFedOurSeaForAThousandYears,
        # Arbitrary tuple.
        _EPITAPHS_OF_THE_WAR['A DEAD STATESMAN'],
    )

    # Tuple of all tuples of types matching at least callable types.
    all_callable_types = (
        cave.CallableTypes,
        cave.CallableOrStrTypes,
        cave.DecoratorTypes,
    )

    # Test "FunctionTypes" and all derived types against...
    _assert_tuples_objects(
        (cave.FunctionTypes,) + all_callable_types,
        # Pure-Python function. Since the test_api_cave_types_core() unit test
        # already exhaustively tests *ALL* possible pure-Python function types,
        # testing only one such type here suffices.
        _we_were_dreamers_dreaming_greatly_in_the_man_stifled_town,
        # C-based builtin function.
        id,
    )

    # Test "MethodBoundTypes" and all derived types against...
    _assert_tuples_objects(
        (cave.MethodBoundTypes, cave.MethodTypes,) + all_callable_types,
        # Bound pure-Python instance method.
        _LORD_GOD_WE_HA_PAID_IN_FULL.and_she_calls_us_still_unfed,
        # Bound C-based instance dunder method.
        ''.__add__,
    )

    # Test "MethodUnboundTypes" and all derived types against...
    _assert_tuples_objects(
        (cave.MethodUnboundTypes, cave.MethodTypes,) + all_callable_types,
        # Unbound class method.
        dict.__dict__['fromkeys'],
        # Unbound C-based instance dunder method.
        str.__add__,
        # Unbound C-based instance non-dunder method.
        str.upper,
    )

    # Test "MethodDecoratorBuiltinTypes" against...
    _assert_tuple_objects(
        cave.MethodDecoratorBuiltinTypes,
        # Unbound class method decorator object.
        _WeHaveFedOurSeaForAThousandYears.__dict__[
            'though_theres_never_a_wave_of_all_her_waves'],
        # Unbound property method decorator object.
        _WeHaveFedOurSeaForAThousandYears.we_have_strawed_our_best_to_the_weeds_unrest,
        # Unbound static method decorator object.
        _WeHaveFedOurSeaForAThousandYears.__dict__[
            'but_marks_our_english_dead'],
    )

    # Test "MethodTypes" against only the following, as prior logic already
    # tested this tuple against all other types of callables...
    _assert_tuple_objects(
        cave.MethodTypes,
        # Bound C-based instance dunder method.
        _IN_THE_SAND_DRIFT_ON_THE_VELDT_SIDE_IN_THE_FERN_SCRUB_WE_LAY.sub,
    )

    # Test "CallableOrStrTypes" against only a string, as prior logic already
    # tested this tuple against all types of callables.
    _assert_tuple_objects(cave.CallableOrStrTypes, 'beartype.beartype')

    # Test "DecoratorTypes" against only a class, as prior logic already
    # tested this tuple against all types of callables.
    _assert_tuple_objects(
        cave.DecoratorTypes, _WeHaveFedOurSeaForAThousandYears)

    # Test "WeakRefProxyCTypes" against...
    _assert_tuple_objects(
        cave.WeakRefProxyCTypes,
        # Callable weak reference proxy.
        weakref.proxy(
            _we_were_dreamers_dreaming_greatly_in_the_man_stifled_town),
        # Uncallable weak reference proxy.
        weakref.proxy(_LORD_GOD_WE_HA_PAID_IN_FULL),
    )

    # Test "BoolOrNumberTypes" against...
    _assert_tuple_objects(
        cave.BoolOrNumberTypes,
        # Boolean.
        True,
        # Integer.
        0xCAFED00D,
        # Float.
        1.1851851851851851,
    )

    # Test "RegexTypes" against...
    _assert_tuple_objects(
        cave.RegexTypes,
        # Compiled regular expression.
        _IN_THE_SAND_DRIFT_ON_THE_VELDT_SIDE_IN_THE_FERN_SCRUB_WE_LAY,
        # Builtin Unicode string.
        _THE_PHANTOM_RICKSHAW,
    )

    # Test "VersionComparableTypes" against...
    _assert_tuple_objects(
        cave.VersionComparableTypes,
        # Tuple-based version specifier.
        (6, 9, 6),
    )


def test_api_cave_tuple_nonetypeor() -> None:
    '''
    Test the **core :class:`beartype.cave.NoneType` tuple factory** (i.e., the
    :class:`beartype.cave.NoneTypeOr` mutable mapping) published by the
    :mod:`beartype.cave` submodule, which is sufficiently distinct from all
    other attributes defined by that submodule to warrant distinct unit tests.
    '''

    # Defer heavyweight imports.
    # from beartype import cave
    from beartype.cave import (
        AnyType, CallableTypes, MappingMutableType, NoneType, NoneTypeOr)
    from beartype.roar import (
        BeartypeCaveNoneTypeOrKeyException,
        BeartypeCaveNoneTypeOrMutabilityException,
    )

    # Assert this factory to be a mutable mapping.
    assert isinstance(NoneTypeOr, MappingMutableType)

    # Assert this factory to be initially empty.
    assert not NoneTypeOr

    # Avoid asserting this factory to be indexable or *NOT* indexable by
    # various types, as the existing test_utilhint_die_unless_hint_nonpep()
    # unit test already exercises these edge cases.
    #
    # Assert this factory to *NOT* be explicitly settable.
    with raises(BeartypeCaveNoneTypeOrMutabilityException):
        NoneTypeOr['If you can meet with'] = 'Triumph and Disaster'

    # Assert that indexing this factory with "NoneType" creates, caches, and
    # returns a tuple containing only "NoneType".
    NoneTypes = NoneTypeOr[NoneType]
    assert NoneTypes == (NoneType,)

    # Assert that indexing this factory with "NoneType" again returns the same
    # tuple implicitly created and cached by the prior indexation.
    assert NoneTypeOr[NoneType] is NoneTypes

    # Assert that indexing this factory with any type *EXCEPT* "NoneType"
    # creates, caches, and returns a new tuple containing that type followed by
    # "NoneType".
    AnyOrNoneTypes = (AnyType, NoneType,)
    assert NoneTypeOr[AnyType] == AnyOrNoneTypes

    # Assert that indexing this factory with a tuple already containing
    # "NoneType" returns the same tuple unmodified.
    assert NoneTypeOr[AnyOrNoneTypes] == AnyOrNoneTypes

    # Assert that indexing this factory with a tuple *NOT* already containing
    # "NoneType" creates, caches, and returns a new tuple containing the types
    # contained in the original tuple followed by "NoneType".
    assert NoneTypeOr[CallableTypes] == CallableTypes + (NoneType,)

# ....................{ TESTS ~ lib                       }....................
@skip_unless_module('numpy')
def test_api_cave_lib_numpy() -> None:
    '''
    Test all core simple types published by the :mod:`beartype.cave` submodule
    against various NumPy objects if the third-party :mod:`numpy` package is
    importable *or* reduce to a noop otherwise.
    '''

    # Defer heavyweight imports.
    import numpy
    from beartype import cave

    # NumPy boolean array prepopulated with NumPy boolean false values.
    array_bool = numpy.ones((6,))

    # NumPy floating-point array prepopulated with an infamous rational series.
    array_float = numpy.asarray((1, 3/2, 7/5, 17/12, 41/29, 99/70))

    # NumPy integer array prepopulated with the GIF header in ASCII code.
    array_int = numpy.asarray((47, 49, 46, 38, 39, 61))

    # NumPy string array prepopulated with Rudyard Kipling, because Truth™.
    array_str = numpy.asarray((
        'I keep six honest serving-men:',
        '(They taught me all I knew)',
        'Their names are What and Where and When',
        'And How and Why and Who.',
    ))

    # Test all container protocols satisfied by NumPy arrays against these
    # specific arrays.
    _assert_types_objects(
        {
            cave.ContainerType,
            cave.SizedType,
            cave.IterableType,
        },
        # NumPy boolean array.
        array_bool,
        # NumPy floating-point array.
        array_float,
        # NumPy integer array.
        array_int,
        # NumPy string array.
        array_str,
    )

    # Test all boolean protocols against items of this boolean arrays.
    _assert_types_objects(
        {
            cave.BoolType,
            cave.NumpyScalarType,
        },
        # NumPy boolean.
        array_bool[0],
    )

    # Test all string protocols against items of this string array.
    _assert_types_objects(
        {
            cave.StrType,
            cave.NumpyScalarType,
        },
        # NumPy Unicode string.
        array_str[0],
    )

    # Test all number protocols satisfied by NumPy numbers against items of
    # these specific arrays.
    _assert_types_objects(
        {
            cave.NumberType,
            cave.IntOrFloatType,
            cave.NumpyScalarType,
        },
        # NumPy floating-point number.
        array_float[0],
    )
    _assert_types_objects(
        {
            cave.NumberType,
            cave.IntOrFloatType,
            cave.IntType,
            cave.NumpyScalarType,
        },
        # NumPy integer.
        array_int[0],
    )

    # Assert all NumPy scalar types to be general-purpose scalar types.
    _assert_tuple_objects(
        cave.ScalarTypes,
        # NumPy boolean.
        array_bool[0],
        # NumPy Unicode string.
        array_str[0],
        # NumPy floating-point number.
        array_float[0],
        # NumPy integer.
        array_int[0],
    )


@skip_unless_module('pkg_resources')
def test_api_cave_lib_setuptools() -> None:
    '''
    Test all core simple types published by the :mod:`beartype.cave` submodule
    against various :mod:`setuptools` objects if that third-party package is
    importable *or* reduce to a noop otherwise.
    '''

    # Defer heavyweight imports.
    #
    # Note that the "packaging" package is available as both a top-level
    # "packaging" package *AND* as the "pkg_resources.extern.packaging"
    # subpackage implicitly called by various "pkg_resources" functions
    # (e.g., pkg_resources.parse_version()). As the latter is generally more
    # stable than the former, we ignore "packaging" entirely and simply call
    # "pkg_resources" functions directly instead.
    import pkg_resources
    from beartype import cave

    # Test "VersionComparableTypes" and "SetuptoolsVersionTypes" against...
    _assert_tuples_objects(
        {
            cave.VersionComparableTypes,
            cave.SetuptoolsVersionTypes,
        },
        # PEP 440-compliant version object.
        pkg_resources.parse_version('6.9.6a'),
        # PEP 440-noncompliant version object.
        pkg_resources.parse_version('6.9.6t'),
    )
