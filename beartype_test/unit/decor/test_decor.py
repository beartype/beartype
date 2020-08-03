#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator type hint-agnostic unit tests.**

This submodule unit tests high-level functionality of the
:func:`beartype.beartype` decorator independent of lower-level type hinting
concerns (e.g., PEP-compliance, PEP-noncompliance).
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

from beartype_test.util.pyterror import raises_cached
from pytest import raises
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

# ....................{ TESTS ~ fail                      }....................
def test_decor_fail_wrappee_type() -> None:
    '''
    Test type-checking for **invalid wrappees** (i.e., objects *not*
    decoratable by the :func:`beartype.beartype` decorator).
    '''

    # Import this decorator.
    from beartype import beartype
    from beartype.roar import BeartypeDecorWrappeeException

    EARLY_CODICES = ('Book of the Astronomican', 'Slaves to Darkness',)

    # Assert that...
    with raises(BeartypeDecorWrappeeException):
        # Uncallable objects cannot be wrapped by @beartype.
        beartype(EARLY_CODICES)

        # Callable classes cannot be wrapped by @beartype.
        @beartype
        class ImperiumNihilus(object):
            pass


def test_decor_fail_hint_unhashable() -> None:
    '''
    Test type-checking for **unhashable annotations** (i.e., annotations that
    are *not* hashable and thus neither classes, strings, tuples, nor tuples of
    classes and/or strings).
    '''

    # Import this decorator.
    from beartype import beartype

    # Assert the expected exception from attempting to type-check a function
    # with an unhashable parameter annotation.
    with raises(TypeError):
        @beartype
        def before_the_fall(
            craftworld: ['Alaitoc', 'Black Library', 'Biel-Tan',]) -> str:
            return craftworld[0]

    # Assert the expected exception from attempting to type-check a function
    # with an unhashable return value annotation.
    with raises(TypeError):
        @beartype
        def after_the_fall(craftworld: str) -> [
            'Iyanden', 'Saim-Hann', 'Ulthwé',]:
            return [craftworld,]

# ....................{ TESTS ~ fail : param              }....................
def test_decor_fail_param_name() -> None:
    '''
    Test type-checking for a function accepting a parameter name reserved for
    internal use by the :func:`beartype.beartype` decorator.
    '''

    # Import this decorator.
    from beartype import beartype
    from beartype.roar import BeartypeDecorParamNameException

    # Define a function accepting a reserved parameter name and assert the
    # expected exception.
    with raises(BeartypeDecorParamNameException):
        @beartype
        def jokaero(weaponsmith: str, __beartype_func: str) -> str:
            return weaponsmith + __beartype_func

# ....................{ TESTS ~ fail : param : call       }....................
def test_decor_fail_param_call_keyword_unknown() -> None:
    '''
    Test type-checking for an annotated function call passed an unrecognized
    keyword parameter.
    '''

    # Import this decorator.
    from beartype import beartype

    # Annotated function to be type-checked.
    @beartype
    def tau(kroot: str, vespid: str) -> str:
        return kroot + vespid

    # Call this function with an unrecognized keyword parameter and assert the
    # expected exception.
    with raises(TypeError) as exception:
        tau(kroot='Greater Good', nicassar='Dhow')

    # Assert that the exception message is that raised by the Python
    # interpreter on calling the decorated callable rather than that raised by
    # the wrapper function on type-checking that callable. This message is
    # currently stable across Python versions and thus safely tested against.
    assert str(exception.value) == (
        "tau() got an unexpected keyword argument 'nicassar'")
