#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Coverage-specific test package requiring registering the standard
:func:`beartype.claw.beartype_this_package` import hook, leveraged by
coverage-specific integration tests to guarantee that coverage continues to
support third-party packages registering a similar hook.
'''

# ....................{ IMPORTS                            }....................
from beartype.claw import beartype_this_package

# ....................{ HOOKS                              }....................
# Register the standard "beartype.claw" import hook. ARE YOU NOT ENTERTAINED!?
beartype_this_package()
