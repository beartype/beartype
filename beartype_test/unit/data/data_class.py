#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype class data submodule.**

This submodule predefines low-level class constants exercising known edge
cases on behalf of higher-level unit test submodules.
'''

# ....................{ IMPORTS                           }....................
from argparse import ArgumentParser

# ....................{ CONSTANTS                         }....................
CLASSES_BUILTIN = frozenset((
    bool,
    complex,
    dict,
    float,
    frozenset,
    int,
    list,
    set,
    str,
    tuple,
))
'''
Frozen set of all **builtin types** i.e., globally accessible C-based type
requiring *no* explicit importation)(.
'''


CLASSES_NON_BUILTIN = frozenset((
    # Arbitrary non-builtin type.
    ArgumentParser,

    # Type of the "None" singleton, which constitutes an edge case due to being
    # globally inaccessible and thus effectively *NOT* builtin despite being
    # declared by the "builtins" module.
    type(None),
))
'''
Frozen set of arbitrary non-builtin types.
'''
