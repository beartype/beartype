#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **current package beartype import hook skippable module** (i.e.,
data module blacklisted by one or more import hooks published by the
:mod:`beartype.claw` subpackage and thus expected to *not* be type-checked by
the :func:`beartype.beartype` decorator).
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    List,
    Union,
)

# ....................{ PEP 526                            }....................
# Validate that *NO* import hooks installed by the caller apply to this
# submodule. In this case, assert that PEP 526-compliant annotated assignment
# statements are *NOT* appended with calls to beartype's statement-level
# beartype.door.die_if_unbearable() exception-raiser.

# Assert that a PEP 526-compliant assignment statement assigning an object
# violating the type hint annotating that statement raises *NO* exception.
in_most_familiar_cadence: str = b'In most familiar cadence, with the howl'
assert isinstance(in_most_familiar_cadence, bytes)

# ....................{ FUNCTIONS                          }....................
def with_the_howl(the_thunder_and_the_hiss: Union[str, complex]) -> (
    Union[complex, List[bytes]]):
    '''
    Arbitrary method neither implicitly *nor* explicitly type-checked by the
    :func:`beartype.beartype` decorator.
    '''

    # This means nothing to us. Nothing!
    return the_thunder_and_the_hiss

# Assert that a function call passed a parameter violating the type hint
# annotating that parameter raises *NO* exception.
of_homeless_streams = with_the_howl(
    b'The thunder and the hiss of homeless streams')
assert isinstance(of_homeless_streams, bytes)
