#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide **import hookable CrossHair integration submodule** (i.e., data module
defining CrossHair-specific Runnables decorated by the third-party
decorator-hostile :func:`langchain_core.runnables.chain` decorator which the
:mod:`beartype.beartype` decorator will then be injected *after* rather than
*before* as the earliest decorator, mimicking real-world usage of
:func:`beartype.claw` import hooks from external callers).

See Also
--------
https://github.com/beartype/beartype/issues/541
    StackOverflow issue exercised by this submodule.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeCallHintReturnViolation
from pytest import raises

# ....................{ CONSTANTS                          }....................
_TRIGGER_BEARTYPE = 0xCAFEBABE
'''
Arbitrary magic constant that, when passed to the :func:`.increment_int`
function defined below should trigger a :mod:`beartype` violation.
'''


_TRIGGER_CROSSHAIR = 0xFEEDFACE
'''
Arbitrary magic constant that, when passed to the :func:`.increment_int`
function defined below should trigger a CrossHair violation.
'''

# ....................{ FUNCTIONS                          }....................
def increment_int(integer: int) -> int:
    '''
    The passed integer possibly incremented by one.

    This decremented by one, thus violating the
    CrossHair-specific post condition constraining this function.

    This trivial function is intentionally:

    * Constrained by a CrossHair-specific post condition, declared below in this
      docstring. Don't ask. We didn't.
    * Implemented in a buggy manner so as to exercise third-party support for
      CrossHair in :mod:`beartype`, such that both remain capable of
      concurrently validating this function.

    post: __return__ > integer
    '''

    # If the passed parameter is this arbitrary magic constant, intentionally
    # erroneously decrement rather than increment this integer. In theory, doing
    # so *SHOULD* trigger a CrossHair violation.
    if integer == _TRIGGER_CROSSHAIR:
        return integer - 1
    # If the passed parameter is this other arbitrary magic constant,
    # intentionally erroneously return a string rather than integer. In theory,
    # doing so *SHOULD* trigger a beartype violation.
    elif integer == _TRIGGER_BEARTYPE:
        return str(integer)
    # Else, the passed parameter is any other integer.

    # Return this integer incremented, satisfying both CrossHair and beartype.
    return integer + 1

# ....................{ PASS                               }....................
# Assert that this function successfully increments *ANY* arbitrary integer
# except those intentionally triggering violations in CrossHair or beartype.
assert increment_int(0) == 1

# ....................{ FAIL                               }....................
# Assert that this function when passed the beartype-specific trigger raises the
# expected @beartype-specific type-checking violation.
with raises(BeartypeCallHintReturnViolation):
    increment_int(_TRIGGER_BEARTYPE)

#FIXME: Doesn't seem to do anything. CrossHair doesn't appear to be raising
#exceptions. No idea what that package is even doing. *LOLBRO*
# Assert that this function when passed the CrossHair-specific trigger raises
# the expected CrossHair-specific constraint-checking violation.
# with raises(BeartypeCallHintParamViolation):
increment_int(_TRIGGER_CROSSHAIR)
