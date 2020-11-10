#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator dataclass unit tests.**

This submodule unit tests the :func:`beartype._decor._data` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import raises

# ....................{ TESTS                             }....................
def test_decor_data() -> None:
    '''
    Test usage of the :func:`beartype._decor._data.BeartypeData` dataclass.
    '''

    # Defer heavyweight imports.
    from beartype._decor._data import BeartypeData

    # Beartype decorator dataclass.
    beartype_data = BeartypeData()

    # Assert that instances of this dataclass are unhashable.
    with raises(TypeError):
        hash(beartype_data)
