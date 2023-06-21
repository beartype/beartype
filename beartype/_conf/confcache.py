#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **configuration cache** (i.e., private dictionary singletons enabling
beartype configurations to be efficiently stored and retrieved based on various
criteria, including both by configuration parameters and object identifiers).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    TYPE_CHECKING,
    Dict,
)
from threading import Lock

# If we are currently being statically type-checked rather than run at runtime,
# explicitly notify the current static type-checker of the absolute locations of
# attributes referenced by fully-qualified forward references below. *rollseyes*
if TYPE_CHECKING:
    from beartype import BeartypeConf
# Else, avoid importing the "BeartypeConf" class. Why? Because doing so would
# cause a circular import dependency. *facepalm*

# ....................{ LOCKS                              }....................
beartype_conf_lock = Lock()
'''
**Non-reentrant beartype configuration thread lock** (i.e., low-level thread
locking mechanism implemented as a highly efficient C extension, defined as an
global for non-reentrant reuse elsewhere as a context manager).
'''

# ....................{ DICTIONARIES                       }....................
beartype_conf_args_to_conf: Dict[tuple, 'BeartypeConf'] = {}
'''
Non-thread-safe **beartype configuration parameter cache** (i.e., dictionary
mapping from the hash of each set of parameters accepted by a prior call of the
:meth:`BeartypeConf.__new__` instantiator to the unique :class:`BeartypeConf`
instance instantiated by that call).

Caveats
----------
**This cache is non-thread-safe.** However, since this cache is only used as a
memoization optimization, the only harmful consequences of a race condition
between threads contending over this cache is a mildly inefficient (but
otherwise harmless) repeated re-memoization of duplicate configurations.
'''
