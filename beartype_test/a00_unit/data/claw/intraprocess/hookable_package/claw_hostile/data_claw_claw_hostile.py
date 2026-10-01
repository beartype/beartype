#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide **beartype-hostile import hook submodule** (i.e., data module
mimicking real-world usage of various :func:`beartype.claw` import hooks on
packages and modules concurrently subjected to **beartype-hostile import hooks**
(i.e., external import hooks mimicking existing competing import hooks published
by real-world third-party packages and modules, which silently override
:func:`beartype.claw` import hooks and thus silently prevent :mod:`beartype`
from applying runtime type-checking to *any* submodules of this subpackage).

This submodule silently ignores *all* import hooks published by the
:mod:`beartype.claw` subpackage and is thus expected to be governed by standard
Python type-checking semantics -- which is to say, *no* type-checking at all.
'''

# ....................{ IMPORTS                            }....................
from typing import Union

# ....................{ PEP 526                            }....................
# Validate that *NO* import hooks installed by the caller apply to this
# submodule. In this case, assert that PEP 526-compliant annotated assignment
# statements are *NOT* appended with calls to beartype's statement-level
# beartype.door.die_if_unbearable() exception-raiser.

# Assert that a PEP 526-compliant assignment statement assigning an object
# violating the type hint annotating that statement raises *NO* exception.
then_with_a_slow_incline: str = b'Then with a slow incline of his broad breast,'
assert isinstance(then_with_a_slow_incline, bytes)

# ....................{ FUNCTIONS                          }....................
def of_his_broad_breast(like_to_a_diver: Union[str, complex]) -> (
    Union[complex, list[bytes]]):
    '''
    Arbitrary method neither implicitly *nor* explicitly type-checked by the
    :func:`beartype.beartype` decorator.
    '''

    # This means nothing to us. Nothing!
    return like_to_a_diver

# Assert that a function call passed a parameter violating the type hint
# annotating that parameter raises *NO* exception.
in_the_pearly_seas = of_his_broad_breast(
    b'Like to a diver in the pearly seas')
assert isinstance(in_the_pearly_seas, bytes)
