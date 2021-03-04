#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartypistry unit tests.**

This submodule unit tests the :attr:`beartype._decor._cache.cachetype.bear_typistry`
singleton.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises
from typing import Tuple, Union

# ....................{ TESTS ~ callable : type           }....................
def test_typistry_register_type_pass() -> None:
    '''
    Test successful usage of the
    :func:`beartype._decor._cache.cachetype.register_typistry_type` function.
    '''

    # Defer heavyweight imports.
    from beartype.cave import RegexCompiledType
    from beartype.roar import _BeartypeDecorBeartypistryException
    from beartype._decor._cache.cachetype import register_typistry_type
    from beartype._util.utilobject import get_object_type_basename

    # Assert this function registers a non-builtin type under the beartypistry
    # and silently permits re-registration of the same type.
    for hint in (RegexCompiledType,)*2:
        hint_name_cached = register_typistry_type(hint)
        assert hint_name_cached != get_object_type_basename(hint)
        hint_cached = _eval_registered_expr(hint_name_cached)
        assert hint is hint_cached

    # Assert this function registers the type of the "None" singleton (despite
    # technically being listed as belonging to the "builtin" module) under the
    # beartypistry rather than its unqualified basename "NoneType" (which
    # doesn't actually exist, which is inconsistent nonsense, but whatever).
    hint = type(None)
    hint_name_cached = register_typistry_type(hint)
    assert hint_name_cached != get_object_type_basename(hint)
    hint_cached = _eval_registered_expr(hint_name_cached)
    assert hint is hint_cached

    # Assert this function registers a builtin type under its unqualified
    # basename.
    hint = list
    hint_name_cached = register_typistry_type(hint)
    assert hint_name_cached == get_object_type_basename(hint)
    hint_cached = _eval_registered_expr(hint_name_cached)
    assert hint is hint_cached


def test_typistry_register_type_fail() -> None:
    '''
    Test unsuccessful usage of the
    :func:`beartype._decor._cache.cachetype.register_typistry_type` function.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintTypeException
    from beartype._decor._cache.cachetype import register_typistry_type
    from beartype_test.a00_unit.data.data_type import NonIsinstanceableClass

    # Assert this function raises the expected exception for non-types.
    with raises(BeartypeDecorHintTypeException):
        register_typistry_type((
            'The best lack all conviction, while the worst',
            'Are full of passionate intensity',
        ))

    # Assert this function raises the expected exception for PEP 560-compliant
    # classes whose metaclasses define an __instancecheck__() dunder method to
    # unconditionally raise exceptions.
    with raises(BeartypeDecorHintTypeException):
        register_typistry_type(NonIsinstanceableClass)

# ....................{ TESTS ~ callable : tuple          }....................
def test_typistry_register_tuple_pass() -> None:
    '''
    Test successful usage of the
    :func:`beartype._decor._cache.cachetype.register_typistry_tuple` function.
    '''

    # Defer heavyweight imports.
    from beartype.cave import CallableTypes, NoneTypeOr
    from beartype.roar import _BeartypeDecorBeartypistryException
    from beartype._decor._cache.cachetype import register_typistry_tuple

    # Assert this function registers a tuple and silently permits
    # re-registration of the same tuple.
    #
    # Note that, unlike types, tuples are internally registered under different
    # objects than their originals (e.g., to ignore both duplicates and
    # ordering) and *MUST* thus be tested by conversion to sets.
    # Assert that tuples are registrable via a trivial function call.
    hint = CallableTypes
    hint_cached_expr_1 = register_typistry_tuple(hint)
    hint_cached = _eval_registered_expr(hint_cached_expr_1)
    assert set(hint) == set(hint_cached)
    hint_cached_expr_2 = register_typistry_tuple(hint)
    assert hint_cached_expr_1 == hint_cached_expr_2

    # Assert this function registers tuples of one type as merely that type
    # rather than that tuple.
    hint = (int,)
    hint_cached = _eval_registered_expr(register_typistry_tuple(hint))
    assert hint_cached == int

    # Assert this function registers tuples containing duplicate types as
    # tuples containing only the proper subset of non-duplicate types.
    hint = (str, str, str,)
    hint_cached = _eval_registered_expr(register_typistry_tuple(hint))
    assert hint_cached == (str,)

    # Assert this function registers tuples containing *NO* duplicate types.
    hint = NoneTypeOr[CallableTypes]
    hint_cached = _eval_registered_expr(register_typistry_tuple(hint, True))
    assert hint == hint_cached

    #FIXME: Disable this until we drop Python 3.6 support. While Python >= 3.7
    #preserves insertion order for sets, Python < 3.7 does *NOT*.
    # # Assert that tuples of the same types but in different orders are
    # # registrable via the same function but reduce to differing objects.
    # hint_a = (int, str,)
    # hint_b = (str, int,)
    # hint_cached_a = _eval_registered_expr(register_typistry_tuple(hint_a))
    # hint_cached_b = _eval_registered_expr(register_typistry_tuple(hint_b))
    # assert hint_cached_a != hint_cached_b


def test_typistry_register_tuple_fail() -> None:
    '''
    Test unsuccessful usage of the
    :func:`beartype._decor._cache.cachetype.register_typistry_tuple` function.
    '''

    # Defer heavyweight imports
    from beartype.roar import BeartypeDecorHintNonPepException
    from beartype._decor._cache.cachetype import register_typistry_tuple
    from beartype_test.a00_unit.data.data_type import NonIsinstanceableClass
    from beartype_test.a00_unit.data.hint.pep.proposal.data_hintpep484 import (
        Pep484GenericTypevaredSingle)

    # Assert this function raises the expected exception for unhashable tuples.
    with raises(BeartypeDecorHintNonPepException):
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

    # Assert this function raises the expected exception for non-tuples.
    with raises(BeartypeDecorHintNonPepException):
        register_typistry_tuple('\n'.join((
            'I will arise and go now, and go to Innisfree,',
            'And a small cabin build there, of clay and wattles made;',
            'Nine bean-rows will I have there, a hive for the honey-bee,',
            'And live alone in the bee-loud glade.',
        )))

    # Assert this function raises the expected exception for empty tuples.
    with raises(BeartypeDecorHintNonPepException):
        register_typistry_tuple(())

    # Assert this function raises the expected exception for tuples containing
    # one or more PEP-compliant types.
    with raises(BeartypeDecorHintNonPepException):
        register_typistry_tuple((int, Pep484GenericTypevaredSingle, str,))

    # Assert this function raises the expected exception for tuples containing
    # one or more PEP 560-compliant classes whose metaclasses define an
    # __instancecheck__() dunder method to unconditionally raise exceptions.
    with raises(BeartypeDecorHintNonPepException):
        register_typistry_tuple((bool, NonIsinstanceableClass, float,))

# ....................{ TESTS ~ singleton                 }....................
def test_typistry_singleton_pass() -> None:
    '''
    Test successful usage of the
    :attr:`beartype._decor._cache.cachetype.bear_typistry` singleton.
    '''

    # Defer heavyweight imports.
    from beartype.roar import _BeartypeDecorBeartypistryException
    from beartype._decor._cache.cachetype import bear_typistry
    from beartype._util.utilobject import get_object_type_name

    # Assert that dictionary syntax also implicitly registers a type. Since
    # this approach explicitly prohibits re-registration for safety, we define
    # a custom user-defined type guaranteed *NOT* to have been registered yet.
    class TestTypistrySingletonPassType(object): pass
    hint = TestTypistrySingletonPassType
    hint_name = get_object_type_name(hint)
    bear_typistry[hint_name] = hint
    assert bear_typistry.get(hint_name) is hint

    # Assert that the same type is *NOT* re-registrable via dictionary syntax.
    with raises(_BeartypeDecorBeartypistryException):
        bear_typistry[hint_name] = hint

    # Avoid asserting tuples are also registrable via dictionary syntax. While
    # they technically are, asserting so would require declaring a new
    # get_typistry_tuple_name() function, which would then require refactoring
    # the register_typistry_tuple_from_frozenset() function to call that
    # function, which would reduce performance. Moreover, since those two
    # functions would be operating on different tuple objects, it's unclear
    # whether that refactoring would even be feasible.


def test_typistry_singleton_fail() -> None:
    '''
    Test unsuccessful usage of the
    :attr:`beartype._decor._cache.cachetype.bear_typistry` singleton.
    '''

    # Defer heavyweight imports.
    from beartype.roar import _BeartypeDecorBeartypistryException
    from beartype._decor._cache.cachetype import bear_typistry

    # Assert that keys that are *NOT* strings are *NOT* registrable.
    with raises(_BeartypeDecorBeartypistryException):
        bear_typistry[(
            'And what rough beast, its hour come round at last,',)] = (
            'Slouches towards Bethlehem to be born?',)

    # Assert that forward references are *NOT* registrable.
    with raises(_BeartypeDecorBeartypistryException):
        bear_typistry['Mere.anarchy.is.loosed.upon.the.world'] = (
            'The blood-dimmed tide is loosed, and everywhere')

    # Assert that unhashable objects are *NOT* registrable.
    with raises(_BeartypeDecorBeartypistryException):
        bear_typistry['Turning.and.turning.in.the.widening.gyre'] = {
            'The falcon cannot hear the falconer;': (
                'Things fall apart; the centre cannot hold;'),
        }

    # Assert that arbitrary non-classes are *NOT* registrable.
    with raises(_BeartypeDecorBeartypistryException):
        bear_typistry['The.ceremony.of.innocence.is.drowned'] = 0xDEADBEEF

# ....................{ PRIVATE ~ utility                 }....................
def _eval_registered_expr(hint_expr: str) -> Union[type, Tuple[type, ...]]:
    '''
    Dynamically evaluate the passed Python expression (assumed to be a string
    returned by either the
    :func:`beartype._decor._cache.cachetype.register_typistry_type` or
    :func:`beartype._decor._cache.cachetype.register_typistry_tuple` functions)
    *and* return the resulting value (assumed to either be a type or tuple of
    types).
    '''
    assert isinstance(hint_expr, str), '{repr(hint_expr)} not string.'

    # Defer heavyweight imports.
    from beartype._decor._cache.cachetype import bear_typistry
    from beartype._decor._code.codesnip import ARG_NAME_TYPISTRY

    # Dictionary of all local variables required to evaluate this expression.
    eval_locals = {ARG_NAME_TYPISTRY: bear_typistry}

    # Evaluate this expression under these local variables and return the
    # resulting value.
    return eval(hint_expr, {}, eval_locals)
