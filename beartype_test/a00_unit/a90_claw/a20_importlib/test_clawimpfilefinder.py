#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **import hook file finder** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype.claw._importlib._clawimpfilefinder` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
#FIXME: Implement us up, please. *sigh*
def test_make_beartype_file_finder_path_hook() -> None:
    '''
    Test the
    :func:`beartype.claw._importlib._clawimpfilefinder.make_beartype_file_finder_path_hook`
    factory.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.claw._importlib._clawimpfilefinder import (
        make_beartype_file_finder_path_hook)

    # ....................{ ASSERTS                        }....................
