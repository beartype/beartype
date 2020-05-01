#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype API unit tests.**

This submodule unit tests the public API of the :mod:`beartype` package itself
as implemented by the :mod:`beartype.__init__` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_api_beartype() -> None:
    '''
    Test the public API of the :mod:`beartype` package itself.
    '''

    # Import this package and relevant types from the beartype cave.
    import beartype
    from beartype.cave import DecoratorTypes

    # Assert this package's public attributes to be of the expected types.
    assert isinstance(beartype.beartype, DecoratorTypes)
    assert isinstance(beartype.__version__, str)
    assert isinstance(beartype.__version_info__, tuple)
