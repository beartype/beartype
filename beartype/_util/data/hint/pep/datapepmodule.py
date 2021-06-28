#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **typing module globals** (i.e., global constants pertaining to
modules declaring official PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ TUPLES                            }....................
HINT_PEP_MODULE_NAMES = ('typing', 'typing_extensions')
'''
Tuple of the names of all **typing modules** (i.e., modules whose attributes
are usable for creating PEP-compliant type hints officially accepted by both
static and runtime type checkers) regardless of whether those modules are
actually importable under the active Python interpreter.
'''
