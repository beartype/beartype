#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Cecil Curry.
# See "LICENSE" for further details.

"""
**Beartype Least Recently Used (LRU) caching utilities.**

This private submodule implements supplementary cache-specific utility
functions required by various :mod:`beartype` facilities, including callables
generated by the :func:`beartype.beartype` decorator.

This private submodule is *not* intended for importation by downstream callers.
"""
# ....................{ IMPORTS                           }....................
from threading import Lock
from typing import Hashable, Union
from beartype.roar import _BeartypeUtilLRUCacheException

# ....................{ CLASSES                           }....................
class LRUCacheStrong(dict):
    """
    **Thread-safe strong Least Recently Used (LRU) cache**: A mapping
    from strong referenced arbitrary keys onto strong referenced arbitrary
    values, limited to some maximum capacity of key-value pairs which is
    implicitly and thread-safely enforced.

    Design
    ------
    LRU cache implementations typically employ weak references for safety;
    Employing strong references invites memory leaks via preventing objects
    *only* referenced by the cache (cache-only objects) from being garbage-collected.
    Nonetheless, this cache intentionally employs strong references to persist
    these cache-only objects across calls to callables decorated with :func:`beartype.beartype`.
    In theory, caching an object under a weak reference would result in immediate
    garbage-collection as, with no external strong referents, the object would
    get collected with all other short-lived objects in the first generation (i.e., generation 0).

    Notes
    -----
     - The equivalent LRU cache employing weak references to keys and/or values
       may be trivially implemented by swapping this classes inheritance from the
       builtin :class:`dict` to either of the builtin :class:`weakref.WeakKeyDictionary`
       or :class:`weakref.WeakValueDictionary`.

     - The standard example of a cache-only object is a container iterator - :meth:`dict.items`

    Attributes
    ----------
    _size : int
        **Cache capacity** - maximum number of key-value pairs persisted by this cache.
    _lock : Lock
        **Instance-specific thread lock** - a low-level thread locking mechanism
        implemented as a highly efficient C extension, defined as an instance
        variable for non-reentrant reuse by the public API of this class.

        Although the canonical Python interpreter - CPython - prohibits conventional
        multithreading via its Global Interpreter Lock, it still coercively
        preempts long-running threads at arbitrary execution points.
        Ergo, multithreading concerns are *not* safely ignorable.
    """

    # ..................{ CLASS VARIABLES                   }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # cache dunder methods. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        '_size',
        '_lock',
    )

    # ..................{ DUNDERS                           }..................
    def __init__(self, size: int) -> None:
        """
        Initialize this cache to an empty cache with a capacity of this size.

        Parameters
        ----------
        size : int
            **Cache capacity** (i.e., maximum number of key-value pairs held in this cache).

        Raises
        ------
        _BeartypeUtilLRUCacheException:
            If the capacity is *not* an integer or its a **non-positive integer** (i.e. Less than 1)
        """
        if not isinstance(size, int):
            raise _BeartypeUtilLRUCacheException(
                f'LRU cache capacity {repr(size)} not integer.')
        elif size < 1:
            raise _BeartypeUtilLRUCacheException(
                f'LRU cache capacity {size} not positive.')

        super().__init__()
        self._size = size
        self._lock = Lock()

    def __getitem__(self,
                    key: Hashable,

                    # Superclass methods efficiently localized as default parameters.
                    __contains=dict.__contains__,
                    ) -> object:
        """
        Returns item previously cached under the passed key otherwise raises an exception.

        Parameters
        ----------
        key : Hashable
            Arbitrary hashable key to retrieve the cached value of.

        Returns
        ----------
        object
            Arbitrary value cached under this key.

        Raises
        ----------
        TypeError
            If this key is not hashable.
        KeyError
            If this key isn't cached.

        Note
        ----
         - **Practically** identical to :meth:`self.__contains__` but one
           critical component disables a direct call to :meth:`self._push`:
           raise an error if there is no value associated with the key.
        """
        with self._lock:
            # Implicitly raises TypeError
            if __contains(self, key):
                # Pop, push, and return the associated value.
                return self._push(key)
            raise KeyError(f'Key Error: {key}')

    def __setitem__(self,
                    key: Hashable,
                    value: object
                    ) -> None:
        """
        Cache this key-value pair while preserving size constraints.

        Parameters
        ----------
        key : Hashable
            Arbitrary hashable key to cache this value to.
        value : object
            Arbitrary value to be cached under this key.

        Raises
        ----------
        TypeError
            If this key is not hashable.
        """
        with self._lock:
            self._push(key, value)

    def __contains__(self,
                     key: Hashable,
                     # Superclass methods efficiently localized as default parameters.
                     __contains=dict.__contains__,
                     __getitem=dict.__getitem__,
                     ) -> bool:
        """
        Returns a boolean indicating whether this key is cached.

        If this key is cached, it's popped and pushed back into the cache.

        Parameters
        ----------
        key : Hashable
            Arbitrary hashable key to detect the existence of.

        Returns
        ----------
        bool
            ``True`` if this key is cached otherwise ```False```

        Raises
        ----------
        TypeError
            If this key is unhashable.
        """
        with self._lock:
            if __contains(self, key):
                self._push(key)
                return True
            return False

    def _push(self,
              key: Hashable,
              value: Union[object, None] = None,

              # Superclass methods efficiently localized as default parameters.
              __contains=dict.__contains__,
              __get=dict.__getitem__,
              __delete=dict.__delitem__,
              __push=dict.__setitem__,
              __iter=dict.__iter__,
              __len=dict.__len__,
              ) -> object:
        """
        Add this key,value pair to the end of the cache.

        This method is meant to be called from within a threading.Lock context manager:
        this private method is non-thread safe by design.

        Parameters
        ----------
        key : Hashable
            Arbitrary hashable key to cache this value to.
        value : object
            Arbitrary value to be cached under this key.

        Raises
        --------
        TypeError
            If this key is not hashable.
        """
        # Remove association from mapping; Implicitly raises TypeError
        if __contains(self, key):
            if value is None:
                value = __get(self, key)
            __delete(self, key)

        __push(self, key, value)

        # Prune the cache
        if __len(self) > self._size:
            __delete(self, next(__iter(self)))

        return value
