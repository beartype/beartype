#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype import hook type hints** (i.e., PEP-compliant hints annotating
callables and classes declared throughout the :mod:`beartype.claw` subpackage,
either for compliance with :pep:`561`-compliant static type checkers like
:mod:`mypy` or simply for documentation purposes).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from ast import (
    # AST,
    # AnnAssign,
    AsyncFunctionDef,
    # Call,
    # Expr,
    FunctionDef,
    # ImportFrom,
    # Load,
    # Module,
    # Name,
    # NodeTransformer,
    # Str,
    # alias,
)
from beartype.typing import (
    # Optional,
    Union,
)

# ....................{ HINTS ~ ast                        }....................
NodeCallable = Union[FunctionDef, AsyncFunctionDef]
'''
PEP-compliant type hint matching a **callable node** (i.e., node of the abstract
syntax tree (AST) describing the currently transformed submodule signifying the
definition of a pure-Python function or method that is either synchronous or
asynchronous).
'''
