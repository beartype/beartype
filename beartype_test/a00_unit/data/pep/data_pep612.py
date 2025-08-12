#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`612` **data submodule.**
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import ParamSpec

# ....................{ TYPEARGS                           }....................
P = ParamSpec('P')
'''
Arbitrary :pep:`612`-compliant unbound parameter specification.
'''
