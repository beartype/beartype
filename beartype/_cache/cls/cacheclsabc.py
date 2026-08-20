#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **thread-safe cache abstract base classes (ABCs)** (i.e.,
superclasses of all concrete subclasses implementing mappings intended to be
instantiated as global thread-safe key-value caches).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from abc import abstractmethod
from beartype._data.cls.dataclsslot import BeartypeSlottedABCMeta
from contextlib import AbstractContextManager
from threading import (
    Lock,
    RLock,
)
from typing import (
    TYPE_CHECKING,
    Union,
)

# ....................{ SUPERCLASSES                       }....................
class CacheABC(metaclass=BeartypeSlottedABCMeta):
    '''
    **Thread-safe cache abstract base class (ABC)** (i.e., superclass of all
    concrete subclasses implementing mappings intended to be instantiated as
    global thread-safe key-value caches).

    This ABC intentionally does *not* adhere to standard mapping semantics by
    subclassing a standard mapping API (e.g., :class:`dict`,
    :class:`collections.abc.MutableMapping`). Standard mapping semantics are
    sufficiently low-level as to invite race conditions between competing
    threads concurrently contesting the same instance of this class. For
    example, consider the following standard non-atomic logic for caching a new
    key-value into an instance of a concrete subclass of this cache:

    .. code-block:: python

       if key not in cache:    # <-- If a context switch happens immediately
                               # <-- after entering this branch, bad stuff!
           cache[key] = value  # <-- We may overwrite another thread's work.

    This ABC and *all* subclasses thereof unconditionally perform thread-safe
    locking, even non-free-threaded CPython builds. Although those builds *do*
    prohibit conventional multithreading via its Global Interpreter Lock (GIL),
    those builds still coercively preempt long-running threads at arbitrary
    execution points. Multithreading concerns are thus *never* safely ignorable.

    Attributes
    ----------
    _lock : AbstractContextManager
        **Instance-specific thread lock** (i.e., low-level thread locking
        mechanism implemented as a highly efficient C extension).
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # @beartype decorations. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        '_lock',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        _lock: AbstractContextManager

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,

        # Optional parameters.
        lock_type: type[Union[Lock, RLock]] = Lock,
    ) -> None:
        '''
        Initialize this cache to an empty cache.

        Parameters
        ----------
        lock_type : type[Lock | RLock], default: Lock
            Type of thread-safe lock to internally use. Defaults to
            :class:`.Lock` (i.e., the type of the standard non-reentrant lock)
            for efficiency.
        '''
        assert lock_type in _LOCK_TYPES, (
            f'{repr(lock_type)} neither '
            f'"threading.Lock" nor "threading.RLock".'
        )

        # Initialize all instance variables.
        self._lock = lock_type()  # type: ignore[assignment]

    # ..................{ PROPERTIES                         }..................
    # This property is read-only and thus intentionally lacks a setter. \o/
    @property
    def lock(self) -> AbstractContextManager:
        '''
        Read-only **instance-specific thread lock** (i.e., low-level thread
        locking mechanism implemented as a highly efficient C extension).
        '''

        # Raven beast: one-liner summons a searing struggle!
        return self._lock

    # ..................{ CLEARERS                           }..................
    @abstractmethod
    def clear_cache(self) -> None:
        '''
        Clear (i.e., empty) this cache of all previously cached key-value pairs.

        This method is intentionally named distinctly from the standard
        :meth:`dict.clear` method. Doing so serves as a trivial guard against
        erroneously calling that non-thread-safe method against low-level
        :class:`dict` instances rather than calling this thread-safe method
        against thread-safe instances of this superclass.

        This method is thread-safe.
        '''

        pass

# ....................{ PRIVATE                            }....................
_LOCK_TYPES = frozenset((Lock, RLock,))
'''
Frozen set of all **thread-locking types** (i.e., standard context managers
acting as low-level thread-locking primitives).
'''
