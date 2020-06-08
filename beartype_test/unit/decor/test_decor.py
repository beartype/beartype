#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator unit tests.**

This submodule unit tests the :func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import pytest
from random import Random

# ....................{ TODO                              }....................
#FIXME: Validate that generator-based coroutines behave as expected, given the
#following snippet in the documentation for this third-party utility:
#    https://smarie.github.io/python-makefun
#
#    @beartype
#    def my_gencoroutine_impl(first_msg):
#        second_msg = (yield first_msg)
#        yield second_msg
#
#    # Verify that the new func is a correct generator-based coroutine.
#    cor = my_gencoroutine_impl('hi')
#    assert next(cor) == 'hi'
#    assert cor.send('chaps') == 'chaps'
#    cor.send('ola')  # raises StopIteration
#FIXME: Likewise, for async-based coroutines:
#    import asyncio
#
#    @beartype
#    async def my_native_coroutine_impl(what, sleep_time):
#        await asyncio.sleep(sleep_time)
#        return what
#
#    # verify that the new function is a native coroutine and behaves correctly
#    event_loop = asyncio.get_event_loop()
#    event_loop.run_until_complete(my_native_coroutine_impl('yum', 5))
#    assert out == 'yum'
#
#In the latter case, note that the usage of an asynchronous event loop
#justifiably complicates matters. Simple unit testing methodology fails here.
#Instead, we need to leverage an asyncio-aware approach. The most popular are:
#
#* "pytest-asyncio", a third-party pytest plugin providing a
#  @pytest.mark.asyncio decorator facilitating trivial asynchronous testing.
#  We'd rather not add yet another testing dependency merely to test one or two
#  asynchronous edge cases, however. Instead...
#* See this extremely well-written blog post:
#  https://medium.com/ideas-at-igenius/testing-asyncio-python-code-with-pytest-a2f3628f82bc
#  The core idea here is that we define a custom pytest fixture instantiating
#  an "asyncio" event loop enabling downstream unit tests to run asynchronous
#  callables under that loop: e.g.,
#      import asyncio
#
#      @pytest.fixture
#      def event_loop():
#          loop = asyncio.get_event_loop()
#          yield loop
#          loop.close()
#
#      def test_muh_async_func(event_loop):
#          assert 'nope' == event_loop.run_until_complete(muh_async_func('wut', 0))
#
#Self-obviously, the latter is the way to go for us. A trivial five-line
#fixture dominates a non-trivial third-party dependency any asynchronous day.

# ....................{ TESTS ~ pass                      }....................
def test_decor_noop() -> None:
    '''
    Test type checking for a function with no function annotations, reducing to
    *no* type checking.
    '''

    # Import this decorator.
    from beartype import beartype

    # Undecorated unannotated function.
    def khorne(gork, mork):
        return gork + mork

    # Decorated unannotated function.
    khorne_typed = beartype(khorne)

    # Assert that @beartype efficiently reduced to a noop (i.e., the identity
    # decorator) by simply returning the undecorated callable as is.
    assert khorne_typed is khorne

    # Call this function and assert the expected return value.
    assert khorne_typed('WAAAGH!', '!HGAAAW') == 'WAAAGH!!HGAAAW'

# ....................{ TESTS ~ pass : param              }....................
def test_decor_pass_param_position_keyword() -> None:
    '''
    Test type checking for a function call successfully passed annotated
    non-variadic positional and keyword parameters.
    '''

    # Import this decorator.
    from beartype import beartype

    # Function to be type checked.
    @beartype
    def slaanesh(daemonette: str, keeper_of_secrets: str) -> str:
        return daemonette + keeper_of_secrets

    # Call this function with both positional and keyword arguments and assert
    # the expected return value.
    assert slaanesh(
        'Seeker of Decadence', keeper_of_secrets="N'Kari") == (
        "Seeker of DecadenceN'Kari")


def test_decor_pass_param_keyword_only() -> None:
    '''
    Test type checking for a function call successfully passed an annotated
    keyword-only parameter following a variadic positional parameter.
    '''

    # Import this decorator.
    from beartype import beartype

    # Function to be type checked.
    @beartype
    def changer_of_ways(
        sky_shark: str, *dark_chronology: int, chaos_spawn: str) -> str:
        return (
            sky_shark +
            str(dark_chronology[0]) +
            str(dark_chronology[-1]) +
            chaos_spawn
        )

    # Call this function and assert the expected return value.
    assert changer_of_ways(
        'Screamers', 0, 1, 15, 25, chaos_spawn="Mith'an'driarkh") == (
        "Screamers025Mith'an'driarkh")


def test_decor_pass_param_tuple() -> None:
    '''
    Test type checking for a function call successfully passed a parameter
    annotated as a tuple.
    '''

    # Import this decorator.
    from beartype import beartype

    # Function to be type checked. For completeness, test both an actual class
    # *AND* a the fully-qualified name of a class in this tuple annotation.
    @beartype
    def genestealer(tyranid: str, hive_fleet: (str, 'int')) -> str:
        return tyranid + str(hive_fleet)

    # Call this function with each of the two types listed in the above tuple.
    assert genestealer('Norn-Queen', 'Behemoth') == 'Norn-QueenBehemoth'
    assert genestealer('Carnifex', 0xDEADBEEF) == 'Carnifex3735928559'


def test_decor_pass_param_custom() -> None:
    '''
    Test type checking for a function call successfully passed a parameter
    annotated as a user-defined rather than built-in type.
    '''

    # Import this decorator.
    from beartype import beartype

    # User-defined type.
    class CustomTestStr(str):
        pass

    # Function to be type checked.
    @beartype
    def hrud(gugann: str, delphic_plague: CustomTestStr) -> str:
        return gugann + delphic_plague

    # Call this function with each of the above type.
    assert hrud(
        'Troglydium hruddi', delphic_plague=CustomTestStr('Delphic Sink')) == (
        'Troglydium hruddiDelphic Sink')


def test_decor_pass_param_str() -> None:
    '''
    Test type checking for a function call successfully passed a parameter
    annotated as a string.
    '''

    # Import this decorator.
    from beartype import beartype

    # Dates between which the Sisters of Battle must have been established.
    ESTABLISHMENT_DATE_MIN = 36000
    ESTABLISHMENT_DATE_MAX = 37000

    # Function to be type checked.
    @beartype
    def sisters_of_battle(
        leader: str, establishment: 'random.Random') -> int:
        return establishment.randint(
            ESTABLISHMENT_DATE_MIN, ESTABLISHMENT_DATE_MAX)

    # Call this function with an instance of the type named above.
    assert sisters_of_battle('Abbess Sanctorum', Random()) in range(
        ESTABLISHMENT_DATE_MIN, ESTABLISHMENT_DATE_MAX + 1)

# ....................{ TESTS ~ pass : return             }....................
def test_decor_pass_return_none() -> None:
    '''
    Test type checking for a function call successfully returning ``None`` and
    annotated as such.
    '''

    # Import this decorator.
    from beartype import beartype

    # Function to be type checked.
    @beartype
    def xenos(interex: str, diasporex: str) -> None:
        print(interex + diasporex)

    # Call this function and assert no value to be returned.
    assert xenos(
        'Luna Wolves', diasporex='Iron Hands Legion') is None

# ....................{ TESTS ~ fail                      }....................
def test_decor_fail_wrappee_type() -> None:
    '''
    Test type checking for **invalid wrappees** (i.e., objects *not*
    decoratable by the :func:`beartype.beartype` decorator).
    '''

    # Import this decorator.
    from beartype import beartype
    from beartype.roar import BeartypeDecorWrappeeException

    EARLY_CODICES = ('Book of the Astronomican', 'Slaves to Darkness',)

    # Assert that...
    with pytest.raises(BeartypeDecorWrappeeException):
        # Uncallable objects cannot be wrapped by @beartype.
        beartype(EARLY_CODICES)

        # Callable classes cannot be wrapped by @beartype.
        @beartype
        class ImperiumNihilus(object):
            pass

# ....................{ TESTS ~ fail : param              }....................
def test_decor_fail_param_name() -> None:
    '''
    Test type checking for a function accepting a parameter name reserved for
    internal use by the :func:`beartype.beartype` decorator.
    '''

    # Import this decorator.
    from beartype import beartype
    from beartype.roar import BeartypeDecorParamNameException

    # Define a function accepting a reserved parameter name and assert the
    # expected exception.
    with pytest.raises(BeartypeDecorParamNameException):
        @beartype
        def jokaero(weaponsmith: str, __beartype_func: str) -> str:
            return weaponsmith + __beartype_func

# ....................{ TESTS ~ fail : param : call       }....................
def test_decor_fail_param_call_keyword_unknown() -> None:
    '''
    Test type checking for an annotated function call passed an unrecognized
    keyword parameter.
    '''

    # Import this decorator.
    from beartype import beartype
    from beartype.roar import BeartypeCallTypeParamException

    # Annotated function to be type checked.
    @beartype
    def tau(kroot: str, vespid: str) -> str:
        return kroot + vespid

    # Call this function with an unrecognized keyword parameter and assert the
    # expected exception.
    with pytest.raises(TypeError) as exception:
        tau(kroot='Greater Good', nicassar='Dhow')

    # For readability, the exception message should synopsize the exact issue
    # raised by the Python interpreter on calling the original function rather
    # than failing to synopsize the exact issue raised by the wrapper
    # type-checking the original function. Since the function annotations
    # defined above guarantee that the exception message of the latter will be
    # suffixed by "not a str", ensure this is *NOT* the case.
    assert not str(exception.value).endswith('not a str.')


def test_decor_fail_param_call_str() -> None:
    '''
    Test type checking for an annotated function call failing a string
    parameter type check.
    '''

    # Import this decorator.
    from beartype import beartype
    from beartype.roar import BeartypeCallTypeParamException

    # Dates between which the Black Legion must have been established.
    ESTABLISHMENT_DATE_MIN = 30000
    ESTABLISHMENT_DATE_MAX = 31000

    # Function to be type checked.
    @beartype
    def black_legion(primarch: str, establishment: 'random.Random') -> int:
        return establishment.randint(
            ESTABLISHMENT_DATE_MIN, ESTABLISHMENT_DATE_MAX)

    # Call this function with an invalid type and assert the expected
    # exception.
    with pytest.raises(BeartypeCallTypeParamException):
        black_legion('Horus', 'Abaddon the Despoiler')


def test_decor_fail_param_call_nonvariadic() -> None:
    '''
    Test type checking for an annotated function call failing a non-variadic
    parameter type check.
    '''

    # Import this decorator.
    from beartype import beartype
    from beartype.roar import BeartypeCallTypeParamException

    # Annotated function to be type checked.
    @beartype
    def eldar(isha: str, asuryan: (str, int)) -> str:
        return isha + asuryan

    # Call this function with an invalid type and assert the expected
    # exception.
    with pytest.raises(BeartypeCallTypeParamException):
        eldar('Mother of the Eldar', 100.100)


def test_decor_fail_param_call_variadic() -> None:
    '''
    Test type checking for an annotated function call failing a variadic
    parameter type check.
    '''

    # Import this decorator.
    from beartype import beartype
    from beartype.roar import BeartypeCallTypeParamException

    # Annotated function to be type checked.
    @beartype
    def imperium_of_man(
        space_marines: str, *ceaseless_years: int, primarch: str) -> str:
        return space_marines + str(ceaseless_years[1]) + primarch

    # Call this function with an invalid type and assert the expected
    # exception.
    with pytest.raises(BeartypeCallTypeParamException):
        imperium_of_man(
            'Legiones Astartes', 30, 31, 36, 'M41', primarch='Leman Russ')

# ....................{ TESTS ~ fail : param : hint       }....................
def test_decor_fail_param_hint_str() -> None:
    '''
    Test type checking for a function with unsupported string parameter
    annotations.
    '''

    # Import this decorator.
    from beartype import beartype

    # Assert the expected exception from attempting to type check a function
    # with a string parameter annotation referencing an unimportable module.
    with pytest.raises(ImportError):
        @beartype
        def eye_of_terror(
            ocularis_terribus: str,

            # While highly unlikely that a top-level module with this name will
            # ever exist, the possibility cannot be discounted. Since there
            # appears to be no syntactically valid module name prohibited from
            # existing, this is probably the best we can do.
            segmentum_obscurus: '__rand0m__.Warp',
        ) -> str:
            return ocularis_terribus + segmentum_obscurus

        eye_of_terror('Perturabo', 'Crone Worlds')

    # Assert the expected exception from attempting to type check a function
    # with a string parameter annotation referencing a missing attribute of an
    # importable module.
    with pytest.raises(ImportError):
        @beartype
        def navigator(
            astronomicon: str,

            # While highly unlikely that a top-level module attribute with this
            # name will ever exist, the possibility cannot be discounted. Since
            # there appears to be no syntactically valid module attribute name
            # prohibited from existing, this is probably the best we can do.
            navis_nobilite: 'random.__Psych1cL1ght__',
        ) -> str:
            return astronomicon + navis_nobilite

        navigator('Homo navigo', 'Kartr Hollis')


def test_decor_fail_param_hint_int() -> None:
    '''
    Test type checking for a function with an unsupported integer parameter
    annotation.
    '''

    # Import this decorator.
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintValueException

    # Assert the expected exception from attempting to type check a function
    # with a parameter annotation that is *NOT* a type.
    with pytest.raises(BeartypeDecorHintValueException):
        @beartype
        def nurgle(nurgling: str, great_unclean_one: 0x8BADF00D) -> str:
            return nurgling + str(great_unclean_one)

# ....................{ TESTS ~ fail : return             }....................
def test_decor_fail_return_call() -> None:
    '''
    Test type checking for an annotated function call failing a return type
    check.
    '''

    # Import this decorator.
    from beartype import beartype
    from beartype.roar import BeartypeCallTypeReturnException

    # Annotated function to be type checked.
    @beartype
    def necron(star_god: str, old_one: str) -> str:
        return 60e6

    # Call this function and assert the expected exception.
    with pytest.raises(BeartypeCallTypeReturnException):
        necron("C'tan", 'Elder Thing')


def test_decor_fail_return_hint() -> None:
    '''
    Test type checking for a function with an unsupported return annotation.
    '''

    # Import this decorator.
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintValueException

    # Assert the expected exception from attempting to type check a function
    # with a return annotation that is *NOT* a supported type.
    with pytest.raises(BeartypeDecorHintValueException):
        @beartype
        def tzeentch(disc: str, lord_of_change: str) -> ['Player of Games',]:
            return 0xB16B00B5
