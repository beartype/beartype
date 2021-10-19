#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **unbounded cache** utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
# from beartype.roar._roarexc import _BeartypeUtilCacheException
from threading import Lock

# ....................{ CLASSES                           }....................
#FIXME: Implement us up, please. This class intentionally does *NOT* subclass
#"dict", which is too low-level for thread-safe caching. All public API methods
#of this class need to behave thread-safely. For example, the canonical caching
#method typically resembles:
#    def cache_entry(self, key: Hashable, value: object) -> object:
#        with self._lock:
#            if key in self._dict:
#                self._dict[key] = value
#            return self._dict[key]
#FIXME: Unit test us up, please.
class CacheUnboundedStrong(object):
    '''
    **Thread-safe strongly unbounded cache** (i.e., mapping of unlimited size
    from strongly referenced arbitrary keys onto strongly referenced arbitrary
    values, whose methods are guaranteed to behave thread-safely).

    Design
    ------
    Cache implementations typically employ weak references for safety.
    Employing strong references invites memory leaks by preventing objects
    *only* referenced by the cache (cache-only objects) from being
    garbage-collected. Nonetheless, this cache intentionally employs strong
    references to persist these cache-only objects across calls to callables
    decorated with :func:`beartype.beartype`. In theory, caching an object
    under a weak reference would result in immediate garbage-collection as,
    with no external strong referents, the object would get collected with all
    other short-lived objects in the first generation (i.e., generation 0).

    Attributes
    ----------
    _lock : Lock
        **Non-reentrant instance-specific thread lock** (i.e., low-level thread
        locking mechanism implemented as a highly efficient C extension,
        defined as an instance variable for non-reentrant reuse by the public
        API of this class). Although CPython, the canonical Python interpreter,
        *does* prohibit conventional multithreading via its Global Interpreter
        Lock (GIL), CPython still coercively preempts long-running threads at
        arbitrary execution points. Ergo, multithreading concerns are *not*
        safely ignorable -- even under CPython.
    '''

    # ..................{ CLASS VARIABLES                   }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # @beartype decorations. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        '_lock',
    )

    # ..................{ INITIALIZER                       }..................
    def __init__(self) -> None:
        '''
        Initialize this cache to an empty cache.
        '''

        # Initialize all remaining instance variables.
        self._lock = Lock()
