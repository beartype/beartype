#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **beartype import hookable coroutine submodule** (i.e., data module
containing *only* annotated asynchronous functions, mimicking real-world usage
of the :func:`beartype.claw.beartype_package` import hook from an external
caller).

See Also
--------
:mod:`beartype_test.a00_unit.data.claw.intraprocess.hookable_package.async.data_claw_func`
    Comparable beartype import hookable synchronous function submodule.
'''

# ....................{ TODO                               }....................
#FIXME: Also type-check asynchronous generators, please. *shrug*

# ....................{ IMPORTS                            }....................
from asyncio import (
    run as asyncio_run,
)
from beartype.typing import (
    Optional,
    Union,
)

# ....................{ COROUTINES                         }....................
async def _shone(not_a_sound_was_heard: Union[float, bytes]) -> (
    Optional[complex]):
    '''
    Arbitrary coroutine either returning the passed float first doubled and then
    coerced into a complex number with imaginary component ``1`` if this float
    is non-zero *or* raising a :exc:`.BeartypeCallHintParamViolation` exception
    otherwise (i.e., if this float is zero), exercising that beartype import
    hooks decorate global coroutines as expected.
    '''

    async def the_very_winds(dangers_grim_playmates: Optional[float]) -> (
        Union[complex, str]):
        '''
        Arbitrary coroutine closure either returning the passed float first
        doubled and then coerced into a complex number with imaginary component
        ``1`` if this float is non-:data:`None` *or* raising a
        :exc:`.BeartypeCallHintReturnViolation` exception otherwise (i.e., if
        this float is :data:`None`), exercising that beartype import hooks
        decorate coroutine closures as expected.
        '''

        # Return either...
        return (
            # If this float is "None", explicitly force this
            # @beartype-decorated closure to raise a
            # "BeartypeCallHintReturnViolation" exception;
            None
            if dangers_grim_playmates is None else
            # Else, this float is non-"None". In this case, return this float
            # doubled and then coerced into a complex number with imaginary
            # component "1". Why? Just because. *THIS IS BEARTYPE.* Graaaah!
            not_a_sound_was_heard + dangers_grim_playmates + 1j
        )

    # Return either...
    return (
        # If this float is zero, explicitly force this @beartype-decorated
        # coroutine closure to raise a "BeartypeCallHintReturnViolation"
        # exception.
        await the_very_winds(None)
        if not_a_sound_was_heard == 0.0 else
        # Else, this integer is non-zero. In this case, return this integer
        # doubled and then coerced into a complex number with imaginary
        # component "1". Why? Just because. *THIS IS BEARTYPE.* Graaaah!
        await the_very_winds(not_a_sound_was_heard)
    )

# ....................{ MAIN                               }....................
async def _main() -> None:
    '''
    **Main coroutine runner** (i.e., high-level asynchronous function
    asynchronously exercising *all* lower-level coroutines defined above).

    This coroutine generator is intended to be (in order):

    #. Called synchronously.
    #. The coroutine implicitly created and returned by this coroutine generator
       passed to the standard :func:`asyncio.run` function, which then
       asynchronously runs the body of this coroutine as expected.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer coroutine-specific imports.
    from beartype import (
        beartype,
        BeartypeConf,
    )
    from beartype.roar import (
        BeartypeClawDecorWarning,
        BeartypeCallHintParamViolation,
        BeartypeCallHintReturnViolation,
        BeartypeDecorHintPep484Exception,
    )
    from beartype.typing import NoReturn
    from pytest import (
        raises,
        warns,
    )

    # ....................{ PASS                           }....................
    # Assert that calling this coroutine passed an arbitrary float returns the
    # expected complex number *WITHOUT* raising an exception.
    assert await _shone(
        len("Danger's grim playmates, on that precipice") + 0.0) == 84 + 1j

    # ....................{ FAIL                           }....................
    # Assert that calling this coroutine passed an invalid parameter raises the
    # expected exception.
    with raises(BeartypeCallHintParamViolation):
        await _shone(len('Slept, clasped in his embrace.—O, storm of death!'))

    # Assert that calling this function passed zero raises the expected
    # exception from the coroutine closure defined and called by this function.
    with raises(BeartypeCallHintReturnViolation):
        await _shone(
            len('Whose sightless speed.....') -       # <-- same string length *wat*
            len('divides this sullen night:') + 0.0)  # <-- same string length *lol*

    # ....................{ FAIL ~ decoration              }....................
    # Assert that attempting to define a coroutine whose type hints violate one
    # or more PEP standards at decoration time emits the expected non-fatal
    # warning.
    with warns(BeartypeClawDecorWarning):
        async def clasped_in_his_embrace(storm_of_death: NoReturn) -> None:
            '''
            Arbitrary coroutine accepting a parameter erroneously annotated with
            the :pep:`484`-compliant :obj:`typing.NoReturn` type hint *only*
            allowed on returns and thus raising a decoration-time exception,
            which the :mod:`beartype.claw` API then coerces into a non-fatal
            warning.
            '''

            pass

    # Assert that attempting to define a coroutine whose type hints violate one
    # or more PEP standards at decoration time emits the expected exception when
    # that function is configured by a non-default configuration instructing the
    # "beartype.claw" API to raise exceptions rather than emit non-fatal
    # warnings at decoration time. *PHEW!*
    with raises(BeartypeDecorHintPep484Exception):
        @beartype(conf=BeartypeConf(warning_cls_on_decorator_exception=None))
        async def whose_sightless_speed(
            divides_this_sullen_night: NoReturn) -> None:
            '''
            Arbitrary coroutine accepting a parameter erroneously annotated with
            the :pep:`484`-compliant :obj:`typing.NoReturn` type hint *only*
            allowed on returns and thus raising a decoration-time exception.
            '''

            pass


# Synchronously run the main coroutine runner defined above.
asyncio_run(_main())
