#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**PyInstaller integration test data package initializer** (i.e., submodule
initializing this package validating that the :mod:`beartype` package raises
*no* unexpected exceptions when the third-party PyInstaller framework bundles
this package into an executable binary file).
'''

# ....................{ PREAMBLE                           }....................
# Print an otherwise ignorable statement as a sanity check for the caller.
print('Registering beartype.claw.beartype_this_package() import hook...')

# ....................{ IMPORTS                            }....................
from beartype.claw import beartype_this_package

# ....................{ BEARTYPE                           }....................
# Type-check this package with the standard beartype import hook.
beartype_this_package()
