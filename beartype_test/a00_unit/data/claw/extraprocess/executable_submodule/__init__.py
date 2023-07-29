#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **executable submodule beartype import hook package initialization
submodule** (i.e., data module mimicking real-world usage of the
:func:`beartype.claw.beartype_this_package` import hook from a top-level
third-party package submodule ``{some_package}.__init__`).
'''

# ....................{ IMPORTS                            }....................
from beartype import BeartypeConf
from beartype.claw import beartype_this_package  # <-- boilerplate for victory
# print(f'__init__.__name__: {__name__}')
# print(f'__init__.__package__: {__package__}')

# ....................{ HOOKS                              }....................
# Install a beartype import hook for the current data subpackage directly
# containing this submodule, configured by the default beartype configuration.
beartype_this_package()
