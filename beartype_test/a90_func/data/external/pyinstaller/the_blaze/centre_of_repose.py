#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**PyInstaller integration test data package sibling submodule** (i.e., submodule
imported from by the main submodule for this package, validating that the
:mod:`beartype` package raises *no* unexpected exceptions when the third-party
PyInstaller framework bundles this package into an executable binary file).

This submodule is required to validate that *other* submodules in this package
(notably the main submodule) can still import from this package within a
PyInstaller-bundled executable even *after* the root :mod:`the_blaze.__init__`
submodule registers a :mod:`beartype.claw` import hook. 
'''

# ....................{ GLOBALS                            }....................
EVEN_HERE_INTO_MY_CENTRE_OF_REPOSE = 'and_the_symmetry'
'''
Arbitrary global to be imported into the main submodule.
'''
