#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **beartype import hookable** :pep:`526` **submodule** (i.e., data
module containing *only* :pep:`526`-compliant annotated variable assignments,
mimicking real-world usage of the :func:`beartype.claw.beartype_package` import
hook from an external caller).
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDoorHintViolation
from beartype.typing import (
    List,
    Union,
)
from pytest import raises

# Import another submodule of this subpackage implicitly installing another
# import hooks configured by another beartype configuration isolated to that
# submodule. Doing so exercises that beartype import hooks correctly support
# import hook composition (i.e., combinations of arbitrary import hooks).
from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.beartype_this_package import (
    this_submodule)

# from beartype.claw._clawstate import claw_state
# print(f'this_submodule conf: {repr(claw_state.module_name_to_beartype_conf)}')

# ....................{ PEP 526                            }....................
# Validate that the import hook presumably installed by the caller implicitly
# appends all PEP 562-compliant annotated assignment statements in this
# submodule with calls to beartype's statement-level
# beartype.door.die_if_unbearable() exception-raiser.

# Assert that a PEP 562-compliant annotated assignment statement assigning an
# object satisfying the type hint annotating that statement raises *NO*
# exception.
and_winter_robing: int = len('And winter robing with pure snow and crowns')

# Assert that a PEP 562-compliant annotated statement lacking an assignment
# raises *NO* exception.
such_magic_as_compels_the_charmed_night: str

# Assert that a PEP 562-compliant annotated assignment statement assigning an
# object violating the type hint annotating that statement raises the expected
# exception.
with raises(BeartypeDoorHintViolation):
    of_starry_ice: Union[float, List[str]] = len(
        'Of starry ice the grey grass and bare boughs;')
