#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **current package beartype import hook package initialization
submodule** (i.e., data module mimicking real-world usage of the
:func:`beartype.claw.beartype_this_package` import hook from a top-level
third-party package submodule ``{some_package}.__init__`).
'''

# ....................{ IMPORTS                            }....................
from beartype import BeartypeConf
from beartype.claw import beartype_this_package
# print(f'__init__.__name__: {__name__}')
# print(f'__init__.__package__: {__package__}')

# ....................{ HOOKS                              }....................
# Install a beartype import hook for the current data subpackage directly
# containing this submodule, configured by an arbitrary non-default beartype
# configuration to exercise that this hook correctly recursively applies this
# configuration to *ALL* submodules of this subpackage.
beartype_this_package(conf=BeartypeConf(is_pep484_tower=True))
# print(f'"beartype_this_package" conf id: {id(BeartypeConf(is_pep484_tower=True))}')
