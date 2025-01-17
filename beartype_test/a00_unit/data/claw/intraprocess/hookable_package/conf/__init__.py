#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype import hook configuration subpackage initialization submodule**
(i.e., data module mimicking real-world usage of various :func:`beartype.claw`
import hooks configured by different beartype configurations).
'''

# ....................{ IMPORTS                            }....................
from beartype import (
    BeartypeConf,
    BeartypeDecorationPosition,
)
from beartype.claw import beartype_package

# Subject this single module to a beartype import hook configured to inject the
# @beartype decorator first before (i.e., below) all other class decorators.
beartype_package(
    package_name=(
        'beartype_test.a00_unit.data.claw.intraprocess.hookable_package.conf.'
        'data_claw_conf_decoration_position_funcs_first'
    ),
    conf=BeartypeConf(
        claw_decoration_position_funcs=BeartypeDecorationPosition.FIRST),
)
from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.conf import (
    data_claw_conf_decoration_position_funcs_first)

# Subject this single module to a beartype import hook configured to inject the
# @beartype decorator first before (i.e., below) all other class decorators.
beartype_package(
    package_name=(
        'beartype_test.a00_unit.data.claw.intraprocess.hookable_package.conf.'
        'data_claw_conf_decoration_position_types_first'
    ),
    conf=BeartypeConf(
        claw_decoration_position_types=BeartypeDecorationPosition.FIRST),
)
from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.conf import (
    data_claw_conf_decoration_position_types_first)
