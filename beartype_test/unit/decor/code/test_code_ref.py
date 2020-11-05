#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
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
from beartype_test.util.pyterror import raises_uncached
from typing import Union

# ....................{ TESTS                             }....................
def test_hint_ref_pass() -> None:
    '''
    Test successful usage of the :func:`beartype.beartype` decorator with
    respect to both PEP-compliant and -noncompliant forward references.
    '''

    # Import this data submodule, which necessarily sequesters away *ALL* data
    # and assertions exercising successful usage of forward references.
    from beartype_test.unit.data.hint import data_hintref


def test_hint_ref_fail() -> None:
    '''
    Test unsuccessful usage of the :func:`beartype.beartype` decorator with
    respect to both PEP-compliant and -noncompliant forward references.
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallCheckUnavailableTypeException

    # Decorated callable annotated by a PEP-noncompliant fully-qualified
    # forward reference referring to a non-existent type.
    TwoForwardRefsDivergedInAYellowWood = (
        'beartype_test.TwoRoadsDivergedInAYellowWood')
    @beartype
    def the_road(not_taken: TwoForwardRefsDivergedInAYellowWood) -> (
        TwoForwardRefsDivergedInAYellowWood):
        return not_taken

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

    # Decorated callable annotated by a PEP-compliant unnested unqualified
    # forward reference referring to a non-existent type.
    @beartype
    def yet_knowing_how_way(
        leads_on_to_way: 'OhIKeptTheFirstForAnotherDay') -> (
        'OhIKeptTheFirstForAnotherDay'):
        return leads_on_to_way

    # Decorated callable annotated by a PEP-compliant unnested unqualified
    # forward reference referring to a non-existent type.
    IShallBeTellingThisForwardRefWithASigh = Union[
        complex, 'IShallBeTellingThisWithASigh', bytes]
    @beartype
    def somewhere_ages(
        and_ages_hence: IShallBeTellingThisForwardRefWithASigh) -> (
        IShallBeTellingThisForwardRefWithASigh):
        return and_ages_hence

    # Assert calling these callables raise the expected exceptions.
    with raises_uncached(BeartypeCallCheckUnavailableTypeException):
        the_road('Two roads diverged in a wood, and I—')
    with raises_uncached(BeartypeCallCheckUnavailableTypeException):
        in_leaves_no_step('I took the one less traveled by,')
    with raises_uncached(BeartypeCallCheckUnavailableTypeException):
        yet_knowing_how_way('And that has made all the difference.')
    with raises_uncached(BeartypeCallCheckUnavailableTypeException):
        yet_knowing_how_way('And that has made all the difference.')
    with raises_uncached(BeartypeCallCheckUnavailableTypeException):
        somewhere_ages('I doubted if I should ever come back.')
