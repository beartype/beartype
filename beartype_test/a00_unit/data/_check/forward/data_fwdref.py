#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **forward reference proxy data** submodule.

This submodule predefines **forward reference proxies** (i.e., low-level objects
created by the :func:`beartype._check.forward.reference.fwdrefmake` submodule)
exercising known edge cases on behalf of higher-level unit test submodules.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.forward.reference.fwdrefmake import (
    make_forwardref_indexable_subtype)

# ....................{ GLOBALS                            }....................
FORWARDREF_RELATIVE_CIRCULAR = make_forwardref_indexable_subtype(
    # Fully-qualified name of the current test module.
    __name__,
    # Unqualified basename of this global currently being declared.
    'FORWARDREF_RELATIVE_CIRCULAR')
'''
**Circular forward reference proxy** (i.e., invalid proxy circularly and thus
recursively referring to the same forward reference proxy).

Since the only means of declaring a circular forward reference proxy is as a
global attribute, the declaration of this proxy is necessarily isolated to its
own data submodule.
'''
