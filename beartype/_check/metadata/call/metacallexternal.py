#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator call metadata dataclass** (i.e., class aggregating *all*
metadata for the callable currently being decorated by the
:func:`beartype.beartype` decorator).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.metadata.call.metacallabc import BeartypeCallMetaABC

# ....................{ SUBCLASSES                         }....................
#FIXME: Docstring us up, please. *sigh*
#FIXME: Implement us up, please. *sigh*
class BeartypeCallExternalMeta(BeartypeCallMetaABC):
    pass
