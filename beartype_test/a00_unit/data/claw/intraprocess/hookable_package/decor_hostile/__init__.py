#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide **beartype import hook decorator-hostile decorator subpackage
initialization submodule** (i.e., data module mimicking real-world usage of
various :func:`beartype.claw` import hooks on callables decorated by chains of
one or more **decorator-hostile decorators** (i.e., decorators hostile to other
decorators by prohibiting other decorators from being applied after they
themselves are applied in such a chain)).
'''

# ....................{ IMPORTS                            }....................
from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.decor_hostile import (
    data_claw_decor_hostile,
)
