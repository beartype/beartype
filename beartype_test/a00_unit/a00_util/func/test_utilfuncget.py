#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Callable utility getter unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.utilfuncget` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ TESTS                             }....................
def test_get_func_wrappee() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncget.get_func_wrappee` function.
    '''

    # Defer heavyweight imports.
    from beartype.roar import _BeartypeUtilCallableException
    from beartype._util.func.utilfuncget import get_func_wrappee
    from functools import wraps

    # Arbitrary callable *NOT* decorated by @wraps.
    def the_journey_begins_with_curiosity() -> str:
        return 'And envolves into soul-felt questions'

    # Arbitrary callable decorated by @wraps.
    @wraps(the_journey_begins_with_curiosity)
    def on_the_stones_that_we_walk() -> str:
        return (
            the_journey_begins_with_curiosity() +
            'And choose to make our path'
        )

    # Assert this getter raises the expected exception when passed a callable
    # *NOT* decorated by @wraps.
    with raises(_BeartypeUtilCallableException):
        get_func_wrappee(the_journey_begins_with_curiosity)

    # Assert this getter returns the wrapped callable when passed a callable
    # decorated by @wraps.
    assert get_func_wrappee(on_the_stones_that_we_walk) is (
        the_journey_begins_with_curiosity)
