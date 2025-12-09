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

# ....................{ IMPORTS                            }....................
# Make it so, Captain Keats.
from the_blaze import the_splendour
