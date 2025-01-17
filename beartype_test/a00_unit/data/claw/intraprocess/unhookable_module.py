#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **current package beartype import hook unhookable module** (i.e.,
data module *not* whitelisted by any import hooks published by the
:mod:`beartype.claw` subpackage and thus expected to be governed by standard
Python type-checking semantics -- which is to say, *no* type-checking at all).

Note that **unhooking** (i.e., *not* whitelisting) is *not* quite the same thing
as **skipping** (i.e., blacklisting). Unhooking is simply the absence of
actively whitelisting; skipping is the action of actively blacklisting.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    List,
    Union,
)

# from beartype.claw._importlib.clawimpcache import module_name_to_beartype_conf
# print(f'this_submodule conf: {repr(module_name_to_beartype_conf)}')

# ....................{ PEP 526                            }....................
# Validate that *NO* import hooks installed by the caller apply to this
# submodule. In this case, assert that PEP 526-compliant annotated assignment
# statements are *NOT* appended with calls to beartype's statement-level
# beartype.door.die_if_unbearable() exception-raiser.

# Assert that a PEP 526-compliant assignment statement assigning an object
# violating the type hint annotating that statement raises *NO* exception.
and_winter_robing: str = b'And winter robing with pure snow and crowns'
assert isinstance(and_winter_robing, bytes)

# ....................{ FUNCTIONS                          }....................
def of_starry_ice(the_grey_grass_and_bare_boughs: Union[str, complex]) -> (
    Union[complex, List[bytes]]):
    '''
    Arbitrary method neither implicitly *nor* explicitly type-checked by the
    :func:`beartype.beartype` decorator.
    '''

    # This means nothing to us. Nothing!
    return the_grey_grass_and_bare_boughs

# Assert that a function call passed a parameter violating the type hint
# annotating that parameter raises *NO* exception.
voluptuous_pantings = of_starry_ice(
    b"If spring's voluptuous pantings when she breathes")
assert isinstance(voluptuous_pantings, bytes)
