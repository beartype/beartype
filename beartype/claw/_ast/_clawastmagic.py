#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **abstract syntax tree (AST) magic** (i.e., global singleton objects
embedded in various nodes of the currently visited AST).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from ast import (
    Load,
)

# ....................{ NODES                              }....................
NODE_CONTEXT_LOAD = Load()
'''
**Node context load singleton** (i.e., object suitable for passing as the
``ctx`` keyword parameter accepted by the ``__init__()`` method of various
abstract syntax tree (AST) node classes).
'''
