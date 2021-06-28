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
)

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

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
