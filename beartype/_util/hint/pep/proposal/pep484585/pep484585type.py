#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **subclass type hint
utilities** (i.e., callables generically applicable to both :pep:`484`- and
:pep:`585`-compliant subclass type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.hint.datahintpep import Hint
from typing import (
    Any,
    Type as typing_Type,  # <-- intentional to distinguish from "type" below
)
