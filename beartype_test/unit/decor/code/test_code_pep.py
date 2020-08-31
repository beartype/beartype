#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-compliant type hint unit tests.**

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to **PEP-compliant type hints** (i.e., :mod:`beartype`-agnostic annotations
generically compliant with annotation-centric PEPs).

See Also
----------
:mod:`beartype_test.unit.pep.p484`
    Subpackage specifically unit testing `PEP 484`_-compliant type hints.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.pyterror import raises_uncached
from typing import Any, List, Union

# ....................{ TODO                              }....................

# ....................{ TESTS ~ pass : param : kind       }....................
def test_pep_param_kind_positional_or_keyword_pass() -> None:
    '''
    Test successful usage of the :func:`beartype.beartype` decorator for a
    function call passed non-variadic positional and/or keyword parameters
    annotated with `PEP 484`_-compliant type hints.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Defer heavyweight imports.
    from beartype import beartype

    # Decorated callable to be exercised.
    @beartype
    def special_plan(
        finally_gone: Union[str, List[Any]],
        finally_done: str,
    ) -> Union[bool, int, str]:
        return ''.join(finally_gone) + finally_done

    # Assert that calling this callable with both positional and keyword
    # arguments returns the expected return value.
    assert special_plan(
        ['When everyone ', 'you have ever loved ', 'is finally gone,'],
        finally_done=(
            'When everything you have ever wanted is finally done with,'),
    ) == (
        'When everyone you have ever loved is finally gone,' +
        'When everything you have ever wanted is finally done with,'
    )


def test_pep_param_kind_variadic_and_keyword_only_pass() -> None:
    '''
    Test successful usage of the :func:`beartype.beartype` decorator for a
    function call passed variadic positional parameters followed by a
    keyword-only parameter, all annotated with PEP-compliant type hints.
    '''

    # Defer heavyweight imports.
    from beartype import beartype

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

    # Assert that calling this callable with variadic positional parameters
    # followed by a keyword-only parameter returns the expected return value.
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


def test_pep_param_kind_variadic_fail() -> None:
    '''
    Test unsuccessful usage of the :func:`beartype.beartype` decorator for a
    function call passed variadic positional parameters annotated with
    PEP-compliant type hints.
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallCheckPepException

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
    with raises_uncached(BeartypeCallCheckPepException):
        tongue_tasting_its_savour(
            'One needs to have a plan, someone said',
            'Who was turned away into the shadows',
            'And who I had believed was sleeping or dead',
            ['Imagine, he said, all the flesh that is eaten',],
            'The teeth tearing into it',
            'The tongue tasting its savour',
            teeth_tearing_into_it='And the hunger for that taste')
