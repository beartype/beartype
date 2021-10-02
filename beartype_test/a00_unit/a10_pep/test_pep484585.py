#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype decorator :pep:`484`- and :pep:`585`-compliant type hint unit tests.

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to :pep:`484`- and :pep:`585`-compliant type hints.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning
from beartype_test.util.mark.pytmark import ignore_warnings

# ....................{ TESTS ~ decor : async             }....................
# Prevent pytest from capturing and displaying all expected non-fatal
# beartype-specific warnings emitted by the @beartype decorator below. Urgh!
@ignore_warnings(BeartypeDecorHintPep585DeprecationWarning)
async def test_decor_async_coroutine() -> None:
    '''
    Test decorating coroutines with the :func:`beartype.beartype` decorator.
    '''

    # Defer heavyweight imports.
    from asyncio import sleep
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintPep484585Exception
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from beartype_test.util.pytroar import raises_uncached
    from collections.abc import Coroutine as Pep585Coroutine
    from typing import Union, Coroutine as Pep484Coroutine

    # Decorated coroutine whose return is annotated with an arbitrary
    # PEP-compliant type hint.
    @beartype
    async def control_the_car(
        said_the: Union[str, int],
        biggest_greenest_bat: Union[str, float],
    ) -> Union[str, float]:
        await sleep(0)
        return said_the + biggest_greenest_bat

    # Assert awaiting this coroutine returns the expected value.
    assert await control_the_car(
        'I saw the big green bat bat a green big eye. ',
        'Suddenly I knew I had gone too far.') == (
        'I saw the big green bat bat a green big eye. '
        'Suddenly I knew I had gone too far.')

    # Decorated coroutine whose return is annotated with a PEP 484-compliant
    # coroutine type hint.
    @beartype
    async def universal_love(
        said_the: Union[str, int], cactus_person: Union[str, float]) -> (
        Pep484Coroutine[None, None, Union[str, float]]):
        await sleep(0)
        return said_the + cactus_person

    # Assert awaiting this coroutine returns the expected value.
    assert await universal_love(
        'The sea was made of strontium; ', 'the beach was made of rye.') == (
        'The sea was made of strontium; the beach was made of rye.')

    # If the active Python interpreter targets Python >= 3.9 and thus supports
    # PEP 585...
    if IS_PYTHON_AT_LEAST_3_9:
        # Decorated coroutine whose return is annotated with a PEP
        # 585-compliant coroutine type hint.
        @beartype
        async def transcendent_joy(
            said_the: Union[str, float], big_green_bat: Union[str, int]) -> (
            Pep585Coroutine[None, None, Union[str, float]]):
            await sleep(0)
            return said_the + big_green_bat

        # Assert awaiting this coroutine returns the expected value.
        assert await transcendent_joy(
            'A thousand stars of sertraline ',
            'whirled round quetiapine moons'
        ) == 'A thousand stars of sertraline whirled round quetiapine moons'

        #FIXME: Assert this decorator raises the expected exception when
        #decorating an asynchronous callable annotating its return as
        #"Pep585Coroutine[...]" accepting an invalid number of arguments.


# Prevent pytest from capturing and displaying all expected non-fatal
# beartype-specific warnings emitted by the @beartype decorator below. Hurk!
@ignore_warnings(BeartypeDecorHintPep585DeprecationWarning)
async def test_decor_async_generator() -> None:
    '''
    Test decorating asynchronous generators with the :func:`beartype.beartype`
    decorator.
    '''

    # Defer heavyweight imports.
    from asyncio import sleep
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintPep484585Exception
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from beartype_test.util.pytroar import raises_uncached
    from collections.abc import AsyncGenerator as Pep585AsyncGenerator
    from typing import Union, AsyncGenerator as Pep484AsyncGenerator

    # Decorated asynchronous generator whose return is annotated with a PEP
    # 484-compliant asynchronous generator type hint.
    @beartype
    async def not_splitting_numbers(
        said_the: Union[str, int], bigger_greener_bat: Union[str, float]) -> (
        Pep484AsyncGenerator[Union[str, float], None]):
        await sleep(0)
        yield said_the + bigger_greener_bat

    # Assert awaiting this asynchronous generator returns the expected value.
    # Unlike synchronous generators, asynchronous generators are *NOT* actually
    # iterators and thus have *NO* clean analogue to the iter() and next()
    # builtins. The closest approximation is this rather unclean hack:
    #     await not_splitting_number.__anext__()
    # See also this relevant StackOvelflow post:
    #     https://stackoverflow.com/a/42561322/2809027
    async for not_splitting_number in not_splitting_numbers(
        'the sand sizzled sharp like cooking oil that hissed and sang and ',
        'threatened to boil the octahedral dunes.',
    ):
        # await sleep(0)
        assert not_splitting_number == (
            'the sand sizzled sharp like cooking oil that hissed and sang and '
            'threatened to boil the octahedral dunes.'
        )

    # If the active Python interpreter targets Python >= 3.9 and thus supports
    # PEP 585...
    if IS_PYTHON_AT_LEAST_3_9:
        # Decorated asynchronous generator whose return is annotated with a PEP
        # 585-compliant asynchronous generator type hint.
        @beartype
        async def but_joining_mind(
            said_the: Union[str, float],
            bigger_greener_bat: Union[str, int],
        ) -> Pep585AsyncGenerator[Union[str, float], None]:
            await sleep(0)
            yield said_the + bigger_greener_bat

        # Assert awaiting this asynchronous generator returns the expected value.
        async for but_joining_time in but_joining_mind(
            'A meteorite of pure delight ', 'struck the sea without a sound.'):
            assert but_joining_time == (
                'A meteorite of pure delight struck the sea without a sound.')

    # Assert this decorator raises the expected exception when decorating an
    # asynchronous generator annotating its return as anything *EXCEPT*
    # "AsyncGenerator[...]".
    with raises_uncached(BeartypeDecorHintPep484585Exception):
        @beartype
        async def upside_down_trees(
            roots_in_the_breeze: str, branches_underground: str) -> str:
            await sleep(0)
            yield roots_in_the_breeze + branches_underground

# ....................{ TESTS ~ decor : sync              }....................
# Prevent pytest from capturing and displaying all expected non-fatal
# beartype-specific warnings emitted by the @beartype decorator below. Blargh!
@ignore_warnings(BeartypeDecorHintPep585DeprecationWarning)
def test_decor_sync_generator() -> None:
    '''
    Test decorating synchronous generators with the :func:`beartype.beartype`
    decorator.
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintPep484585Exception
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from beartype_test.util.pytroar import raises_uncached
    from collections.abc import Generator as Pep585Generator
    from typing import Union, Generator as Pep484Generator

    # Decorated synchronous generator whose return is annotated with a PEP
    # 484-compliant synchronous generator type hint.
    @beartype
    def not_facts_or_factors_or_factories(
        said_the: Union[str, int],
        bigger_greener_bat: Union[str, float],
    ) -> Pep484Generator[Union[str, float], None, None]:
        yield said_the + bigger_greener_bat

    # Assert this synchronous generator yields the expected value when
    # iterated.
    assert next(not_facts_or_factors_or_factories(
        'The watery sun began to run ',
        'and it fell on the ground as rain.',
    )) == 'The watery sun began to run and it fell on the ground as rain.'

    # If the active Python interpreter targets Python >= 3.9 and thus supports
    # PEP 585...
    if IS_PYTHON_AT_LEAST_3_9:
        # Decorated synchronous generator whose return is annotated with a PEP
        # 585-compliant synchronous generator type hint.
        @beartype
        def contact_with_the_abstract_attractor(
            said_the: Union[str, float],
            bigger_greener_bat: Union[str, int],
        ) -> Pep585Generator[Union[str, float], None, None]:
            yield said_the + bigger_greener_bat

        # Assert this synchronous generator yields the expected value when
        # iterated.
        assert next(contact_with_the_abstract_attractor(
            'Then tree and beast all fled due east and ',
            'the moon and stars shot south.',
        )) == (
            'Then tree and beast all fled due east and '
            'the moon and stars shot south.'
        )

    # Assert this decorator raises the expected exception when decorating a
    # synchronous generator annotating its return as anything *EXCEPT*
    # "Generator[...]".
    with raises_uncached(BeartypeDecorHintPep484585Exception):
        @beartype
        def GET_OUT_OF_THE_CAR(
            FOR_THE_LOVE_OF_GOD: str, FACTOR_THE_NUMBER: str) -> str:
            yield FOR_THE_LOVE_OF_GOD + FACTOR_THE_NUMBER
