#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**PyInstaller integration test data package entry point** (i.e., root script
importing the lower-level package submodule performing business logic for this
package, validating that the :mod:`beartype` package raises *no* unexpected
exceptions when the third-party PyInstaller framework bundles this package into
an executable binary file).

Caveats
-------
**PyInstaller requires a root script.** Since PyInstaller fails to support
standard entry points (e.g., :mod:`the_blaze.__main__` submodule), this
executable script (which no one cares about) exists solely to facilitate the
execution of this package (which everyone cares about).
'''

# ....................{ IMPORTS ~ beartype                 }....................
# Import from a package registering a "beartype.claw" import hook *BEFORE*
# importing from any other packages. Prior to the resolution of the issue
# validated by this integration test, the first import performed *AFTER* (but
# not before) the first import from a package registering a "beartype.claw"
# import hook in a PyInstaller-bundled binary fails with an unreadable
# "ModuleNotFoundError" exception. Only importing from a package registering a
# "beartype.claw" import hook reliably reproduces the underlying issue validated
# by this integration test.
from the_blaze import the_splendour

# ....................{ IMPORTS ~ non-beartype             }....................
# Import an arbitrary attribute from an arbitrary standard Python module
# guaranteed to exist.
from argparse import ArgumentParser

# ....................{ MAIN                               }....................
# Trivially validate an arbitrary fact about this attribute as a sanity check.
if not isinstance(ArgumentParser, type):
    raise ValueError(
        f'"argparse.ArgumentParser" {repr(ArgumentParser)} not type.')
