#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype decorator :pep:`484`-compliant **never** (i.e., :obj:`typing.Never` and
its semantically equivalent alias :obj:`typing.NoReturn`) unit tests.

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to the :pep:`484`-compliant :obj:`typing.Never` and :obj:`typing.NoReturn` type
hint singletons.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_decor_pep484_hint_noreturn() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on synchronous callables
    against all edge cases of the :obj:`typing.Never` and :obj:`typing.NoReturn`
    type hint singletons, which are valid *only* as an unsubscripted return
    annotations.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import (
        BeartypeCallHintViolation,
        BeartypeDecorHintPep484Exception,
    )
    from beartype_test._util.pytroar import raises_uncached
    from beartype._util.api.standard.utiltyping import get_typing_attrs
    from typing import Union

    # ..................{ CLASSES                            }..................
    # Exception guaranteed to be raised *ONLY* by the mending_wall() function.
    class BeforeIBuiltAWallIdAskToKnow(Exception): pass

    # ..................{ FACTORIES                          }..................
    # For each "Never" and "NoReturn" type hint singleton importable from a
    # typing module...
    for Never in get_typing_attrs('Never'):
        # ..................{ CALLABLES                      }..................
        # Synchronous callable unconditionally raising an exception correctly
        # annotating its return as "Never" or "NoReturn".
        @beartype
        def mending_wall() -> Never:
            raise BeforeIBuiltAWallIdAskToKnow(
                "Something there is that doesn't love a wall,")

        # Callable explicitly returning a value incorrectly annotating its
        # return as "Never" or "NoReturn".
        @beartype
        def frozen_ground_swell() -> Never:
            return 'That sends the frozen-ground-swell under it,'

        # Callable implicitly returning a value incorrectly annotating its
        # return as "Never" or "NoReturn".
        @beartype
        def we_do_not_need_the_wall() -> Never:
            'There where it is we do not need the wall:'

        # ..................{ PASS                           }..................
        # Assert this callable raises the expected exception when called.
        with raises_uncached(BeforeIBuiltAWallIdAskToKnow):
            mending_wall()

        # Assert this callable raises the expected exception when called.
        with raises_uncached(BeartypeCallHintViolation):
            frozen_ground_swell()

        # Assert this callable raises the expected exception when called.
        with raises_uncached(BeartypeCallHintViolation):
            we_do_not_need_the_wall()

        # ..................{ FAIL                           }..................
        # Assert this decorator raises the expected exception when decorating a
        # synchronous callable returning a value incorrectly annotating its
        # return as "Never" or "NoReturn".
        with raises_uncached(BeartypeDecorHintPep484Exception):
            @beartype
            def upper_boulders(in_the_sun: Never):
                return 'And spills the upper boulders in the sun;'

        # Assert this decorator raises the expected exception when decorating a
        # synchronous callable returning a value annotating a parameter as a
        # supported PEP 484-compliant type hint incorrectly subscripted by
        # "Never" or "NoReturn".
        with raises_uncached(BeartypeDecorHintPep484Exception):
            @beartype
            def makes_gaps(abreast: Union[str, Never]):
                return 'And makes gaps even two can pass abreast.'


async def test_decor_pep484_hint_noreturn_async() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on asynchronous callables
    against all edge cases of the :pep:`484`-compliant :obj:`typing.Never` and
    :obj:`typing.NoReturn` type hint singletons, which are valid *only* as an
    unsubscripted return annotations.
    '''

    # Defer test-specific imports.
    from beartype import beartype
    from beartype._util.api.standard.utiltyping import get_typing_attrs

    # For each "Never" and "NoReturn" type hint singleton importable from a
    # typing module...
    for Never in get_typing_attrs('Never'):
        # Asynchronous coroutine unconditionally raising an exception correctly
        # annotating its return as "Never" or "NoReturn".
        @beartype
        async def work_of_hunters(another_thing) -> Never:
            raise ValueError('The work of hunters is another thing:')
