#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide **beartype-hostile import hook subpackage initialization submodule**
(i.e., data module mimicking real-world usage of various :func:`beartype.claw`
import hooks on packages and modules concurrently subjected to
**beartype-hostile import hooks** (i.e., external import hooks mimicking
existing competing import hooks published by real-world third-party packages and
modules, which silently override :func:`beartype.claw` import hooks and thus
silently prevent :mod:`beartype` from applying runtime type-checking to *any*
submodules of this subpackage)).
'''

# ....................{ IMPORTS                            }....................
from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.claw_hostile import (
    data_claw_claw_hostile)
