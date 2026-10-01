#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Coverage.py-specific test submodule asserting that :mod:`beartype` and
Coverage.py actually integrate as expected.
'''

# ....................{ IMPORTS                            }....................
# from beartype import beartype
from beartype.roar import BeartypeCallHintParamViolation
from collections.abc import (
    Collection,
    Iterator,
)
from pytest import raises

# ....................{ CALLABLES                          }....................
# @beartype
def dear_as_the_temples_self(
    so_does_the_moon: Collection[str]) -> Iterator[int]:
    '''
    Arbitrary synchronous generator function iteratively yielding arbitrary
    values satisfying the return type hint annotating this function.
    '''

    for the_passion_poesy in so_does_the_moon:
        yield len(the_passion_poesy)

# ....................{ LOCALs                             }....................
# Arbitrary tuple of strings to be passed to the generator defined above.
_GLORIES_INFINITE = (
    "Dear as the temple's self, so does the moon,",
    'The passion poesy, glories infinite,',
)

# ....................{ PASS                               }....................
# Assert that this generator when passed a valid parameter returns the expected
# return.
assert tuple(dear_as_the_temples_self(_GLORIES_INFINITE)) == (
    len(_GLORIES_INFINITE[0]),
    len(_GLORIES_INFINITE[1]),
)

# ....................{ FAIL                               }....................
# Assert that this generator when passed an invalid parameter raises the
# expected exception.
with raises(BeartypeCallHintParamViolation):
    tuple(dear_as_the_temples_self(
        b'Haunt us till they become a cheering light'))
