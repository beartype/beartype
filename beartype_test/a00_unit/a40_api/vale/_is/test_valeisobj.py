#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype code-based object data validation unit tests.**

This submodule unit tests the subset of the public API of the
:mod:`beartype.vale` subpackage defined by the private
:mod:`beartype.vale._is._valeisobj` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ CONSTANTS                         }....................
AS_WHEN_NIGHT_IS_BARE = (
    "From one lonely cloud",
    "The moon rains out her beams, and Heaven is overflow'd.",
)
'''
Arbitrary tuple to be assigned to an arbitrary instance variable of the
arbitrary class defined below.
'''

# ....................{ CLASSES ~ good                    }....................
class AllTheEarthAndAir(object):
    '''
    Arbitrary class defining an arbitrary attribute whose value has *no*
    accessible attributes but satisfies a validator tested below.
    '''

    def __init__(self) -> None:
        '''
        Initialize this object by defining this attribute.
        '''

        # Initialize this attribute to a shallow copy of this list rather
        # than this list itself to properly test equality comparison.
        self.with_thy_voice_is_loud = AS_WHEN_NIGHT_IS_BARE[:]


class WhatThouArtWeKnowNot(object):
    '''
    Arbitrary class defining an arbitrary attribute whose value is an instance
    of another class defining another arbitrary attribute.
    '''

    def __init__(self) -> None:
        '''
        Initialize this object by defining this attribute.
        '''

        self.what_is_most_like_thee = AllTheEarthAndAir()

# ....................{ CLASSES ~ bad                     }....................
class InAPalaceTower(object):
    '''
    Arbitrary class defining an arbitrary attribute of a differing name as that
    defined by the :class:`AllTheEarthAndAir` class.
    '''

    def __init__(self) -> None:
        '''
        Initialize this object by defining this attribute.
        '''

        self.soothing_her_love_laden = [
            'Soul in secret hour',
            'With music sweet as love, which overflows her bower:',
        ]


class TillTheWorldIsWrought(object):
    '''
    Arbitrary class defining an arbitrary attribute of the same name as that
    defined by the :class:`AllTheEarthAndAir` class whose value has *no*
    accessible attributes and does *not* satisfy a validator tested below.
    '''

    def __init__(self) -> None:
        '''
        Initialize this object by defining this attribute.
        '''

        # Initialize this attribute to an arbitrary list unequal to the value
        # initializing the comparable
        # "AllTheEarthAndAir.with_thy_voice_is_loud" attribute.
        self.with_thy_voice_is_loud = [
            'To sympathy with hopes and fears it heeded not:',
            'As from thy presence showers a rain of melody.',
        ]


class InADellOfDew(object):
    '''
    Arbitrary class defining an arbitrary attribute of the same name as that
    defined by the :class:`WhatThouArtWeKnowNot` class whose value is an
    instance of another class defining an attribute of the same name as that
    defined by the :class:`AllTheEarthAndAir` class whose value does *not*
    satisfy a validator tested below.
    '''

    def __init__(self) -> None:
        '''
        Initialize this object by defining this attribute.
        '''

        self.what_is_most_like_thee = TillTheWorldIsWrought()

# ....................{ TESTS ~ class : isattr            }....................
def test_api_vale_isattr_pass() -> None:
    '''
    Test successful usage of the :mod:`beartype.vale.IsAttr` factory.
    '''

    # Defer test-specific imports.
    from beartype.vale import IsAttr, IsEqual
    from beartype.vale._core._valecore import BeartypeValidator

    # Instances of valid test classes declared above.
    from_rainbow_clouds = AllTheEarthAndAir()
    drops_so_bright_to_see = WhatThouArtWeKnowNot()

    # Instances of invalid test classes declared above.
    like_a_glow_worm_golden = InAPalaceTower()
    like_a_high_born_maiden = TillTheWorldIsWrought()
    scattering_unbeholden = InADellOfDew()

    # Validator produced by subscripting this factory with the name of an
    # attribute defined by the former class and that attribute's value.
    IsInTheLightOfThought = IsAttr[
        'with_thy_voice_is_loud', IsEqual[AS_WHEN_NIGHT_IS_BARE]]

    # Validator produced by subscripting this factory with the name of an
    # attribute defined by the latter class and the prior validator.
    IsSingingHymnsUnbidden = IsAttr[
        'what_is_most_like_thee', IsInTheLightOfThought]

    # Assert these validators satisfy the expected API.
    assert isinstance(IsInTheLightOfThought, BeartypeValidator)
    assert isinstance(IsSingingHymnsUnbidden, BeartypeValidator)

    # Assert these validators produce the same objects when subscripted by the
    # same arguments (and are thus memoized on subscripted arguments).
    assert IsSingingHymnsUnbidden is IsAttr[
        'what_is_most_like_thee', IsInTheLightOfThought]

    # Assert these validators accept objects defining attributes with the same
    # names and values as those subscripting these validators.
    assert IsInTheLightOfThought.is_valid(from_rainbow_clouds) is True
    assert IsSingingHymnsUnbidden.is_valid(drops_so_bright_to_see) is True

    # Assert these validators reject objects defining attributes with differing
    # names to those subscripting these validators.
    assert IsInTheLightOfThought.is_valid(like_a_glow_worm_golden) is False
    assert IsSingingHymnsUnbidden.is_valid(like_a_glow_worm_golden) is False

    # Assert these validators reject objects defining attributes with the same
    # names but differing values to those subscripting these validators.
    assert IsInTheLightOfThought.is_valid(like_a_high_born_maiden) is False
    assert IsSingingHymnsUnbidden.is_valid(scattering_unbeholden) is False

    # Assert these validators have the expected representation.
    IsInTheLightOfThought_repr = repr(IsInTheLightOfThought)
    assert repr('with_thy_voice_is_loud') in IsInTheLightOfThought_repr
    assert repr(AS_WHEN_NIGHT_IS_BARE) in IsInTheLightOfThought_repr

    # Validator synthesized from the above validators with the domain-specific
    # language (DSL) supported by these validators.
    IsInTheLightOfThoughtOrSingingHymnsUnbidden = (
        IsInTheLightOfThought | IsSingingHymnsUnbidden)

    # Assert this object performs the expected validation.
    assert IsInTheLightOfThoughtOrSingingHymnsUnbidden.is_valid(
        AllTheEarthAndAir()) is True
    assert IsInTheLightOfThoughtOrSingingHymnsUnbidden.is_valid(
        WhatThouArtWeKnowNot()) is True
    assert IsInTheLightOfThoughtOrSingingHymnsUnbidden.is_valid(
        InAPalaceTower()) is False
    assert IsInTheLightOfThoughtOrSingingHymnsUnbidden.is_valid(
        TillTheWorldIsWrought()) is False
    assert IsInTheLightOfThoughtOrSingingHymnsUnbidden.is_valid(
        InADellOfDew()) is False

    # Assert this object provides the expected representation.
    assert '|' in repr(IsInTheLightOfThoughtOrSingingHymnsUnbidden)


def test_api_vale_isattr_fail() -> None:
    '''
    Test unsuccessful usage of the :mod:`beartype.vale.IsAttr` factory.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeValeSubscriptionException
    from beartype.vale import IsAttr, IsEqual
    from pytest import raises

    # Assert that subscripting this factory with the empty tuple raises the
    # expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsAttr[()]

    # Assert that subscripting this factory with the empty tuple raises the
    # expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsAttr[()]

    # Assert that subscripting this factory with one non-tuple argument raises
    # the expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsAttr['Among the flowers and grass, which screen it from the view:']

    # Assert that subscripting this factory with three or more arguments raises
    # the expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsAttr[
            "Like a rose embower'd",
            "In its own green leaves,",
            "By warm winds deflower'd,",
        ]

    # Assert that subscripting this factory with two arguments whose first
    # argument is *NOT* a string raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsAttr[
            IsEqual['Till the scent it gives'],
            IsEqual[
                'Makes faint with too much sweet those heavy-winged thieves:']]

    # Assert that subscripting this factory with two arguments whose first
    # argument is the empty string raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsAttr['', IsEqual['Sound of vernal showers']]

    # Assert that subscripting this factory with two arguments whose first
    # argument is an invalid Python identifier raises the expected exception.
    with raises(BeartypeValeSubscriptionException):
        IsAttr['On the twinkling grass,', IsEqual["Rain-awaken'd flowers,"]]
