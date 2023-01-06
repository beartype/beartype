#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype decorator :pep:`484`-compliant type hint unit tests.

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to :pep:`484`-compliant type hints.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ argument : namedtuple      }....................
def test_decor_pep484_arg_namedtuple() -> None:
    '''
    Test the :func:`beartype.beartype` decorator against all edge cases of
    instances of user-defined subclasses of the :pep:`484`-compliant
    :attr:`typing.NamedTuple` superclass, which are instances rather than types
    and thus invalid as actual type hints.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from typing import (
        NamedTuple,
        Optional,
    )
    from pytest import raises

    # ..................{ LOCALS                             }..................
    @beartype
    class WindsContend(NamedTuple):
        '''
        Arbitrary named tuple type-checked by :func:`beartype.beartype`.
        '''

        starbeams: Optional[str]
        '''
        Standard instance variable passed by the :class:`NamedTuple` metaclass
        to the the implicit ``__new__()`` method synthesized for this subclass.
        '''

    # Arbitrary instance of this named tuple exercising all edge cases.
    dart_through_them = WindsContend(
        starbeams='Or the star-beams dart through them. Winds contend')

    # ..................{ PASS                               }..................
    # Assert this dataclass defines the expected attributes.
    assert dart_through_them.starbeams == (
        'Or the star-beams dart through them. Winds contend')

    # ..................{ FAIL                               }..................
    # Assert that attempting to instantiate an instance of this dataclass with a
    # parameter violating the corresponding type hint annotating the field of
    # the same name raises the expected exception.
    with raises(BeartypeCallHintParamViolation):
        WindsContend(starbeams=0xBABECAFE)

# ....................{ TESTS ~ decor : no_type_check      }....................
def test_decor_pep484_no_type_check() -> None:
    '''
    Test the :func:`beartype.beartype` decorator against all edge cases of the
    :pep:`484`-compliant :attr:`typing.no_type_check` decorator.
    '''

    # Defer test-specific imports.
    from beartype import beartype
    from beartype.typing import (
        Union,
        no_type_check,
    )

    # Callable decorated by @typing.no_type_check whose otherwise PEP-compliant
    # type hints *SHOULD* be subsequently ignored by @beartype.
    @no_type_check
    def of_beechen_green(and_shadows_numberless: Union[int, str]) -> str:
        return and_shadows_numberless

    # The same callable additionally decorated by @beartype.
    of_beechen_green_beartyped = beartype(of_beechen_green)

    # Assert these two callables to be the same, implying @beartype silently
    # reduced to a noop by returning this callable undecorated.
    assert of_beechen_green is of_beechen_green_beartyped

# ....................{ TESTS ~ hint : noreturn            }....................
def test_decor_pep484_hint_noreturn() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on synchronous callables
    against all edge cases of the :pep:`484`-compliant :attr:`typing.NoReturn`
    type hint, which is valid *only* as an unsubscripted return annotation.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import (
        BeartypeCallHintViolation,
        BeartypeDecorHintPep484Exception,
    )
    from beartype.typing import (
        NoReturn,
        Union,
    )
    from beartype_test._util.pytroar import raises_uncached

    # ..................{ LOCALS                             }..................
    # Exception guaranteed to be raised *ONLY* by the mending_wall() function.
    class BeforeIBuiltAWallIdAskToKnow(Exception): pass

    # Synchronous callable unconditionally raising an exception correctly
    # annotating its return as "NoReturn".
    @beartype
    def mending_wall() -> NoReturn:
        raise BeforeIBuiltAWallIdAskToKnow(
            "Something there is that doesn't love a wall,")

    # Callable explicitly returning a value incorrectly annotating its return
    # as "NoReturn".
    @beartype
    def frozen_ground_swell() -> NoReturn:
        return 'That sends the frozen-ground-swell under it,'

    # Callable implicitly returning a value incorrectly annotating its return
    # as "NoReturn".
    @beartype
    def we_do_not_need_the_wall() -> NoReturn:
        'There where it is we do not need the wall:'

    # ..................{ PASS                               }..................
    # Assert this callable raises the expected exception when called.
    with raises_uncached(BeforeIBuiltAWallIdAskToKnow):
        mending_wall()

    # Assert this callable raises the expected exception when called.
    with raises_uncached(BeartypeCallHintViolation):
        frozen_ground_swell()

    # Assert this callable raises the expected exception when called.
    with raises_uncached(BeartypeCallHintViolation):
        we_do_not_need_the_wall()

    # ..................{ FAIL                               }..................
    # Assert this decorator raises the expected exception when decorating a
    # synchronous callable returning a value incorrectly annotating its return
    # as "NoReturn".
    with raises_uncached(BeartypeDecorHintPep484Exception):
        @beartype
        def upper_boulders(in_the_sun: NoReturn):
            return 'And spills the upper boulders in the sun;'

    # Assert this decorator raises the expected exception when decorating a
    # synchronous callable returning a value annotating a parameter as a
    # supported PEP 484-compliant type hint incorrectly subscripted by
    # "NoReturn".
    with raises_uncached(BeartypeDecorHintPep484Exception):
        @beartype
        def makes_gaps(abreast: Union[str, NoReturn]):
            return 'And makes gaps even two can pass abreast.'


async def test_decor_pep484_hint_noreturn_async() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on asynchronous callables
    against all edge cases of the :pep:`484`-compliant :attr:`typing.NoReturn`
    type hint, which is valid *only* as an unsubscripted return annotation.
    '''

    # Defer test-specific imports.
    from beartype import beartype
    from beartype.typing import NoReturn

    # Asynchronous coroutine unconditionally raising an exception correctly
    # annotating its return as "NoReturn".
    @beartype
    async def work_of_hunters(another_thing) -> NoReturn:
        raise ValueError('The work of hunters is another thing:')

# ....................{ TESTS ~ hint : sequence            }....................
def test_decor_pep484_hint_sequence_args_1_cached() -> None:
    '''
    Test that a `subtle issue <issue #5_>`__ of the :func:`beartype.beartype`
    decorator with respect to metadata describing **PEP-compliant standard
    sequence hints** (e.g., :attr:`typing.List`) cached via memoization across
    calls to that decorator has been resolved and *not* regressed.

    Note that the more general-purpose :func:`test_p484` test *should* already
    exercise this issue, but that this issue was sufficiently dire to warrant
    special-purposed testing exercising this exact issue.

    .. _issue #5:
       https://github.com/beartype/beartype/issues/5
    '''

    # Defer test-specific imports.
    from beartype import beartype
    from beartype.typing import Union

    # Callable annotated by an arbitrary PEP 484 standard sequence type hint.
    @beartype
    def fern_hill(prince_of_the_apple_towns: Union[int, str]) -> str:
        return prince_of_the_apple_towns

    # A different callable annotated by the same hint and another arbitrary
    # non-"typing" type hint.
    @beartype
    def apple_boughs(
        famous_among_the_barns: Union[int, str],
        first_spinning_place: str
    ) -> str:
        return famous_among_the_barns + first_spinning_place

    # Validate that these callables behave as expected.
    assert fern_hill(
        'Now as I was young and easy under the apple boughs'
        'About the lilting house and happy as the grass was green,'
        '  The night above the dingle starry,'
        '    Time let me hail and climb'
        '  Golden in the heydays of his eyes,'
        'And honoured among wagons I was prince of the apple towns'
        'And once below a time I lordly had the trees and leaves'
        '    Trail with daisies and barley'
        '  Down the rivers of the windfall light. '
    ).startswith('Now as I was young and easy under the apple boughs')
    assert apple_boughs((
        'And as I was green and carefree, famous among the barns'
        'About the happy yard and singing as the farm was home,'
        '  In the sun that is young once only,'
        '    Time let me play and be'
        '  Golden in the mercy of his means,'
        'And green and golden I was huntsman and herdsman, the calves'
        'Sang to my horn, the foxes on the hills barked clear and cold,'
        '    And the sabbath rang slowly'
        '  In the pebbles of the holy streams.'
    ), 'All the sun long it was running, it was lovely, the hay').startswith(
        'And as I was green and carefree, famous among the barns')

# ....................{ TESTS ~ hint : invalid             }....................
#FIXME: Excise us up. We're unconvinced that arbitrarily prohibiting *ANY*
#isinstanceable classes from being used as type hints is a useful approach --
#even if those classes are "typing" attributes typically intended to be
#instantiated when used as type hints. Nobody's here to tell anybody they can't
#do something that otherwise appears sensible.
#
#When we next read this comment, refactor our test suite as follows:
#* Remove this test.
#* Remove the
#  "beartype_test.a00_unit.data.hint.pep.data_pep.HINTS_PEP_INVALID_TYPE_NONGENERIC"
#  frozen set entirely.

# def test_pep484_hint_invalid_types_nongeneric() -> None:
#     '''
#     Test the :func:`beartype.beartype` decorator against **invalid non-generic
#     classes** (i.e., classes declared by the :mod:`typing` module used to
#     instantiate PEP-compliant type hints but themselves invalid as
#     PEP-compliant type hints).
#     '''
#
#     # Defer test-specific imports.
#     from beartype import beartype
#     from beartype.roar import BeartypeDecorHintPepSignException
#     from beartype_test.a00_unit.data.hint.pep.data_pep import (
#         HINTS_PEP_INVALID_TYPE_NONGENERIC)
#
#     # Assert that decorating a callable annotated by a non-generic class raises
#     # the expected exception.
#     for type_nongeneric in HINTS_PEP_INVALID_TYPE_NONGENERIC:
#         with raises_uncached(BeartypeDecorHintPepSignException):
#             @beartype
#             def childe_roland(to_the_dark_tower_came: type_nongeneric) -> (
#                 type_nongeneric):
#                 raise to_the_dark_tower_came
