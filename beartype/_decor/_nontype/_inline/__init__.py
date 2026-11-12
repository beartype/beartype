#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype inline type-checking subpackage** (i.e., private subpackage binding
dynamically generated type-checkers directly into callables instrumented by the
:mod:`beartype.claw` abstract syntax tree (AST) transformer, rather than
wrapping those callables with an additional stack frame).

See issue #734 for further details.

This private subpackage is *not* intended for importation by downstream callers.
'''
