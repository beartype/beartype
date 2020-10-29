#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype conditional** :mod:`typing` **imports** (i.e., attributes only
conditionally importable from the stdlib :mod:`typing` module depending on the
active Python environment).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.utilobject import Iota
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_9,
)

# ....................{ IMPORTS ~ conditional             }....................
# Imports conditionally dependent on the major version of Python targeted by
# the active Python interpreter, falling back to a unique minimally small
# placeholder under older versions.

#FIXME: Currently unused and possibly fragile.
# if IS_PYTHON_AT_LEAST_3_9:
#     from typing import Annotated
# else:
#     Annotated = Iota()
