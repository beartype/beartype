#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
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
from beartype_test.util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS                             }....................
def test_arg_kind_flex() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on a callable passed two
    **flexible parameters** (i.e., non-variadic positional or keyword
    parameters) annotated with PEP-compliant type hints.
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


def test_arg_kind_flex_varkw() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on a callable passed a
    mandatory flexible parameter, an optional flexible parameter, and a
    variadic keyword parameter, all annotated with PEP-compliant type hints.

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


def test_arg_kind_flex_varpos_kwonly() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on a callable passed a
    flexible parameter, a variadic positional parameter, and a keyword-only
    parameter, all annotated with PEP-compliant type hints.
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintViolation
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

    # Assert this callable returns the expected value.
    assert tongue_tasting_its_savour(
        'When all of your nightmares are for a time obscured',
        'As by a shining brainless beacon',
        'Or a blinding eclipse of the many terrible shapes of this world,',
        'When you are calm and joyful',
        'And finally entirely alone,',
        'Then in a great new darkness',
        teeth_tearing_into_it='You will finally execute your special plan',
    ) == '\n'.join((
        'When all of your nightmares are for a time obscured',
        'As by a shining brainless beacon',
        'Or a blinding eclipse of the many terrible shapes of this world,',
        'When you are calm and joyful',
        'And finally entirely alone,',
        'Then in a great new darkness',
        'You will finally execute your special plan',
    ))

    # Assert that calling this callable with invalid variadic positional
    # parameters raises the expected exception.
    with raises_uncached(BeartypeCallHintViolation):
        tongue_tasting_its_savour(
            'One needs to have a plan, someone said',
            'Who was turned away into the shadows',
            'And who I had believed was sleeping or dead',
            ['Imagine, he said, all the flesh that is eaten',],
            'The teeth tearing into it',
            'The tongue tasting its savour',
            teeth_tearing_into_it='And the hunger for that taste')


# Positional-only keywords require PEP 570 compliance and thus Python >= 3.8.
@skip_if_python_version_less_than('3.8.0')
def test_arg_kind_posonly_flex_varpos_kwonly() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on a callable passed a
    mandatory positional-only parameter, optional positional-only parameter,
    flexible parameter, variadic positional parameter, and keyword-only
    parameter, all annotated with PEP-compliant type hints.
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from beartype_test.a00_unit.data.pep.data_pep570 import (
        pep570_posonly_flex_varpos_kwonly)

    # Wrapper function type-checking this unchecked function.
    shining_brainless_beacon = beartype(pep570_posonly_flex_varpos_kwonly)

    # Assert this function returns the expected value.
    assert shining_brainless_beacon(
        'When all of your nightmares are for a time obscured',
        'When you are calm and joyful',
        'And finally entirely alone,',
        'Then in a great new darkness',
        your_special_plan='You will finally execute your special plan',
    ) == '\n'.join((
        'When all of your nightmares are for a time obscured',
        'When you are calm and joyful',
        'And finally entirely alone,',
        'Then in a great new darkness',
        'You will finally execute your special plan',
    ))
