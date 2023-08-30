#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`563` unit tests.

This submodule unit tests the public :func:`beartype.peps.resolve_pep563`
function.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# .....................{ TESTS                             }....................
def test_resolve_pep563() -> None:
    '''
    Test the :func:`beartype.peps.resolve_pep563` resolver.
    '''

    # .....................{ IMPORTS                       }....................
    # Defer test-specific imports.
    from beartype.peps import resolve_pep563
    from beartype.roar import BeartypePep563Exception
    from pytest import raises

    # .....................{ FAIL                          }....................
    # Assert that this resolver raises the expected exception when passed an
    # uncallable object.
    with raises(BeartypePep563Exception):
        resolve_pep563('Mont Blanc yet gleams on high:—the power is there,')
