#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator parameter kind** unit tests.

This submodule unit tests the :func:`beartype.beartype` decorator with respect
all explicitly supported **parameter kinds** (e.g., keyword-only,
positional-only, variadic positional, variadic keyword).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip

# ....................{ TESTS ~ name                       }....................
def test_decor_arg_name_fail() -> None:
    '''
    Test unsuccessful usage of the :func:`beartype.beartype` decorator for
    callables accepting one or more **decorator-reserved parameters** (i.e.,
    parameters whose names are reserved for internal use by this decorator).
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeDecorParamNameException
    from pytest import raises

    # ....................{ RAISES                         }....................
    # Assert that decorating a callable accepting a reserved parameter name
    # raises the expected exception.
    with raises(BeartypeDecorParamNameException):
        @beartype
        def jokaero(weaponsmith: str, __beartype_func: str) -> str:
            return weaponsmith + __beartype_func

# ....................{ TESTS ~ flexible                   }....................
def test_decor_arg_kind_flex() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on a callable passed two
    **flexible parameters** (i.e., non-variadic positional or keyword
    parameters) annotated with PEP-compliant type hints.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from typing import Union

    # ....................{ CALLABLES                      }....................
    @beartype
    def special_plan(
        finally_gone: Union[list, str],
        finally_done: str,
    ) -> Union[bool, int, str]:
        '''
        Decorated callable to be exercised.
        '''

        return ''.join(finally_gone) + finally_done

    # ....................{ PASSES                         }....................
    # Assert this callable returns the expected value.
    assert special_plan(
        ['When everyone ', 'you have ever loved ', 'is finally gone,'],
        finally_done=(
            'When everything you have ever wanted is finally done with,'),
    ) == (
        'When everyone you have ever loved is finally gone,' +
        'When everything you have ever wanted is finally done with,'
    )


@skip('Currently broken due to known issues in decoration-time type-checking.')
def test_decor_arg_kind_flex_optional() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on a callable passed an
    optional flexible parameter whose default value violates the type hint
    annotating that parameter. Since :func:`beartype.beartype` type-checks
    default values at decoration time (rather than call time as is the common
    case for all other parameter types), this extremely common case warrants
    exhaustive testing.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import (
        BeartypeDecorHintParamDefaultForwardRefWarning,
        BeartypeDecorHintParamDefaultViolation,
    )
    from beartype_test._util.pytroar import raises_uncached
    from pytest import warns

    # ....................{ PASS                           }....................
    # Assert that decorating a callable passed an optional flexible parameter
    # annotated by a forward reference that *CANNOT* be resolved at decoration
    # time emits the expected warning (rather than raising an exception).
    #
    # Note that passing nothing to warns() enables undocumented edge-case
    # behaviour in which warns() captures warnings issued by this block
    # *WITHOUT* validating the types of these warnings. See also:
    #     https://docs.pytest.org/en/4.6.x/warnings.html#recwarn
    with warns() as warnings_info:
        @beartype
        def startled_by(
            # Optional parameter whose default value satisfies its type hint.
            his_own_thoughts: str = (
                'There was no fair fiend near him, not a sight'),
            # Optional parameter whose default value violates its type hint,
            # which is a forward reference that *CANNOT* be resolved at
            # decoration time.
            he_looked_around: 'ThereWasNoFairFiendNearHimNotASight' = (
                'Or sound of awe but in his own deep mind.'),
        ) -> str:
            '''
            Decorated callable to be exercised.
            '''

            return his_own_thoughts + str(he_looked_around)

    # Assert that the above decoration emitted exactly one warning.
    assert len(warnings_info) == 1

    # Warning emitted by the above decoration.
    warning_info = warnings_info[0]

    # Assert that this warning is of the expected type.
    assert warning_info.category is (
        BeartypeDecorHintParamDefaultForwardRefWarning)

    # Warning message.
    warning_message = str(warning_info.message)

    # Assert that this message contains the names of this function, the
    # optional parameter whose default value is uncheckable, and the
    # unresolvable forward reference causing this warning.
    assert 'startled_by' in warning_message
    assert 'he_looked_around' in warning_message
    assert 'ThereWasNoFairFiendNearHimNotASight' in warning_message

    # ....................{ FAIL                           }....................
    # Assert that decorating a callable passed an optional flexible parameter
    # whose default value violates the type hint annotating that parameter
    # raises the expected exception.
    with raises_uncached(BeartypeDecorHintParamDefaultViolation) as (
        exception_info):
        @beartype
        def with_doubtful_smile(
            # Optional parameter whose default value satisfies its type hint.
            mocking_its_own: str = (
                'With doubtful smile mocking its own strange charms.'),
            # Optional parameter whose default value violates its type hint.
            strange_charms: bytes = (
                'Startled by his own thoughts he looked around.'),
        ) -> str:
            '''
            Decorated callable to be exercised.
            '''

            return mocking_its_own + str(strange_charms)

    # Exception message raised by the above decoration of this function.
    exception_message = str(exception_info.value)

    # Assert that this message contains the names of both this function *AND*
    # the optional parameter whose default value violates its type hint.
    assert 'with_doubtful_smile' in exception_message
    assert 'strange_charms' in exception_message


def test_decor_arg_kind_flex_varkw() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on a callable passed a
    mandatory flexible parameter, an optional flexible parameter, and a
    variadic keyword parameter, all annotated with PEP-compliant type hints.

    This test exercises a recent failure in our pre-0.10.0 release cycle:
        https://github.com/beartype/beartype/issues/78
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from typing import Union

    # ....................{ CALLABLES                      }....................
    @beartype
    def one_needs_to_have_a_plan(
        someone_said_who_was_turned: Union[bool, str],
        away_into_the_shadows: Union[float, str] = 'and who i had believed',
        **was_sleeping_or_dead,
    ) -> Union[list, str]:
        '''
        Decorated callable to be exercised.
        '''

        return (
            someone_said_who_was_turned + '\n' +
            away_into_the_shadows + '\n' +
            '\n'.join(was_sleeping_or_dead.values())
        )

    # ....................{ PASS                           }....................
    # Assert this callable returns the expected value.
    assert one_needs_to_have_a_plan(
        someone_said_who_was_turned='imagine he said',
        all_the_flesh_that_is_eaten='the teeth tearing into it',
    ) == '\n'.join((
        'imagine he said',
        'and who i had believed',
        'the teeth tearing into it',
    ))

# ....................{ TESTS ~ keyword                    }....................
def test_decor_arg_kind_kw_unknown_fail() -> None:
    '''
    Test unsuccessful usage of the :func:`beartype.beartype` decorator on
    wrapper functions passed unrecognized keyword parameters.
    '''

    # Defer test-specific imports.
    from beartype import beartype
    from pytest import raises

    @beartype
    def tau(kroot: str, vespid: str) -> str:
        '''
        Decorated callable to be exercised.
        '''

        return kroot + vespid

    # Assert that calling this callable with an unrecognized keyword parameter
    # raises the expected exception.
    with raises(TypeError) as exception:
        tau(kroot='Greater Good', nicassar='Dhow')

    # Assert that this exception's message is that raised by the Python
    # interpreter on calling the decorated callable rather than that raised by
    # the wrapper function on type-checking that callable. This message is
    # currently stable across Python versions and thus robustly testable.
    assert str(exception.value).endswith(
        "tau() got an unexpected keyword argument 'nicassar'")

# ....................{ TESTS ~ variadic                   }....................
def test_decor_arg_kind_variadic() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on a callable exercising edge
    cases with respect to variadic positional and keyword parameters.

    Specifically, that callable:

    * Explicitly accepts multiple annotated flexible and keyword-only
      parameters.
    * Implicitly accepts an arbitrary number of excess positional parameters via
      an annotated variadic keyword parameter.
    * Implicitly accepts an arbitrary number of excess keyword parameters via an
      annotated variadic keyword parameter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from pytest import raises

    # ....................{ CALLABLES                      }....................
    @beartype
    def images(
        # Annotated flexible parameter.
        all_the_woven_boughs: int,
        # Annotated flexible parameter.
        above: bytes,
        *,
        # Annotated keyword-only parameter.
        and_each_depending_leaf: float,
        # Annotated variadic keyword parameter.
        **and_every_speck: str
    ) -> int:
        '''
        Arbitrary callable decorated by :func:`beartype.beartype`, exercising
        edge cases with respect to variadic positional and keyword parameters.
        '''

        return (
            all_the_woven_boughs +
            len(above) +
            int(and_each_depending_leaf) +
            len(and_every_speck)
        )

    # ....................{ PASS                           }....................
    # Assert that this callable returns the expected integer when passed a
    # joyous medley of both explicitly and implicitly accepted parameters whose
    # values all satisfy their type hints.
    assert images(
        # Pass at least one explicit flexible parameter positionally.
        len('Of azure sky, darting between their chasms;'),
        # Pass at least one explicit flexible parameter by keyword.
        above=b'Images all the woven boughs above,',
        # Pass at least one explicit keyword-only parameter.
        and_each_depending_leaf=4.17,
        # Pass at least two implicit excess keyword parameters.
        of_azure_sky='darting between their chasms;',
        nor_aught_else='in the liquid mirror laves',
    ) == 83

    # ....................{ FAIL                           }....................
    # Assert that this callable raises the expected exception when passed a
    # hateful chorus of both explicitly and implicitly accepted parameters, at
    # least one of whose values violates its type hint.
    with raises(BeartypeCallHintParamViolation):
        images(
            # Pass at least one explicit flexible parameter positionally.
            len('And each depending leaf, and every speck'),
            # Pass at least one explicit flexible parameter by keyword.
            above=b'Its portraiture, but some inconstant star',
            # Pass at least one explicit keyword-only parameter.
            and_each_depending_leaf=92.303,
            # Pass at least two implicit excess keyword parameters, only the
            # last of which violates its type hint.
            between_one_foliaged_lattice='twinkling fair',
            or_painted_bird=b'sleeping beneath the moon',
        )

# ....................{ TESTS ~ keyword-only               }....................
# Keyword-only keywords require PEP 3102 compliance, which has thankfully been
# available since Python >= 3.0.

def test_decor_arg_kind_kwonly_mixed() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on a callable passed one
    optional keyword-only parameter and one mandatory keyword-only parameter
    (in that non-standard and quite counter-intuitive order), each annotated
    with PEP-compliant type hints.
    '''

    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintViolation
    from beartype.typing import Union
    from beartype_test._util.pytroar import raises_uncached

    @beartype
    def my_own_special_plan(
        *,
        i_listened_to_these_words: Union[dict, str] = (
            'and yet I did not wonder'),
        if_this_creature: Union[set, str],
    ) -> Union[tuple, str]:
        '''
        Decorated callable to be exercised.
        '''

        return i_listened_to_these_words + '\n' + if_this_creature

    # Assert this function returns the expected value.
    assert my_own_special_plan(
        if_this_creature='whom I had thought sleeping or') == '\n'.join((
        'and yet I did not wonder', 'whom I had thought sleeping or'))

    # Assert that calling this callable with invalid parameters raises the
    # expected exception.
    with raises_uncached(BeartypeCallHintViolation):
        my_own_special_plan(
            if_this_creature=b'dead would ever approach his vision')


def test_decor_arg_kind_flex_varpos_kwonly() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on a callable passed a
    flexible parameter, a variadic positional parameter, and a keyword-only
    parameter, all annotated with PEP-compliant type hints.
    '''

    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintViolation
    from beartype.typing import Union
    from beartype_test._util.pytroar import raises_uncached

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

    # Assert that calling this callable with invalid parameters raises the
    # expected exception.
    with raises_uncached(BeartypeCallHintViolation):
        tongue_tasting_its_savour(
            'One needs to have a plan, someone said',
            'Who was turned away into the shadows',
            'And who I had believed was sleeping or dead',
            ['Imagine, he said, all the flesh that is eaten',],
            'The teeth tearing into it',
            'The tongue tasting its savour',
            teeth_tearing_into_it='And the hunger for that taste')

# ....................{ TESTS ~ pep 570                    }....................
# Positional-only keywords require PEP 570 compliance and thus Python >= 3.8.

def test_decor_arg_kind_posonly() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on a callable passed two
    positional-only parameters annotated with PEP-compliant type hints.
    '''

    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintViolation
    from beartype_test.a00_unit.data.pep.data_pep570 import pep570_posonly
    from beartype_test._util.pytroar import raises_uncached

    # Wrapper function type-checking this unchecked function.
    the_taste_and_the_hunger = beartype(pep570_posonly)

    # Assert this function returns the expected value.
    assert the_taste_and_the_hunger(
        'Take away everything as it is') == '\n'.join((
        'Take away everything as it is', 'and the tongue'))

    # Assert that calling this callable with invalid parameters raises the
    # expected exception.
    with raises_uncached(BeartypeCallHintViolation):
        the_taste_and_the_hunger(b'That was my plan')


def test_decor_arg_kind_posonly_flex_varpos_kwonly() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on a callable passed a
    mandatory positional-only parameter, optional positional-only parameter,
    flexible parameter, variadic positional parameter, and keyword-only
    parameter, all annotated with PEP-compliant type hints.
    '''

    # Defer test-specific imports.
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
