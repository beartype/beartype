#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **generic types data** submodule.

This submodule predefines low-level class constants exercising known edge
cases on behalf of higher-level unit test submodules.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDoorHintViolation
from beartype.typing import (
    Union,
)
from pytest import raises

# ....................{ PEP 526                            }....................
# Validate that the beartype_this_package() import hook installed by the parent
# "beartype_this_package.__init__" submodule implicitly appends all PEP
# 562-compliant annotated assignment statements in other submodules of this
# "beartype_this_package" subpackage with calls to beartype's statement-level
# beartype.door.die_if_unbearable() exception-raiser.

# Assert that a PEP 562-compliant assignment statement assigning an object
# satisfying the type hint annotating that statement raises *NO* exception.
#
# Note that this type hint is intentionally annotated as "float" rather than
# either "int" *OR* "Union[int, float]", exercising that that import hook
# successfully associated this and *ALL* other submodules of the
# "beartype_this_package" subpackage with a non-default beartype configuration
# enabling the PEP 484-compliant implicit numeric tower (i.e.,
# "is_pep484_tower=True").
loves_philosophy: float = len('The fountains mingle with the river')

# Assert that a PEP 562-compliant assignment statement assigning an object
# violating the type hint annotating that statement raises the expected
# exception.
with raises(BeartypeDoorHintViolation):
    and_the_rivers_with_the_ocean: Union[str, bytes] = (
        'The winds of heaven mix for ever')

# ....................{ CLASSES                            }....................
#FIXME: Implement us up, please.
