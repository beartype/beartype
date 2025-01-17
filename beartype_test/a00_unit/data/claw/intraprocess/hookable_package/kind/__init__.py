#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **beartype import hook data type subpackage initialization
submodule** (i.e., data module mimicking real-world usage of various
:func:`beartype.claw` import hooks on various types of objects, including both
callables and non-callable containers).
'''

# ....................{ IMPORTS                            }....................
from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.kind import (
    # Intentionally exercise synchronous functions first. As the simplest form
    # of decoratable object supported by @beartype, synchronous functions form
    # the core backbone of @beartype. If @beartype fails to decorate even
    # synchronous functions, all hope is lost for less trivial decoration below.
    # there is *NO* hope for
    data_claw_func,

    # Intentionally exercise coroutines (i.e., asynchronous functions) next.
    # Although still simple, coroutines are slightly less trivial than
    # synchronous functions for @beartype to decorate.
    data_claw_coro,

    # Intentionally exercise types (i.e., user-defined classes) next. Types are
    # considerably higher-level and thus  less trivial than either synchronous
    # or asynchronous functions for @beartype to decorate.
    data_claw_type,
)
