#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype decorator :pep:`484`- and :pep:`585`-compliant unit tests.

This submodule unit tests :pep:`484` and :pep:`585` support implemented in the
:func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning
from beartype_test._util.mark.pytmark import ignore_warnings

# ....................{ TESTS ~ decor : async              }....................
# Prevent pytest from capturing and displaying all expected non-fatal
# beartype-specific warnings emitted by the @beartype decorator below. Urgh!
@ignore_warnings(BeartypeDecorHintPep585DeprecationWarning)
async def test_decor_async_coroutine() -> None:
    '''
    Test decorating coroutines with the :func:`beartype.beartype` decorator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from asyncio import sleep
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintPep585Exception
    from beartype_test._util.pytroar import raises_uncached
    from collections.abc import Coroutine as Pep585Coroutine
    from typing import Union, Coroutine as Pep484Coroutine

    # ....................{ CALLABLES                      }....................
    @beartype
    async def control_the_car(
        said_the: Union[str, int],
        biggest_greenest_bat: Union[str, float],
    ) -> Union[str, float]:
        '''
        Decorated coroutine whose return is annotated with an arbitrary
        PEP-compliant type hint.
        '''

        await sleep(0)
        return said_the + biggest_greenest_bat


    @beartype
    async def universal_love(
        said_the: Union[str, int], cactus_person: Union[str, float]) -> (
        Pep484Coroutine[None, None, Union[str, float]]):
        '''
        Decorated coroutine whose return is annotated with a
        :pep:`484`-compliant coroutine type hint.
        '''

        await sleep(0)
        return said_the + cactus_person


    @beartype
    async def transcendent_joy(
        said_the: Union[str, float], big_green_bat: Union[str, int]) -> (
        Pep585Coroutine[None, None, Union[str, float]]):
        '''
        Decorated coroutine whose return is annotated with a
        :pep:`585`-compliant coroutine type hint.
        '''

        await sleep(0)
        return said_the + big_green_bat

    # ....................{ PASS                           }....................
    # Assert awaiting this coroutine returns the expected value.
    assert await control_the_car(
        'I saw the big green bat bat a green big eye. ',
        'Suddenly I knew I had gone too far.') == (
        'I saw the big green bat bat a green big eye. '
        'Suddenly I knew I had gone too far.')

    # Assert awaiting this coroutine returns the expected value.
    assert await universal_love(
        'The sea was made of strontium; ', 'the beach was made of rye.') == (
        'The sea was made of strontium; the beach was made of rye.')

    # Assert awaiting this coroutine returns the expected value.
    assert await transcendent_joy(
        'A thousand stars of sertraline ',
        'whirled round quetiapine moons'
    ) == 'A thousand stars of sertraline whirled round quetiapine moons'

    # ....................{ FAIL                           }....................
    # Assert @beartype raises the expected exception when decorating a coroutine
    # whose return is annotated with a PEP 585-compliant coroutine type hint
    # *NOT* subscripted by exactly three child hints.
    with raises_uncached(BeartypeDecorHintPep585Exception):
        @beartype
        async def with_each_planck_moment_ever_fit() -> (
            Pep585Coroutine['to be eternally enjoyed']):
            await sleep(0)
            return 'Time will decay us but time can be left blank'


# Prevent pytest from capturing and displaying all expected non-fatal
# beartype-specific warnings emitted by the @beartype decorator below. Hurk!
@ignore_warnings(BeartypeDecorHintPep585DeprecationWarning)
async def test_decor_async_generator() -> None:
    '''
    Test decorating asynchronous generators with the :func:`beartype.beartype`
    decorator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from asyncio import sleep
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintPep484585Exception
    from beartype_test._util.pytroar import raises_uncached
    from beartype.typing import (
        AsyncGenerator as AsyncGeneratorUnsubscripted,
    )
    from collections.abc import (
        AsyncGenerator as Pep585AsyncGenerator,
        AsyncIterable as Pep585AsyncIterable,
        AsyncIterator as Pep585AsyncIterator,
    )
    from typing import (
        Union,
        AsyncGenerator as Pep484AsyncGenerator,
        AsyncIterable as Pep484AsyncIterable,
        AsyncIterator as Pep484AsyncIterator,
    )

    # ....................{ LOCALS                         }....................
    # Tuple of all PEP 484- or 585-compliant type hints annotating the returns
    # of asynchronous generators -- exercising all possible edge cases.
    HINTS_RETURN = (
        # ....................{ NON-PEP                    }....................
        AsyncGeneratorUnsubscripted,

        # ....................{ PEP 484                    }....................
        Pep484AsyncGenerator[Union[str, float], None],
        Pep484AsyncIterable[Union[str, float]],
        Pep484AsyncIterator[Union[str, float]],

        # ....................{ PEP 585                    }....................
        Pep585AsyncGenerator[Union[str, float], None],
        Pep585AsyncIterable[Union[str, float]],
        Pep585AsyncIterator[Union[str, float]],
    )

    # ....................{ PASS                           }....................
    # For each return type hint defined above...
    for hint_return in HINTS_RETURN:
        @beartype
        async def some_kind_of_spiritual_thing(
            said_the: Union[str, int], bigger_greener_bat: Union[str, float]
        ) -> hint_return:
            '''
            :func:`beartype.beartype`-decorated asynchronous generator whose
            return is annotated by a :pep:`484`- or :pep:`585`-compliant type
            hint deeply type-checking the value yielded by this generator.
            '''

            await sleep(0)
            yield said_the + bigger_greener_bat

        # Assert awaiting this asynchronous generator returns the expected
        # value. Unlike synchronous generators, asynchronous generators are
        # *NOT* actually iterators and thus have *NO* clean analogue to the
        # iter() and next() builtins. The closest approximation is this rather
        # unclean hack:
        #     await not_splitting_number.__anext__()
        #
        # See also this relevant StackOvelflow post:
        #     https://stackoverflow.com/a/42561322/2809027
        async for some_kind_of_spiritual in some_kind_of_spiritual_thing(
            'I should be trying to do some kind of spiritual thing ',
            'involving radical acceptance and enlightenment and such.',
        ):
            assert some_kind_of_spiritual == (
                'I should be trying to do some kind of spiritual thing '
                'involving radical acceptance and enlightenment and such.'
            )

    # ....................{ FAIL                           }....................
    # Assert this decorator raises the expected exception when decorating an
    # asynchronous generator annotating its return as anything *EXCEPT*
    # "AsyncGenerator[...]", "AsyncIterable[...]", or "AsyncIterator[...]".
    with raises_uncached(BeartypeDecorHintPep484585Exception):
        @beartype
        async def upside_down_trees(
            roots_in_the_breeze: str, branches_underground: str) -> str:
            await sleep(0)
            yield roots_in_the_breeze + branches_underground

# ....................{ TESTS ~ decor : sync               }....................
# Prevent pytest from capturing and displaying all expected non-fatal
# beartype-specific warnings emitted by the @beartype decorator below. Blargh!
@ignore_warnings(BeartypeDecorHintPep585DeprecationWarning)
def test_decor_sync_generator() -> None:
    '''
    Test decorating synchronous generators with the :func:`beartype.beartype`
    decorator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintPep484585Exception
    from beartype_test._util.pytroar import raises_uncached
    from beartype.typing import (
        Generator as GeneratorUnsubscripted,
    )
    from collections.abc import (
        Generator as Pep585Generator,
        Iterable as Pep585Iterable,
        Iterator as Pep585Iterator,
    )
    from typing import (
        Union,
        Generator as Pep484Generator,
        Iterable as Pep484Iterable,
        Iterator as Pep484Iterator,
    )

    # ....................{ LOCALS                         }....................
    # Tuple of all PEP 484- or 585-compliant type hints annotating the returns
    # of ynchronous generators -- exercising all possible edge cases.
    HINTS_RETURN = (
        # ....................{ NON-PEP                    }....................
        GeneratorUnsubscripted,

        # ....................{ PEP 484                    }....................
        Pep484Generator[Union[str, float], None, None],
        Pep484Iterable[Union[str, float]],
        Pep484Iterator[Union[str, float]],

        # ....................{ PEP 585                    }....................
        Pep585Generator[Union[str, float], None, None],
        Pep585Iterable[Union[str, float]],
        Pep585Iterator[Union[str, float]],
    )

    # ....................{ PASS                           }....................
    # For each return type hint defined above...
    for hint_return in HINTS_RETURN:
        @beartype
        def western_logocentric_stuff(
            said_the: Union[str, int], bigger_greener_bat: Union[str, float]
        ) -> hint_return:
            '''
            :func:`beartype.beartype`-decorated synchronous generator whose
            return is annotated by a :pep:`484`- or :pep:`585`-compliant type
            hint deeply type-checking the value yielded by this generator.
            '''

            yield said_the + bigger_greener_bat

        # Assert awaiting this synchronous generator yields the expected value
        # when iterated.
        assert next(western_logocentric_stuff(
              'all my Western logocentric stuff ', 'about factoring numbers',
        )) == 'all my Western logocentric stuff about factoring numbers'

    # ....................{ FAIL                           }....................
    # Assert this decorator raises the expected exception when decorating a
    # synchronous generator annotating its return as anything *EXCEPT*
    # "Generator[...]", "Iterable[...]", and "Iterator[...]".
    with raises_uncached(BeartypeDecorHintPep484585Exception):
        @beartype
        def GET_OUT_OF_THE_CAR(
            FOR_THE_LOVE_OF_GOD: str, FACTOR_THE_NUMBER: str) -> str:
            yield FOR_THE_LOVE_OF_GOD + FACTOR_THE_NUMBER
