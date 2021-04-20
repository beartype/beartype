#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Callable scope utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.utilfuncscope` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ CLASSES                           }....................
class WhenOwlsCallTheBreathlessMoon(object):
    '''
    Arbitrary class declaring an arbitrary method.
    '''

    def in_the_blue_veil_of_the_night(self) -> None:
        '''
        Arbitrary method.
        '''

        pass

# ....................{ CALLABLES                         }....................
def when_in_the_springtime_of_the_year():
    '''
    Arbitrary callable declaring an arbitrary nested callable.
    '''

    def when_the_trees_are_crowned_with_leaves():
        '''
        Arbitrary nested callable.
        '''

        pass

    # Return this nested callable.
    return when_the_trees_are_crowned_with_leaves

# ....................{ TESTS                             }....................
def test_is_func_nested() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncscope.is_func_nested` function.
    '''

    # Defer heavyweight imports.
    from beartype._util.func.utilfuncscope import is_func_nested

    # Nested callable returned by the above callable.
    when_the_ash_and_oak_and_the_birch_and_yew = (
        when_in_the_springtime_of_the_year())

    # Assert this function accepts methods.
    assert is_func_nested(
        WhenOwlsCallTheBreathlessMoon.in_the_blue_veil_of_the_night) is True

    # Assert this function accepts nested callables.
    # print(f'__nested__: {repr(when_the_ash_and_oak_and_the_birch_and_yew.__nested__)}')
    assert is_func_nested(when_the_ash_and_oak_and_the_birch_and_yew) is True

    # Assert this function rejects non-nested parent callables declaring nested
    # callables.
    # print(f'__nested__: {repr(when_in_the_springtime_of_the_year.__nested__)}')
    assert is_func_nested(when_in_the_springtime_of_the_year) is False

    # Assert this function rejects C-based builtins.
    assert is_func_nested(iter) is False


#FIXME: Unclear whether we'll ever require this, but preserved as is for now.
# def test_get_func_wrappee() -> None:
#     '''
#     Test the
#     :func:`beartype._util.func.utilfuncget.get_func_wrappee` function.
#     '''
#
#     # Defer heavyweight imports.
#     from beartype.roar._roarexc import _BeartypeUtilCallableException
#     from beartype._util.func.utilfuncget import get_func_wrappee
#     from functools import wraps
#
#     # Arbitrary callable *NOT* decorated by @wraps.
#     def the_journey_begins_with_curiosity() -> str:
#         return 'And envolves into soul-felt questions'
#
#     # Arbitrary callable decorated by @wraps.
#     @wraps(the_journey_begins_with_curiosity)
#     def on_the_stones_that_we_walk() -> str:
#         return (
#             the_journey_begins_with_curiosity() +
#             'And choose to make our path'
#         )
#
#     # Assert this getter raises the expected exception when passed a callable
#     # *NOT* decorated by @wraps.
#     with raises(_BeartypeUtilCallableException):
#         get_func_wrappee(the_journey_begins_with_curiosity)
#
#     # Assert this getter returns the wrapped callable when passed a callable
#     # decorated by @wraps.
#     assert get_func_wrappee(on_the_stones_that_we_walk) is (
#         the_journey_begins_with_curiosity)
