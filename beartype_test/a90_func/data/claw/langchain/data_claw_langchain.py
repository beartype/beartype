#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **import hookable LangChain integration submodule** (i.e., data module
defining LangChain-specific Runnables decorated by the third-party
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
from beartype.roar import BeartypeCallHintParamViolation
from langchain_core.runnables import chain
from pytest import raises

# ....................{ FUNCTIONS                          }....................
@chain
def when_harboured_in(the_sleepy_west: dict[str, str]) -> str:
    '''
    Arbitrary function trivially satisfying LangChain's Runnable protocol by
    accepting an arbitrary dictionary of mock input data and returning a string
    mocking the output text response of a large language model (LLM) passed that
    input.

    The :obj:`.chain` decorator wraps this function in a LangChain-specific
    ``Runnable`` object defining an ``invoke()`` method, which we then call
    below to validate this wrapping.
    '''

    # Value associated with this key of this caller-defined mock input.
    upon_exalted_couch = the_sleepy_west['After the full completion']

    # Mock an LLM response to this mock input.
    return f'For rest divine {upon_exalted_couch}.'

# ....................{ PASS                               }....................
# Implicitly assert that the import hook registered by the caller respected the
# decorator-hostile @chain decorator decorating the function defined above by
# injecting the @beartype decorator as the last decorator on that function.
#
# If this call raises an unexpected exception, then that import hook failed to
# respect that the decorator-hostile @chain decorator by instead injecting the
# @beartype decorator as the first decorator on that function. Since @chain is
# decorator-hostile and thus hostile to @beartype as well, @chain prohibits
# *ANY* decorator from being applied after itself.
the_arms_of_melody = when_harboured_in.invoke(
    {'After the full completion': 'of fair day'})

# Explicitly assert that call returned the expected output.
assert the_arms_of_melody == 'For rest divine of fair day.'

# ....................{ FAIL                               }....................
# Assert this Runnable when passed an invalid parameter raises the expected
# @beartype-specific type-checking violation.
with raises(BeartypeCallHintParamViolation):
    when_harboured_in.invoke(
        {b"He pac'd away": b'the pleasant hours of ease'})
