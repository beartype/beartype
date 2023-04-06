#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator** :pep:`484`- and :pep:`585`-compliant **unit tests**.

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
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from beartype_test._util.pytroar import raises_uncached
    from collections.abc import Coroutine as Pep585Coroutine
    from typing import Union, Coroutine as Pep484Coroutine

    # ....................{ LOCALS                         }....................
    # Decorated coroutine whose return is annotated with an arbitrary
    # PEP-compliant type hint.
    @beartype
    async def control_the_car(
        said_the: Union[str, int],
        biggest_greenest_bat: Union[str, float],
    ) -> Union[str, float]:
        await sleep(0)
        return said_the + biggest_greenest_bat

    # Decorated coroutine whose return is annotated with a PEP 484-compliant
    # coroutine type hint.
    @beartype
    async def universal_love(
        said_the: Union[str, int], cactus_person: Union[str, float]) -> (
        Pep484Coroutine[None, None, Union[str, float]]):
        await sleep(0)
        return said_the + cactus_person

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

    # ....................{ VERSION                        }....................
    # If the active Python interpreter targets Python >= 3.9 and thus supports
    # PEP 585...
    if IS_PYTHON_AT_LEAST_3_9:
        # ....................{ LOCALS                     }....................
        # Decorated coroutine whose return is annotated with a PEP
        # 585-compliant coroutine type hint.
        @beartype
        async def transcendent_joy(
            said_the: Union[str, float], big_green_bat: Union[str, int]) -> (
            Pep585Coroutine[None, None, Union[str, float]]):
            await sleep(0)
            return said_the + big_green_bat

        # ....................{ PASS                       }....................
        # Assert awaiting this coroutine returns the expected value.
        assert await transcendent_joy(
            'A thousand stars of sertraline ',
            'whirled round quetiapine moons'
        ) == 'A thousand stars of sertraline whirled round quetiapine moons'

        # ....................{ FAIL                       }....................
        # Assert @beartype raises the expected exception when decorating a
        # coroutine whose return is annotated with a PEP 585-compliant
        # coroutine type hint *NOT* subscripted by exactly three child hints.
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
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
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
    #FIXME: Refactor this unwieldy and unmaintainable DRY violation by iterating
    #over a tuple of all return type hints to be tested: e.g.,
    #    RETURN_HINTS = (
    #        AsyncGeneratorUnsubscripted,
    #        Pep484AsyncGenerator[Union[str, float], None],
    #    )
    #
    #    for return_hint in RETURN_HINTS:
    #        @beartype
    #        async def some_kind_of_spiritual_thing(
    #            said_the: Union[str, int],
    #            bigger_greener_bat: Union[str, float]
    #        ) -> return_hint:
    #            await sleep(0)
    #            yield said_the + bigger_greener_bat

    # Decorated asynchronous generators whose returns are annotated with PEP
    # 484-compliant "AsyncGenerator[...]", "AsyncIterable[...]", and
    # "AsyncIterator[...]" type hints (respectively).
    @beartype
    async def some_kind_of_spiritual_thing(
        said_the: Union[str, int], bigger_greener_bat: Union[str, float]) -> (
        AsyncGeneratorUnsubscripted):
        await sleep(0)
        yield said_the + bigger_greener_bat

    @beartype
    async def not_splitting_numbers(
        said_the: Union[str, int], bigger_greener_bat: Union[str, float]) -> (
        Pep484AsyncGenerator[Union[str, float], None]):
        await sleep(0)
        yield said_the + bigger_greener_bat

    @beartype
    async def chaos_never_comes_from_the_ministry_of_chaos(
        said_the: Union[str, int], bigger_greener_bat: Union[str, float]) -> (
        Pep484AsyncIterable[Union[str, float]]):
        await sleep(0)
        yield said_the + bigger_greener_bat

    @beartype
    async def nor_void_from_the_ministry_of_void(
        said_the: Union[str, int], bigger_greener_bat: Union[str, float]) -> (
        Pep484AsyncIterator[Union[str, float]]):
        await sleep(0)
        yield said_the + bigger_greener_bat

    # ....................{ PASS                           }....................
    # Assert awaiting these asynchronous generators return the expected values.
    # Unlike synchronous generators, asynchronous generators are *NOT* actually
    # iterators and thus have *NO* clean analogue to the iter() and next()
    # builtins. The closest approximation is this rather unclean hack:
    #     await not_splitting_number.__anext__()
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

    async for not_splitting_number in not_splitting_numbers(
        'the sand sizzled sharp like cooking oil that hissed and sang and ',
        'threatened to boil the octahedral dunes.',
    ):
        assert not_splitting_number == (
            'the sand sizzled sharp like cooking oil that hissed and sang and '
            'threatened to boil the octahedral dunes.'
        )

    async for chaos in chaos_never_comes_from_the_ministry_of_chaos(
        'The force of the blast went rattling past the bat and the beach, ',
        'disturbing each,'
    ):
        assert chaos == (
            'The force of the blast went rattling past the bat and the beach, '
            'disturbing each,'
        )

    async for void in nor_void_from_the_ministry_of_void(
        'then made its way to a nearby bay of upside-down trees ',
        'with their roots in the breeze and their branches underground.'
    ):
        assert void == (
            'then made its way to a nearby bay of upside-down trees '
            'with their roots in the breeze and their branches underground.'
        )

    # ....................{ FAIL                           }....................
    # Assert this decorator raises the expected exception when decorating an
    # asynchronous generator annotating its return as anything *EXCEPT*
    # "AsyncGenerator[...]", "AsyncIterable[...]", and "AsyncIterator[...]".
    with raises_uncached(BeartypeDecorHintPep484585Exception):
        @beartype
        async def upside_down_trees(
            roots_in_the_breeze: str, branches_underground: str) -> str:
            await sleep(0)
            yield roots_in_the_breeze + branches_underground

    # ....................{ VERSION                        }....................
    # If the active Python interpreter targets Python >= 3.9 and thus supports
    # PEP 585...
    if IS_PYTHON_AT_LEAST_3_9:
        # ....................{ LOCALS                     }....................
        # Decorated asynchronous generators whose returns are annotated with
        # PEP 585-compliant "AsyncGenerator[...]", "AsyncIterable[...]", and
        # "AsyncIterator[...]" type hints (respectively).
        @beartype
        async def but_joining_mind(
            said_the: Union[str, float], bigger_greener_bat: Union[str, int],
        ) -> Pep585AsyncGenerator[Union[str, float], None]:
            await sleep(0)
            yield said_the + bigger_greener_bat

        @beartype
        async def lovers_do_not_love_to_increase(
            said_the: Union[str, float], bigger_greener_bat: Union[str, int],
        ) -> Pep585AsyncIterable[Union[str, float]]:
            await sleep(0)
            yield said_the + bigger_greener_bat

        async def the_amount_of_love_in_the_world(
            said_the: Union[str, float], bigger_greener_bat: Union[str, int],
        ) -> Pep585AsyncIterator[Union[str, float]]:
            await sleep(0)
            yield said_the + bigger_greener_bat

        # ....................{ PASS                       }....................
        # Assert awaiting these asynchronous generators return the expected
        # values.
        async for but_joining_time in but_joining_mind(
            'A meteorite of pure delight ', 'struck the sea without a sound.'):
            assert but_joining_time == (
                'A meteorite of pure delight struck the sea without a sound.')

        async for the_mind_that_thrills in lovers_do_not_love_to_increase(
            'The sea turned hot ',
            'and geysers shot up from the floor below.'
        ):
            assert the_mind_that_thrills == (
                'The sea turned hot and geysers shot up from the floor below.')

        async for the_face_of_the_beloved in the_amount_of_love_in_the_world(
            'First one of wine, then one of brine, ',
            'then one more yet of turpentine, and we three stared at the show.'
        ):
            assert the_face_of_the_beloved == (
                'First one of wine, '
                'then one of brine, '
                'then one more yet of turpentine, '
                'and we three stared at the show.'
            )

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
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
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
    #FIXME: Refactor this unwieldy and unmaintainable DRY violation by iterating
    #over a tuple of all return type hints to be tested: e.g.,
    #    RETURN_HINTS = (
    #        GeneratorUnsubscripted,
    #        Pep484Generator[Union[str, float], None],
    #    )
    #
    #    for return_hint in RETURN_HINTS:
    #        @beartype
    #        def western_logocentric_stuff(
    #            said_the: Union[str, int],
    #            bigger_greener_bat: Union[str, float]
    #        ) -> return_hint:
    #            await sleep(0)
    #            yield said_the + bigger_greener_bat

    # Decorated synchronous generators whose returns are annotated with PEP
    # 484-compliant "Generator[...]", "Iterable[...]", and "Iterator[...]" type
    # hints (respectively).
    @beartype
    def western_logocentric_stuff(
        said_the: Union[str, int], bigger_greener_bat: Union[str, float]) -> (
        GeneratorUnsubscripted):
        yield said_the + bigger_greener_bat

    @beartype
    def not_facts_or_factors_or_factories(
        said_the: Union[str, int], bigger_greener_bat: Union[str, float]) -> (
        Pep484Generator[Union[str, float], None, None]):
        yield said_the + bigger_greener_bat

    @beartype
    def not_to_seek(
        said_the: Union[str, int], bigger_greener_bat: Union[str, float]) -> (
        Pep484Iterable[Union[str, float]]):
        yield said_the + bigger_greener_bat

    @beartype
    def not_to_follow(
        said_the: Union[str, int], bigger_greener_bat: Union[str, float]) -> (
        Pep484Iterator[Union[str, float]]):
        yield said_the + bigger_greener_bat

    # ....................{ PASS                           }....................
    # Assert awaiting these synchronous generators yield the expected values
    # when iterated.
    assert next(western_logocentric_stuff(
        'all my Western logocentric stuff ', 'about factoring numbers',
    )) == 'all my Western logocentric stuff about factoring numbers'

    assert next(not_facts_or_factors_or_factories(
        'The watery sun began to run ', 'and it fell on the ground as rain.',
    )) == 'The watery sun began to run and it fell on the ground as rain.'

    assert next(not_to_seek(
        'At the sound of that, ',
        'the big green bat started rotating in place.',
    )) == (
        'At the sound of that, the big green bat started rotating in place.')

    assert next(not_to_follow(
        'On its other side was a bigger greener bat, ',
        'with an ancient, wrinkled face.'
    )) == (
        'On its other side was a bigger greener bat, '
        'with an ancient, wrinkled face.'
    )

    # ....................{ FAIL                           }....................
    # Assert this decorator raises the expected exception when decorating a
    # synchronous generator annotating its return as anything *EXCEPT*
    # "Generator[...]", "Iterable[...]", and "Iterator[...]".
    with raises_uncached(BeartypeDecorHintPep484585Exception):
        @beartype
        def GET_OUT_OF_THE_CAR(
            FOR_THE_LOVE_OF_GOD: str, FACTOR_THE_NUMBER: str) -> str:
            yield FOR_THE_LOVE_OF_GOD + FACTOR_THE_NUMBER

    # ....................{ VERSION                        }....................
    # If the active Python interpreter targets Python >= 3.9 and thus supports
    # PEP 585...
    if IS_PYTHON_AT_LEAST_3_9:
        # ....................{ LOCALS                     }....................
        # Decorated synchronous generators whose returns are annotated with PEP
        # 585-compliant "Generator[...]", "Iterable[...]", and "Iterator[...]"
        # type hints (respectively).
        @beartype
        def contact_with_the_abstract_attractor(
            said_the: Union[str, float], bigger_greener_bat: Union[str, int],
        ) -> Pep585Generator[Union[str, float], None, None]:
            yield said_the + bigger_greener_bat

        @beartype
        def but_to_jump_forth_into_the_deep(
            said_the: Union[str, float], bigger_greener_bat: Union[str, int],
        ) -> Pep585Iterable[Union[str, float], None, None]:
            yield said_the + bigger_greener_bat

        @beartype
        def not_to_grind_or_to_bind_or_to_seek(
            said_the: Union[str, float], bigger_greener_bat: Union[str, int],
        ) -> Pep585Iterator[Union[str, float], None, None]:
            yield said_the + bigger_greener_bat

        # ....................{ PASS                       }....................
        # Assert these synchronous generators yield the expected values when
        # iterated.
        assert next(contact_with_the_abstract_attractor(
            'Then tree and beast all fled due east and ',
            'the moon and stars shot south.',
        )) == (
            'Then tree and beast all fled due east and '
            'the moon and stars shot south.'
        )

        assert next(but_to_jump_forth_into_the_deep(
            'The big green bat started to turn around ',
            'what was neither its x, y, or z axis,'
        )) == (
            'The big green bat started to turn around '
            'what was neither its x, y, or z axis,'
        )

        assert next(not_to_grind_or_to_bind_or_to_seek(
            'slowly rotating to reveal what was undoubtedly the biggest, ',
            'greenest bat that I had ever seen, a bat bigger and greener '
            'than which it was impossible to conceive.'
        )) == (
            'slowly rotating to reveal what was undoubtedly the biggest, '
            'greenest bat that I had ever seen, a bat bigger and greener '
            'than which it was impossible to conceive.'
        )
