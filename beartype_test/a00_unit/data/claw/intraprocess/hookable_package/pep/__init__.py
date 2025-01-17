#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype import hook Python enhancement proposal (PEP) subpackage
initialization submodule** (i.e., data module mimicking real-world usage of
various :func:`beartype.claw` import hooks on various PEPs).
'''

# ....................{ IMPORTS                            }....................
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12
from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.pep import (
    data_claw_pep557,
    pep526,
)

# If the active Python interpreter targets Python >= 3.12 and thus supports PEP
# 695...
if IS_PYTHON_AT_LEAST_3_12:
    # Defer version-specific imports.
    from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.pep import (
        data_claw_pep695)
# Else, this interpreter targets Python < 3.12 and thus fails to support PEP
# 695.
