#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python word size** utility unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.py.utilpyword` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_word_size() -> None:
    '''
    Test the :func:`beartype._util.py.utilpyword.WORD_SIZE` constant.
    '''

    # Defer test-specific imports.
    from beartype._util.py.utilpyword import WORD_SIZE

    # Assert the active Python interpreter to be either 32- or 64-bit.
    assert WORD_SIZE in {32, 64}
