#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator forward reference unit tests.**

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to both PEP-compliant and -noncompliant **forward reference type hints** (i.e.,
strings whose values are the names of classes and tuples of classes that
typically have yet to be defined).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_pep484_ref_data() -> None:
    '''
    Test successful usage of the :func:`beartype.beartype` decorator with
    respect to both PEP-compliant and -noncompliant forward references by
    importing an external data module declaring these references *before* the
    user-defined classes referred to by these references.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype.roar import (
        BeartypeCallHintParamViolation,
        BeartypeCallHintReturnViolation,
    )
    from beartype_test.a00_unit.data.pep.pep484.data_pep484ref import (
        AllHisBulkAnAgony,
        BeforeTheHurricane,
        TheDarkestEveningOfTheYear,
        WithSluggishSurge,
        a_little_shallop,
        # between_the_woods_and_frozen_lake,
        but_i_have_promises,
        its_fields_of_snow,
        of_easy_wind,
        stopping_by_woods_on,
        the_dry_leaf,
        the_woods_are_lovely,
        winding_among_the_springs,
    )
    from pytest import raises

    # ..................{ LOCALS                             }..................
    # Objects passed below to exercise forward references.
    miles_to_go = TheDarkestEveningOfTheYear('And miles to go before I sleep')
    woods_are_lovely = TheDarkestEveningOfTheYear(
        'The woods are lovely, dark and deep,')
    and_frozen_lake = TheDarkestEveningOfTheYear(
        'Between the woods and frozen lake')
    i_think_i_know = TheDarkestEveningOfTheYear(
        'Whose woods these are I think I know.')
    with_burning_smoke = [
        TheDarkestEveningOfTheYear(
            'With burning smoke, or where bitumen lakes'),
        TheDarkestEveningOfTheYear('On black bare pointed islets ever beat'),
    ]
    rugged_and_dark = WithSluggishSurge()

    # ..................{ PASS                               }..................
    # Assert these forward-referencing callables return the expected values.
    assert a_little_shallop(with_burning_smoke) is with_burning_smoke
    assert but_i_have_promises(miles_to_go) is miles_to_go
    assert of_easy_wind(woods_are_lovely) is woods_are_lovely
    assert stopping_by_woods_on(and_frozen_lake) is and_frozen_lake
    assert the_woods_are_lovely(i_think_i_know) is i_think_i_know
    assert its_fields_of_snow(with_burning_smoke) is with_burning_smoke[0]
    assert the_dry_leaf(TheDarkestEveningOfTheYear) is (
        TheDarkestEveningOfTheYear)
    assert rugged_and_dark.or_where_the_secret_caves() is rugged_and_dark
    assert winding_among_the_springs(rugged_and_dark) is rugged_and_dark

    # ..................{ PASS ~ container                   }..................
    # Assert that instantiating a sequence containing valid items satisfying its
    # annotations raises *NO* type-checking violation.
    crept_gradual = AllHisBulkAnAgony((rugged_and_dark,))

    # Assert that calling various methods of this sequence behave as expected.
    assert crept_gradual[0] is rugged_and_dark
    assert next(iter(crept_gradual)) is rugged_and_dark
    assert tuple(reversed(crept_gradual)) == (rugged_and_dark,)

    # ..................{ FAIL                               }..................
    # Assert that calling a method violating its return annotated as a 2-tuple
    # of type variables whose bounds are expressed as PEP-compliant relative
    # forward references to the same class raises the expected violation.
    with raises(BeartypeCallHintReturnViolation):
        BeforeTheHurricane().in_a_silver_vision_floats()

    # Assert that instantiating a custom sequence containing invalid items
    # violating its annotations raises the expected exception.
    with raises(BeartypeCallHintParamViolation):
        AllHisBulkAnAgony(('Crept gradual, from the feet unto the crown,',))

    #FIXME: Disabled until we decide whether we want to bother trying to
    #resolve nested forward references or not.
    # # ..................{ NESTED                             }..................
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

# ....................{ TESTS ~ pass                       }....................
def test_pep484_ref_arg_pass() -> None:
    '''
    Test successful usage of the :func:`beartype.beartype` decorator for a
    callable passed a parameter annotated with a :pep:`484`-compliant
    fully-qualified forward reference referencing an existing attribute of an
    external module.
    '''

    # ..................{ IMPORTS                            }..................
    # Import this decorator.
    from beartype import beartype

    # ..................{ LOCALS                             }..................
    # Dates between which the Sisters of Battle must have been established.
    ESTABLISHMENT_DATE_MIN = 36000
    ESTABLISHMENT_DATE_MAX = 37000

    # ..................{ FUNCTIONS                          }..................
    # Function to be type-checked.
    @beartype
    def sisters_of_battle(
        leader: str, establishment: 'random.Random') -> int:
        return establishment.randint(
            ESTABLISHMENT_DATE_MIN, ESTABLISHMENT_DATE_MAX)

    # Import the stdlib module referenced above *AFTER* that forward reference.
    from random import Random

    # ..................{ PASS                               }..................
    # Call this function with an instance of the type named above.
    assert sisters_of_battle('Abbess Sanctorum', Random()) in range(
        ESTABLISHMENT_DATE_MIN, ESTABLISHMENT_DATE_MAX + 1)

# ....................{ TESTS ~ fail                       }....................
def test_pep484_ref_decor_fail() -> None:
    '''
    Test unsuccessful decorator-time usage of the :func:`beartype.beartype`
    decorator with respect to both PEP-compliant and -noncompliant forward
    references.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintForwardRefException
    from beartype_test._util.pytroar import raises_uncached

    # ..................{ CALLABLES                          }..................
    def of_oceans(mountainous_waste: 'ToMutualWar'):
        '''
        Arbitrary callable annotated by an **unresolvable relative forward
        reference** (i.e., unqualified name of a user-defined type that is
        *never* defined in either local or global scope).
        '''

        return mountainous_waste

    # Maliciously delete the "__module__" dunder attribute of that callable to
    # exercise an edge case below.
    del of_oceans.__module__

    # ..................{ FAIL                               }..................
    #FIXME: Uncomment if and when a future Python release unconditionally
    #enables some variant of PEP 563... yet again.
    # from beartype.roar import (
    #     BeartypeDecorHintForwardRefException,
    #     BeartypePep563Exception,
    # )
    # from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10
    #
    # # Type of exception raised by @beartype when decorating callables annotated
    # # by syntactically invalid forward reference type hints. Due to ambiguities
    # # in PEP 563 unconditionally enabled under Python >= 3.10, @beartype is
    # # unable to reliably differentiate forward references from non-forward
    # # references and thus treats the former as the latter here.
    # exception_cls = (
    #     BeartypePep563Exception
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

    # Assert @beartype raises the expected exception when decorating a callable
    # annotated by a syntactically valid forward reference type hint when the
    # caller maliciously deletes the "__module__" dunder attribute of that
    # callable *AFTER* defining that callable but before decorating that
    # callable by @beartype.
    with raises_uncached(exception_cls):
        beartype(of_oceans)


def test_pep484_ref_call_fail() -> None:
    '''
    Test unsuccessful call-time usage of the :func:`beartype.beartype`
    decorator with respect to both PEP-compliant and -noncompliant forward
    references.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintForwardRefException
    from beartype.typing import Union
    from beartype_test._util.pytroar import raises_uncached

    # ..................{ FAIL                               }..................
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


def test_pep484_ref_call_arg_fail() -> None:
    '''
    Test unsuccessful call-time usage of the :func:`beartype.beartype`
    decorator for callables passed parameters annotated with PEP-noncompliant
    fully-qualified forward references referencing module attributes exercising
    erroneous edge cases.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import (
        BeartypeCallHintForwardRefException,
        BeartypeCallHintParamViolation,
    )
    from beartype_test._util.pytroar import raises_uncached

    # ..................{ LOCALS                             }..................
    # Dates between which the Black Legion must have been established.
    ESTABLISHMENT_DATE_MIN = 30000
    ESTABLISHMENT_DATE_MAX = 31000

    # ..................{ FUNCTIONS                          }..................
    @beartype
    def black_legion(primarch: str, establishment: 'random.Random') -> int:
        '''
        Arbitrary callable annotated with a forward reference type hint
        referencing an existing class of an importable module.
        '''

        return establishment.randint(
            ESTABLISHMENT_DATE_MIN, ESTABLISHMENT_DATE_MAX)

    @beartype
    def eye_of_terror(
        ocularis_terribus: str,

        # While highly unlikely that a top-level module with this name will
        # ever exist, the possibility cannot be discounted. Since there appears
        # to be no syntactically valid module name prohibited from existing,
        # this is probably the best we can do.
        segmentum_obscurus: '__rand0m__.Warp',
    ) -> str:
        '''
        Arbitrary callable annotated with a forward reference type hint
        referencing a non-existent attribute of a non-existent module.
        '''

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
        navis_nobilite: 'random.Psych1c__L1ght__',
    ) -> str:
        '''
        Arbitrary callable annotated with a forward reference type hint
        referencing a non-existent attribute of an importable module.
        '''

        return astronomicon + navis_nobilite

    # ..................{ FAIL                               }..................
    # Assert call these callables raise the expected exceptions.
    with raises_uncached(BeartypeCallHintParamViolation):
        black_legion('Horus', 'Abaddon the Despoiler')
    with raises_uncached(BeartypeCallHintForwardRefException):
        eye_of_terror('Perturabo', 'Crone Worlds')
    with raises_uncached(BeartypeCallHintForwardRefException):
        navigator('Homo navigo', 'Kartr Hollis')
