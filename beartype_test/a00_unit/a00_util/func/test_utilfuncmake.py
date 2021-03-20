#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Callable creation utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.utilfuncmake` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ GLOBALS                           }....................
# Arbitrary global referenced in functions created below.
AND_SEE_THE_GREAT_ACHILLES = 'whom we knew'

# ....................{ TESTS                             }....................
def test_make_func_pass() -> None:
    '''
    Test successful usage of the
    :func:`beartype._util.func.utilfuncmake.make_func` function.
    '''

    # Defer heavyweight imports.
    from beartype._util.func.utilfuncmake import make_func
    from typing import Optional

    # Arbitrary local referenced in functions created below.
    THO_MUCH_IS_TAKEN = 'much abides; and tho’'

    # Arbitrary callable wrapped by wrappers created below.
    def we_are_not_now_that_strength_which_in_old_days() -> str:
        '''
        One equal temper of heroic hearts,
        '''

        return 'Moved earth and heaven, that which we are, we are;'

    # Arbitrary wrapper accessing both globally and locally scoped attributes,
    # exercising most optional parameters.
    ulysses = make_func(
        name='it_may_be_that_the_gulfs_will_wash_us_down',
        code='''
def it_may_be_that_the_gulfs_will_wash_us_down(
    it_may_be_we_shall_touch_the_happy_isles: Optional[str]) -> str:
    return (
        AND_SEE_THE_GREAT_ACHILLES +
        THO_MUCH_IS_TAKEN +
        we_are_not_now_that_strength_which_in_old_days() +
        (
            it_may_be_we_shall_touch_the_happy_isles or
            'Made weak by time and fate, but strong in will'
        )
    )
''',
        attrs_global={
            'AND_SEE_THE_GREAT_ACHILLES': AND_SEE_THE_GREAT_ACHILLES,
            'THO_MUCH_IS_TAKEN': THO_MUCH_IS_TAKEN,
            'we_are_not_now_that_strength_which_in_old_days': (
                we_are_not_now_that_strength_which_in_old_days),
        },
        attrs_local={
            'Optional': Optional,
        },
        func_wrapped=we_are_not_now_that_strength_which_in_old_days,
    )

    # Assert this wrapper wrapped this wrappee.
    assert ulysses.__doc__ == (
        we_are_not_now_that_strength_which_in_old_days.__doc__)

    # Assert this wrapper returns an expected value.
    odyssey = ulysses('Made weak by time and fate, but strong in will')
    assert 'Made weak by time and fate, but strong in will' in odyssey

    # Arbitrary callable accessing no scoped attributes.
    to_strive_to_seek_to_find = make_func(
        name='to_strive_to_seek_to_find',
        code='''
def to_strive_to_seek_to_find(and_not_to_yield: str) -> str:
    return and_not_to_yield
''',
    )

    # Assert this wrapper returns an expected value.
    assert (
        to_strive_to_seek_to_find('Tis not too late to seek a newer world.') ==
        'Tis not too late to seek a newer world.'
    )


def test_make_func_fail() -> None:
    '''
    Test unsuccessful usage of the
    :func:`beartype._util.func.utilfuncmake.make_func` function.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorWrapperException
    from beartype._util.func.utilfuncmake import make_func

    # Assert that attempting to create a syntactically invalid function raises
    # the expected exception.
    with raises(BeartypeDecorWrapperException):
        make_func(
            name='to_sail_beyond_the_sunset',
            code='''
def to_sail_beyond_the_sunset(and_the_baths: str) -> str:
    Of all the western stars, until I die.
''',
            label='Heroic to_sail_beyond_the_sunset() function',
            code_exception_cls=BeartypeDecorWrapperException,
        )
