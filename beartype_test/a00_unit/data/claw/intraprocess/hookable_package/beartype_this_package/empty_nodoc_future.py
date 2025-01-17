#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

# Semantically empty submodule containing only only zero or more whitespace
# characters zero or more inline comments, and one or more "from __future__"
# import statements -- exercising a pernicious edge case in AST transformation
# that actually happened and destroyed everything.

# Arbitrary "from __future__" import statement.
from __future__ import annotations
