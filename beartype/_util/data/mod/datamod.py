#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **module globals** (i.e., global constants describing various
well-known modules and packages).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ NAMES                              }....................
MODULE_NAME_BUILTINS = 'builtins'
'''
Fully-qualified name of the **builtins module** (i.e., objects defined by the
standard :mod:`builtins` module and thus globally available by default
*without* requiring explicit importation).
'''

# ....................{ SETS                              }....................
#FIXME: Replace all usage of "HINT_PEP_MODULE_NAMES" with usage of this set;
#then excise the former, please.
MODULE_NAMES_HINT = frozenset((
    # Name of the official typing module bundled with the Python stdlib.
    'typing',
    # Name of the third-party "typing_extensions" module, backporting "typing"
    # hints introduced in newer Python versions to older Python versions.
    'typing_extensions',
))
'''
Frozen set of the fully-qualified names of all **hinting modules** (i.e.,
modules officially declaring attributes usable for creating PEP-compliant type
hints accepted by both static and runtime type checkers).
'''
