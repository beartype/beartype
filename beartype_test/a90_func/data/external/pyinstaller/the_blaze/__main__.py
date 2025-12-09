#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**PyInstaller integration test data package entry point** (i.e., submodule
running the business logic performed for this package, validating that the
:mod:`beartype` package raises *no* unexpected exceptions when the third-party
PyInstaller framework bundles this package into an executable binary file).

Caveats
-------
**This entry point exists purely for local manual testing purposes only.** Since
PyInstaller itself currently fails to support entry points, this submodule
exists only to facilitate execution of this package by running the following
from the parent directory containing this package:

.. code-block:: bash

   python3 -m the_blaze
'''

# ....................{ IMPORTS                            }....................
# Make it so, Captain Keats.
from the_blaze import the_splendour
