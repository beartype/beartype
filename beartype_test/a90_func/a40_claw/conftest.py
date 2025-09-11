#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.


'''
**Test configuration** (i.e., :mod:`pytest`-specific early-time configuration
guaranteed to be implicitly imported by :mod:`pytest` into *all* sibling and
child submodules of the test subpackage containing this :mod:`pytest` plugin).
'''

# ....................{ IMPORTS                            }....................
# Import all subpackage-specific fixtures implicitly required by tests defined
# by submodules of this subpackage.
from beartype_test.a90_func.a40_claw._clawfixture import clean_claws_func
