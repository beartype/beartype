#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype import hook** :pep:`526` **subpackage initialization submodule**
(i.e., data module mimicking real-world usage of various :func:`beartype.claw`
import hooks on :pep:`526`-compliant annotated variable assignments).
'''

# ....................{ IMPORTS                            }....................
from beartype import BeartypeConf
from beartype.claw import beartype_package
from beartype.roar import BeartypeValeLambdaWarning
from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.pep.pep526 import (
    data_claw_pep526_raise)

# Subject this single module to a beartype import hook configured to silently
# ignore (rather than type-check) all PEP 526-compliant annotated assignments.
beartype_package(
    'beartype_test.a00_unit.data.claw.intraprocess.hookable_package.pep.pep526.data_claw_pep526_ignore',
    conf=BeartypeConf(claw_is_pep526=False),
)
from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.pep.pep526 import (
    data_claw_pep526_ignore)

# Subject this single module to a beartype import hook configured to emit
# non-fatal warnings of an arbitrary beartype-specific warning type unlikely to
# arise via accidental change rather than raise fatal exceptions.
beartype_package(
    'beartype_test.a00_unit.data.claw.intraprocess.hookable_package.pep.pep526.data_claw_pep526_warn',
    conf=BeartypeConf(violation_door_type=BeartypeValeLambdaWarning),
)
from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.pep.pep526 import (
    data_claw_pep526_warn)
