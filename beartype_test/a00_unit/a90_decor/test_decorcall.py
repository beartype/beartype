#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator dataclass unit tests.**

This submodule unit tests the :func:`beartype._decor._call` submodule.
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
    Test usage of the :func:`beartype._decor._call.BeartypeCall` dataclass.
    '''

    # Defer heavyweight imports.
    from beartype._decor._call import BeartypeCall

    # Beartype decorator dataclass.
    beartype_data = BeartypeCall()

    # Assert that instances of this dataclass are unhashable.
    with raises(TypeError):
        hash(beartype_data)
