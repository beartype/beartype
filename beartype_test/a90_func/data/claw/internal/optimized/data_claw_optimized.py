#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide **import hookable Python optimization integration submodule** (i.e.,
data module defining various decoratable objects, which the
:mod:`beartype.beartype` decorator will then be applied to by
:func:`beartype.claw` import hooks only if the active Python interpreter is
unoptimized by either the ``-O`` command-line option *or* the
``${PYTHONOPTIMIZE}`` environment variable).
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDoorHintViolation
from beartype._util.py.utilpyinterpreter import is_python_optimized
from pytest import raises

# ....................{ PEP 526                            }....................
# This submodule intentionally tests type-checking violations *ONLY* with
# respect to PEP 526-compliant annotated variable assignments. This submodule
# does *NOT* bother testing type-checking violations with respect to either
# callables *OR* types. Why? Because prior unit tests have already validated the
# @beartype decorator to reduce to a noop when the active Python interpreter is
# optimized. The "beartype.claw" import hook type-checks callables and types by
# decorating those callables and types by the @beartype decorator. Ergo,
# re-testing callable and type decoration here would *NOT* unambiguously
# validate that import hooks reduce to a noop when the active Python interpreter
# is optimized. After all, regardless of whether import hooks correctly reduce
# to a noop, the @beartype decorator is already guaranteed to reduce to a noop.
#
# The *ONLY* means of unambiguously validating that import hooks themselves
# reduce to a noop is to type-check unique syntax *NOT* already decoratable by
# the @beartype decorator. PEP 526-compliant annotated variable assignments are
# that syntax. After all, you can't decorate an assignment. Not yet, anyway!

# If the active Python interpreter is optimized...
if is_python_optimized():
    # Implicitly assert that a similar call raises *NO* exception, exactly as
    # expected when the active Python interpreter is optimized.
    to_the_high_towers: int = "Jarr'd his own golden region; and before"
# Else, the active Python interpreter is optimized. In this case...
else:
    # Explicitly assert that the call to the beartype.door.die_if_unbearable()
    # function injected by the "beartype.claw" import hook *AFTER* this PEP
    # 526-compliant annotated variable assignment (whose assigned value violates
    # the hint annotating this assignment) raises the expected
    # @beartype-specific type-checking violation.
    with raises(BeartypeDoorHintViolation):
        and_from_the_basements_deep: int = (
            'And from the basements deep to the high towers')
