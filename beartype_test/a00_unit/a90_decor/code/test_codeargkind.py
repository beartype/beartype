#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator parameter kind unit tests.**

This submodule unit tests the :func:`beartype.beartype` decorator with respect
all explicitly supported **parameter kinds** (e.g., keyword-only,
positional-only, variadic positional, variadic keyword).
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ pass : param : kind       }....................
def test_arg_kind_positional_or_keyword_pass() -> None:
    '''
    Test successful usage of the :func:`beartype.beartype` decorator for a
    callable passed non-variadic positional and/or keyword parameters annotated
    with PEP-compliant type hints.
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from typing import Union

    # Decorated callable to be exercised.
    @beartype
    def special_plan(
        finally_gone: Union[list, str],
        finally_done: str,
    ) -> Union[bool, int, str]:
        return ''.join(finally_gone) + finally_done

    # Assert this callable returns the expected value.
    assert special_plan(
        ['When everyone ', 'you have ever loved ', 'is finally gone,'],
        finally_done=(
            'When everything you have ever wanted is finally done with,'),
    ) == (
        'When everyone you have ever loved is finally gone,' +
        'When everything you have ever wanted is finally done with,'
    )


def test_arg_kind_variadic_and_keyword_only_pass() -> None:
    '''
    Test successful usage of the :func:`beartype.beartype` decorator for a
    callable passed a variadic positional parameter followed by a keyword-only
    parameter, all annotated with PEP-compliant type hints.
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from typing import Union

    # Decorated callable to be exercised.
    @beartype
    def shining_brainless_beacon(
        a_time_obscured: Union[bool, str],
        *all_of_your_nightmares: Union[float, str],
        your_special_plan: Union[int, str]
    ) -> Union[list, str]:
        return (
            a_time_obscured + '\n' +
            '\n'.join(all_of_your_nightmares) + '\n' +
            your_special_plan
        )

    # Assert this callable returns the expected value.
    assert shining_brainless_beacon(
        'When all of your nightmares are for a time obscured',
        'As by a shining brainless beacon',
        'Or a blinding eclipse of the many terrible shapes of this world,',
        'When you are calm and joyful',
        'And finally entirely alone,',
        'Then in a great new darkness',
        your_special_plan='You will finally execute your special plan',
    ) == '\n'.join((
        'When all of your nightmares are for a time obscured',
        'As by a shining brainless beacon',
        'Or a blinding eclipse of the many terrible shapes of this world,',
        'When you are calm and joyful',
        'And finally entirely alone,',
        'Then in a great new darkness',
        'You will finally execute your special plan',
    ))


def test_arg_kind_flexible_and_variadic_keyword_pass() -> None:
    '''
    Test successful usage of the :func:`beartype.beartype` decorator for a
    callable passed one or more mandatory flexible parameters, one or more
    optional flexible parameters, and a variadic keyword parameter, all
    annotated with PEP-compliant type hints.

    This test exercises a recent failure in our pre-0.10.0 release cycle:
        https://github.com/beartype/beartype/issues/78
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from typing import Union

    # Decorated callable to be exercised.
    @beartype
    def one_needs_to_have_a_plan(
        someone_said_who_was_turned: Union[bool, str],
        away_into_the_shadows: Union[float, str] = 'and who i had believed',
        **was_sleeping_or_dead,
    ) -> Union[list, str]:
        return (
            someone_said_who_was_turned + '\n' +
            away_into_the_shadows + '\n' +
            '\n'.join(was_sleeping_or_dead.values())
        )

    # Assert this callable returns the expected value.
    assert one_needs_to_have_a_plan(
        someone_said_who_was_turned='imagine he said',
        all_the_flesh_that_is_eaten='the teeth tearing into it',
    ) == '\n'.join((
        'imagine he said',
        'and who i had believed',
        'the teeth tearing into it',
    ))


def test_arg_kind_variadic_fail() -> None:
    '''
    Test unsuccessful usage of the :func:`beartype.beartype` decorator for a
    function call passed a variadic positional parameter annotated with
    PEP-compliant type hints.
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintPepException
    from beartype_test.util.pytroar import raises_uncached
    from typing import Union

    # Decorated callable to be exercised.
    @beartype
    def tongue_tasting_its_savour(
        turned_away_into_the_shadows: Union[dict, str],
        *all_the_flesh_that_is_eaten: Union[frozenset, str],
        teeth_tearing_into_it: Union[set, str]
    ) -> Union[tuple, str]:
        return (
            turned_away_into_the_shadows + '\n' +
            '\n'.join(all_the_flesh_that_is_eaten) + '\n' +
            teeth_tearing_into_it
        )

    # Assert that calling this callable with invalid variadic positional
    # parameters raises the expected exception.
    with raises_uncached(BeartypeCallHintPepException):
        tongue_tasting_its_savour(
            'One needs to have a plan, someone said',
            'Who was turned away into the shadows',
            'And who I had believed was sleeping or dead',
            ['Imagine, he said, all the flesh that is eaten',],
            'The teeth tearing into it',
            'The tongue tasting its savour',
            teeth_tearing_into_it='And the hunger for that taste')
