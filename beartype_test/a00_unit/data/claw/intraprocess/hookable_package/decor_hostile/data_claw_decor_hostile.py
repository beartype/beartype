#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide **beartype import hookable decorator-hostile decorator submodule**
(i.e., defining callables decorated by chains of one or more **decorator-hostile
decorators** (i.e., decorators hostile to other decorators by prohibiting other
decorators from being applied after they themselves are applied in such a chain)
into which the :mod:`beartype.beartype` decorator will be injected after the
last decorator-hostile decorator, mimicking real-world usage of the
:func:`beartype.claw.beartype_package` import hook from external callers).
'''

# ....................{ IMPORTS                            }....................
# Exercise all possible kinds of imports of this same decorator-hostile
# decorator.
from beartype_test.a00_unit.data.func.data_decor import decorator_hostile
from beartype.roar import BeartypeCallHintReturnViolation
from pytest import raises

# ....................{ FUNCTIONS                          }....................
# Validate that the import hook presumably registered by the caller implicitly
# injects the @beartype decorator *AFTER* the last decorator-hostile decorator
# in all chains of callable decorations.

@decorator_hostile
def roused_from_icy_trance() -> int:
    '''
    Arbitrary function trivially violating its return type hint, decorated by a
    decorator-hostile decorator function directly imported as an attribute from
    the submodule defining that function.
    '''

    return "Even now, while Saturn, rous'd from icy trance,"

# ....................{ FAIL                               }....................
# Assert that the import hook registered by the caller injected the @beartype
# decorator *AFTER* the last decorator-hostile decorator decorating callables
# defined above.
with raises(BeartypeCallHintReturnViolation):
    roused_from_icy_trance()
