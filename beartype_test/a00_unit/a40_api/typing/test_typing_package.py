#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **typing subpackage initialization submodule** unit tests.

This submodule unit tests both the public *and* private API of the private
:mod:`beartype.typing.__init__` subpackage for sanity.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ protocol : metaclass       }....................
def test_typing_init_getattr() -> None:
    '''
    Test the private :class:`beartype.typing.__init__.__getattr__` dunder
    method.
    '''

    # Defer test-specific imports.
    import beartype.typing as beartype_typing
    from pytest import raises

    # Assert that attempting to import a non-existent attribute from the
    # "beartype.typing" subpackage raises the expected exception.
    with raises(AttributeError):
        beartype_typing.that_for_themselves_a_cooling_covert_make
