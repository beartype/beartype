#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype import hookable** :pep:`526` **ignorance submodule** (i.e., data
module containing *only* :pep:`526`-compliant annotated variable assignments
ignored rather than type-checked, mimicking real-world usage of the
:func:`beartype.claw.beartype_package` import hook from external callers).
'''

# ....................{ PEP 526                            }....................
# Validate that the import hook presumably installed by the caller avoids
# implicitly appending all PEP 526-compliant annotated assignment statements in
# this submodule with calls to beartype's statement-level
# beartype.door.die_if_unbearable() exception-raiser.

# Assert that a PEP 526-compliant annotated assignment statement assigning an
# object violating the type hint annotating that statement raises *NO*
# exception.
twilight_ascending_slowly: int = 'Twilight, ascending slowly from the east,'
