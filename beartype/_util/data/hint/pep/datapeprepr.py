#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **bare PEP-compliant type hint representations** (i.e., global
constants pertaining to machine-readable strings returned by the :func:`repr`
builtin suffixed by *no* "["- and "]"-delimited subscription representations).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.data.hint.pep.proposal.datapep484 import (
    HINT_PEP484_BARE_ATTRS_DEPRECATED)

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ SETS                              }....................
HINT_PEP_BARE_REPRS_DEPRECATED = (
    HINT_PEP484_BARE_REPRS_DEPRECATED
)
'''
Frozen set of all **bare deprecated PEP-compliant type hint representations**
(i.e., machine-readable strings returned by the :func:`repr` builtin suffixed
by *no* "["- and "]"-delimited subscription representations for all obsoleted
hints, often by equivalent hints standardized under more recent PEPs).
'''

# ....................{ TUPLES                            }....................
HINT_PEP_MODULE_NAMES = ('typing', 'typing_extensions')
'''
Tuple of the names of all **typing modules** (i.e., modules declaring official
PEP-compliant type hints) regardless of whether those modules are actually
importable under the active Python interpreter.
'''
