#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-compliant type hint globals** (i.e., global constants
pertaining to PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.data.hint.pep.proposal.datapep484 import (
    HINT_PEP484_ATTRS_DEPRECATED,
    # HINT_PEP484_ATTRS_ISINSTANCEABLE,
)
# from beartype._util.data.hint.pep.proposal.datapep585 import (
#     HINT_PEP585_ATTRS_ISINSTANCEABLE,
# )

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ MODULES                           }....................
HINT_PEP_MODULE_NAMES = frozenset((
    # Name of the official typing module bundled with the Python stdlib.
    'typing',

    # Name of the third-party "typing_extensions" module backporting "typing"
    # hints introduced in newer Python versions to older Python versions.
    'typing_extensions',
))
'''
Frozen set of the unqualified names of all top-level **hinting modules** (i.e.,
modules declaring attributes usable for creating PEP-compliant type hints
accepted by both static and runtime type checkers).
'''

# ....................{ TYPING                            }....................
#FIXME: Shift this frozen set into the "datapepattr" submodule.
#FIXME: Refactor all usage of this frozen set to test unsubscripted attributes
#rather than signs, whose meaning will now be entirely different.
HINT_PEP_ATTRS_DEPRECATED = (
    HINT_PEP484_ATTRS_DEPRECATED
)
'''
Frozen set of all **deprecated typing attributes** (i.e., :mod:`typing` type
hints obsoleted by more recent PEPs).
'''
