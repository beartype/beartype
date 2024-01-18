#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **beartype import hook** :pep:`526` **subpackage initialization
submodule** (i.e., data module mimicking real-world usage of various
:func:`beartype.claw` import hooks on :pep:`526`-compliant annotated variable
assignments).
'''

# ....................{ IMPORTS                            }....................
from beartype import BeartypeConf
from beartype.claw import beartype_package

#FIXME: Uncomment after "violation_door_type" exists, please.
# # Subject this single module to a beartype import hook configured to emit
# # non-fatal warnings rather than raise fatal exceptions.
# beartype_package(
#     'beartype_test.a00_unit.data.claw.intraprocess.hookable_package.pep.pep526.data_claw_pep526_warn',
#     conf=BeartypeConf(violation_door_type=UserWarning),
# )

from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.pep.pep526 import (
    data_claw_pep526_raise)

#FIXME: Uncomment after "violation_door_type" exists, please.
# from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.pep.pep526 import (
#     data_claw_pep526_warn)
