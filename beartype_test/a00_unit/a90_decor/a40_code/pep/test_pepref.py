#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator forward reference unit tests.**

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to both PEP-compliant and -noncompliant **forward reference type hints** (i.e.,
strings whose values are the names of classes and tuples of classes that
typically have yet to be defined).
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.pytroar import raises_uncached
from typing import Union

# ....................{ TESTS ~ pass                      }....................
def test_hint_forwardref_data_pass() -> None:
    '''
    Test successful usage of the :func:`beartype.beartype` decorator with
    respect to both PEP-compliant and -noncompliant forward references by
    importing an external data module declaring these references *before* the
    user-defined classes referred to by these references.
    '''

    # Defer heavyweight imports.
    from beartype_test.a00_unit.data.hint.data_hintref import (
        TheDarkestEveningOfTheYear,
        but_i_have_promises,
        of_easy_wind,
        stopping_by_woods_on,
        the_woods_are_lovely,
        # between_the_woods_and_frozen_lake,
    )

    # ..................{ UNNESTED                          }..................
    # Objects passed below to exercise forward references.
    MILES_TO_GO = TheDarkestEveningOfTheYear('And miles to go before I sleep')
    WOODS = TheDarkestEveningOfTheYear('The woods are lovely, dark and deep,')
    LAKE = TheDarkestEveningOfTheYear('Between the woods and frozen lake')
    KNOW = TheDarkestEveningOfTheYear('Whose woods these are I think I know.')

    # Assert these forward-referencing callables return the expected values.
    assert but_i_have_promises(MILES_TO_GO) == MILES_TO_GO
    assert of_easy_wind(WOODS) == WOODS
    assert stopping_by_woods_on(LAKE) == LAKE
    assert the_woods_are_lovely(KNOW) == KNOW

    #FIXME: Disabled until we decide whether we want to bother trying to
    #resolve nested forward references or not.
    # # ..................{ NESTED                            }..................
    # # 3-tuple of closures and classes nested in this callable.
    # (to_stop_without, to_watch_his_woods, WhoseWoodsTheseAreIThinkIKnow) = (
    #     between_the_woods_and_frozen_lake())
    #
    # # Objects passed below to exercise nested forward references.
    # MY_LITTLE_HORSE = WhoseWoodsTheseAreIThinkIKnow(
    #     'My little horse must think it queer')
    # STOP = WhoseWoodsTheseAreIThinkIKnow('To stop without a farmhouse near')
    #
    # # Assert these forward-referencing closures return the expected values.
    # assert to_stop_without(MY_LITTLE_HORSE) == MY_LITTLE_HORSE
    # assert to_watch_his_woods(STOP) == STOP


def test_hint_forwardref_param_pass() -> None:
    '''
    Test successful usage of the :func:`beartype.beartype` decorator for a
    callable passed a parameter annotated with a PEP-noncompliant
    fully-qualified forward reference referencing an existing attribute of an
    external module.
    '''

    # Import this decorator.
    from beartype import beartype

    # Dates between which the Sisters of Battle must have been established.
    ESTABLISHMENT_DATE_MIN = 36000
    ESTABLISHMENT_DATE_MAX = 37000

    # Function to be type-checked.
    @beartype
    def sisters_of_battle(
        leader: str, establishment: 'random.Random') -> int:
        return establishment.randint(
            ESTABLISHMENT_DATE_MIN, ESTABLISHMENT_DATE_MAX)

    # Import the stdlib module referenced above *AFTER* that forward reference.
    from random import Random

    # Call this function with an instance of the type named above.
    assert sisters_of_battle('Abbess Sanctorum', Random()) in range(
        ESTABLISHMENT_DATE_MIN, ESTABLISHMENT_DATE_MAX + 1)

# ....................{ TESTS ~ fail                      }....................
def test_hint_forwardref_decor_fail() -> None:
    '''
    Test unsuccessful decorator-time usage of the :func:`beartype.beartype`
    decorator with respect to both PEP-compliant and -noncompliant forward
    references.
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintForwardRefException

    #FIXME: Uncomment if and when a future Python release unconditionally
    #enables some variant of PEP 563... yet again.
    # from beartype.roar import (
    #     BeartypeDecorHintForwardRefException,
    #     BeartypeDecorHintPep563Exception,
    # )
    # from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10
    #
    # # Type of exception raised by @beartype when decorating callables annotated
    # # by syntactically invalid forward reference type hints. Due to ambiguities
    # # in PEP 563 unconditionally enabled under Python >= 3.10, @beartype is
    # # unable to reliably differentiate forward references from non-forward
    # # references and thus treats the former as the latter here.
    # exception_cls = (
    #     BeartypeDecorHintPep563Exception
    #     if IS_PYTHON_AT_LEAST_3_10 else
    #     BeartypeDecorHintForwardRefException
    # )

    # Type of exception raised by @beartype when decorating callables annotated
    # by syntactically invalid forward reference type hints.
    exception_cls = BeartypeDecorHintForwardRefException

    # Assert @beartype raises the expected exception when decorating a callable
    # annotated by a syntactically invalid forward reference type hint.
    with raises_uncached(exception_cls):
        @beartype
        def linnets_wings(evening_full: (
            "There midnight’s all a glimmer, and noon a purple glow,")):
            return evening_full

    # Assert @beartype raises the expected exception when decorating a callable
    # annotated by a mildly syntactically invalid forward reference type hint.
    with raises_uncached(exception_cls):
        @beartype
        def deep_hearts_core(i_hear_it: (
            'While.I.stand.on.the.roadway.or.on.the.pavements.0grey')):
            return i_hear_it


def test_hint_forwardref_call_fail() -> None:
    '''
    Test unsuccessful call-time usage of the :func:`beartype.beartype`
    decorator with respect to both PEP-compliant and -noncompliant forward
    references.
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintForwardRefException

    # Decorated callable annotated by a PEP-noncompliant fully-qualified
    # forward reference referring to a non-existent type.
    TwoForwardRefsDivergedInAYellowWood = (
        'beartype_test.TwoRoadsDivergedInAYellowWood')
    @beartype
    def the_road(not_taken: TwoForwardRefsDivergedInAYellowWood) -> (
        TwoForwardRefsDivergedInAYellowWood):
        return not_taken

    # Assert calling this callable raises the expected exception.
    with raises_uncached(BeartypeCallHintForwardRefException):
        the_road('Two roads diverged in a wood, and I—')

    # Decorated callable annotated by a PEP-noncompliant tuple containing
    # standard types and a fully-qualified forward reference referring to a
    # non-existent type.
    AndBothForwardRefsThatMorningEquallyLay = (
        complex, TwoForwardRefsDivergedInAYellowWood, bool)
    @beartype
    def in_leaves_no_step(
        had_trodden_black: AndBothForwardRefsThatMorningEquallyLay) -> (
        AndBothForwardRefsThatMorningEquallyLay):
        return had_trodden_black

    # Assert calling this callable raises the expected exception.
    with raises_uncached(BeartypeCallHintForwardRefException):
        in_leaves_no_step('I took the one less traveled by,')

    # Decorated callable annotated by a PEP-compliant unnested unqualified
    # forward reference referring to a non-existent type.
    @beartype
    def yet_knowing_how_way(
        leads_on_to_way: 'OhIKeptTheFirstForAnotherDay') -> (
        'OhIKeptTheFirstForAnotherDay'):
        return leads_on_to_way

    # Assert calling this callable raises the expected exception.
    with raises_uncached(BeartypeCallHintForwardRefException):
        yet_knowing_how_way('And that has made all the difference.')

    # Decorated callable annotated by a PEP-compliant unnested unqualified
    # forward reference referring to a non-existent type.
    IShallBeTellingThisForwardRefWithASigh = Union[
        complex, 'IShallBeTellingThisWithASigh', bytes]
    @beartype
    def somewhere_ages(
        and_ages_hence: IShallBeTellingThisForwardRefWithASigh) -> (
        IShallBeTellingThisForwardRefWithASigh):
        return and_ages_hence

    # Assert calling this callable raises the expected exception.
    with raises_uncached(BeartypeCallHintForwardRefException):
        somewhere_ages('I doubted if I should ever come back.')


def test_hint_forwardref_call_param_fail() -> None:
    '''
    Test unsuccessful call-time usage of the :func:`beartype.beartype`
    decorator for callables passed parameters annotated with PEP-noncompliant
    fully-qualified forward references referencing module attributes exercising
    erroneous edge cases.
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from beartype.roar import (
        BeartypeCallHintForwardRefException,
        BeartypeCallHintParamViolation,
    )

    # Dates between which the Black Legion must have been established.
    ESTABLISHMENT_DATE_MIN = 30000
    ESTABLISHMENT_DATE_MAX = 31000

    # Callable with a forward reference type hint referencing an existing
    # class of an importable module.
    @beartype
    def black_legion(primarch: str, establishment: 'random.Random') -> int:
        return establishment.randint(
            ESTABLISHMENT_DATE_MIN, ESTABLISHMENT_DATE_MAX)

    # Callable with a forward reference type hint referencing a missing
    # attribute of an unimportable module.
    @beartype
    def eye_of_terror(
        ocularis_terribus: str,

        # While highly unlikely that a top-level module with this name will
        # ever exist, the possibility cannot be discounted. Since there appears
        # to be no syntactically valid module name prohibited from existing,
        # this is probably the best we can do.
        segmentum_obscurus: '__rand0m__.Warp',
    ) -> str:
        return ocularis_terribus + segmentum_obscurus

    # Callable with a forward reference type hint referencing a missing
    # attribute of an importable module.
    @beartype
    def navigator(
        astronomicon: str,

        # While highly unlikely that a top-level module attribute with this
        # name will ever exist, the possibility cannot be discounted. Since
        # there appears to be no syntactically valid module attribute name
        # prohibited from existing, this is probably the best we can do.
        navis_nobilite: 'random.__Psych1cL1ght__',
    ) -> str:
        return astronomicon + navis_nobilite

    # Assert call these callables raise the expected exceptions.
    with raises_uncached(BeartypeCallHintParamViolation):
        black_legion('Horus', 'Abaddon the Despoiler')
    with raises_uncached(BeartypeCallHintForwardRefException):
        eye_of_terror('Perturabo', 'Crone Worlds')
    with raises_uncached(BeartypeCallHintForwardRefException):
        navigator('Homo navigo', 'Kartr Hollis')
