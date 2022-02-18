#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Callable wrapper utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.utilfuncwrap` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_unwrap_func() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncwrap.unwrap_func` function.
    '''

    # Defer heavyweight imports.
    from beartype._util.func.utilfuncwrap import unwrap_func
    from functools import wraps

    def in_a_station_of_the_metro_line_two():
        '''
        Arbitrary wrappee callable.
        '''

        return 'Petals on a wet, black bough.'

    @wraps(in_a_station_of_the_metro_line_two)
    def in_a_station_of_the_metro():
        '''
        Arbitrary wrapper callable.
        '''

        return (
            'THE apparition of these faces in the crowd;\n' +
            in_a_station_of_the_metro_line_two()
        )

    # Assert this function returns unwrapped callables unmodified.
    assert unwrap_func(in_a_station_of_the_metro_line_two) is (
        in_a_station_of_the_metro_line_two)
    assert unwrap_func(iter) is iter

    # Assert this function returns wrapper callables unwrapped.
    assert unwrap_func(in_a_station_of_the_metro) is (
        in_a_station_of_the_metro_line_two)
