#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.


'''
:mod:`pytest` **DOOR test plugin** (i.e., early-time configuration guaranteed to
be run by :mod:`pytest` *after* passed command-line arguments are parsed).

:mod:`pytest` implicitly imports *all* functionality defined by this module
into *all* submodules of this subpackage.
'''

# ....................{ IMPORTS                            }....................
# Import all subpackage-specific fixtures implicitly required by tests defined
# by submodules of this subpackage.
from beartype_test.a00_unit.a60_api.door._doorfixture import (
    door_cases_equality,
    door_cases_subhint,
)
