#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Coverage-specific test placeholder submodule whose only purpose is simply to
exist and which thus defines *no* meaningful content.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDoorHintViolation

# ....................{ CHECKS                             }....................
# Validate that the beartype-specific "BeartypeSourceFileLoader" subclass
# installed by the "beartype.claw" import hook registered by the sibling
# "dismal_rack_of_clouds.__init__" submodule has preserved type-checking in
# user-defined submodules (like this one), which *SHOULD* reside outside the
# purview of the recursion guard implemented by that subclass. One means of
# validating that that subclass has implemented its recursion guard improperly
# is to detect if this user-defined submodule is no longer type-checked.

# True only if the "beartype.claw" import hook registered by the sibling
# "dismal_rack_of_clouds.__init__" submodule is still active, defaulting to
# false for safety.
is_beartype_claw_active = False

# Attempt to assign an arbitrary value violating the arbitrary type hint
# annotating an arbitrary global variable in a PEP 526-compliant annotated
# variable assignment. If the "beartype.claw" import hook registered by the
# sibling "dismal_rack_of_clouds.__init__" submodule is still active, then this
# assignment will raise the expected "BeartypeDoorHintViolation" exception.
try:
    upon_the_boundaries: str = b'Upon the boundaries of day and night,'
# If the above assignment raises the expected "BeartypeDoorHintViolation"
# exception, note that the "beartype.claw" import hook registered by the sibling
# "dismal_rack_of_clouds.__init__" submodule remains active.
except BeartypeDoorHintViolation:
    is_beartype_claw_active = True

# If the "beartype.claw" import hook registered by the sibling
# "dismal_rack_of_clouds.__init__" submodule is no longer active, raise an
# arbitrary non-beartype exception to induce integration test failure.
if not is_beartype_claw_active:
    raise ValueError(
        '"beartype.claw"-based type-checking erroneously disabled.')
# Else, the "beartype.claw" import hook registered by the sibling
# "dismal_rack_of_clouds.__init__" submodule is still active.
