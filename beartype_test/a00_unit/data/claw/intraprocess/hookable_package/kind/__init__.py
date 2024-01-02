#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **beartype import hook data type subpackage initialization
submodule** (i.e., data module mimicking real-world usage of various
:func:`beartype.claw` import hooks on various types of objects, including both
callables and non-callable containers).
'''

# ....................{ IMPORTS                            }....................
from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.kind import (
    data_claw_type,
    data_claw_func,
)
