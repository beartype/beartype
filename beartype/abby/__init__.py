#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype functional type-checking API.**

This submodule provides an orthogonal API to that of the
:func:`beartype.beartype` decorator. Whereas that decorator is suitable *only*
for type-checking callable parameters and returns at call time, the functions
exported by this API are suitable for type-checking arbitrary objects at *any*
arbitrary time during the lifecycle of the active Python process.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ....................{ IMPORTS                           }....................
from beartype.abby._abbytest import (
    die_if_unbearable as die_if_unbearable,
    is_bearable as is_bearable,
)
