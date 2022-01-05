#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
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
BUILTINS_MODULE_NAME = 'builtins'
'''
Fully-qualified name of the **builtins module** (i.e., objects defined by the
standard :mod:`builtins` module and thus globally available by default
*without* requiring explicit importation).
'''

# ....................{ SETS                              }....................
TYPING_MODULE_NAMES = frozenset((
    # Name of the official typing module bundled with the Python stdlib.
    'typing',
    # Name of the third-party "typing_extensions" module, backporting "typing"
    # hints introduced in newer Python versions to older Python versions.
    'typing_extensions',
))
'''
Frozen set of the fully-qualified names of all **typing modules** (i.e.,
modules officially declaring attributes usable for creating PEP-compliant type
hints accepted by both static and runtime type checkers).
'''


TYPING_MODULE_NAMES_DOTTED = frozenset(
    f'{typing_module_name}.' for typing_module_name in TYPING_MODULE_NAMES)
'''
Frozen set of the fully-qualified ``.``-suffixed names of all typing modules.

This set is a negligible optimization enabling callers to perform slightly more
efficient testing of string prefixes against items of this specialized set than
those of the more general-purpose :data:`TYPING_MODULE_NAMES` set.

See Also
----------
:data:`TYPING_MODULE_NAMES`
    Further details.
'''
