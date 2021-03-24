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

    # Assert this function accepts this nested callable.
    # print(f'__nested__: {repr(when_the_ash_and_oak_and_the_birch_and_yew.__nested__)}')
    assert is_func_nested(when_the_ash_and_oak_and_the_birch_and_yew) is True

    # Assert this function rejects the callable declaring this nested callable.
    # print(f'__nested__: {repr(when_in_the_springtime_of_the_year.__nested__)}')
    assert is_func_nested(when_in_the_springtime_of_the_year) is False

    # Assert this function rejects C-based builtins.
    assert is_func_nested(iter) is False
