#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **strongly unbounded cache** (i.e., mapping of unlimited size from
strongly referenced arbitrary keys onto strongly referenced arbitrary values,
whose methods are guaranteed to behave thread-safely) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._cache.cls.cacheclsabc import CacheABC
from beartype._data.kind.datakindiota import SENTINEL
from collections.abc import (
    Callable,
    Hashable,
)

# ....................{ SUBCLASSES                         }....................
#FIXME: Submit back to StackOverflow, preferably under this question:
#    https://stackoverflow.com/questions/1312331/using-a-global-dictionary-with-threads-in-python
class CacheVastStrong(CacheABC):
    '''
    **Thread-safe strongly unbounded cache** (i.e., mapping of unlimited size
    from strongly referenced arbitrary keys onto strongly referenced arbitrary
    values, whose methods are guaranteed to behave thread-safely).

    Design
    ------
    Cache implementations typically employ weak references for safety. Employing
    strong references invites memory leaks by preventing objects *only*
    referenced by the cache (cache-only objects) from being garbage-collected.
    Instances of this cache intentionally employ strong references to persist
    these cache-only objects across calls to callables decorated with
    :func:`beartype.beartype`. In theory, caching an object under a weak
    reference would result in immediate garbage-collection; with *no* external
    strong referents, that object would be garbage-collected with all other
    short-lived objects in the first generation (i.e., generation 0).

    Attributes
    ----------
    _key_to_value : dict[Hashable, object]
        Internal **backing store** (i.e., thread-unsafe dictionary of unlimited
        size mapping from strongly referenced arbitrary keys onto strongly
        referenced arbitrary values).
    _key_to_value_get : Callable
        The :meth:`self._key_to_value.get` method, classified for efficiency.
    _key_to_value_set : Callable
        The :meth:`self._key_to_value.__setitem__` dunder method, classified
        for efficiency.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # @beartype decorations. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        '_key_to_value',
        '_key_to_value_get',
        '_key_to_value_set',
    )

    # ..................{ INITIALIZER                        }..................
    def __init__(self, *args, **kwargs) -> None:
        '''
        Initialize this cache to an empty cache.

        Parameters
        ----------
        All parameters are passed as is to the superclass
        :meth:`CacheABC.__init__` constructor.
        '''

        # Initialize our superclass with all passed parameters.
        super().__init__(*args, **kwargs)

        # Initialize all instance variables.
        self._key_to_value: dict[Hashable, object] = {}
        self._key_to_value_get = self._key_to_value.get
        self._key_to_value_set = self._key_to_value.__setitem__

    # ..................{ GETTERS                            }..................
    def cache_or_get_cached_value(
        self,

        # Mandatory parameters.
        key: Hashable,
        value: object,

        # Hidden parameters, localized for negligible efficiency.
        _SENTINEL=SENTINEL,
    ) -> object:
        '''
        Non-dynamically associate the passed key with the passed value if this
        cache has yet to cache this key (i.e., if this method has yet to be
        passed this key) and, in any case, return the value now guaranteed to be
        associated with this key.

        This method is intentionally implemented as a distinct method from the
        sibling :meth:`cache_or_get_cached_func_return_arg` method. Why?
        Efficiency, which is the whole point of caching. If caching isn't
        efficient, there is *no* reason to even cache.

        Parameters
        ----------
        key : Hashable
            **Key** (i.e., arbitrary hashable object) to return the associated
            value of.
        value : object
            **Value** (i.e., arbitrary object) to associate with this key if
            this key has yet to be associated with any value.

        Returns
        -------
        object
            **Value** (i.e., arbitrary object) associated with this key.

        Raises
        ------
        TypeError
            If the passed key is unhashable.
        '''
        # assert isinstance(key, Hashable), f'{repr(key)} unhashable.'

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize with the
        # cache_or_get_cached_func_return_arg() method.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # Thread-safely...
        with self._lock:
            # Value previously cached under this key if any *OR* the sentinel
            # placeholder otherwise.
            value_old = self._key_to_value_get(key, _SENTINEL)

            # If this key has already been cached, return this value as is.
            if value_old is not _SENTINEL:
                return value_old
            # Else, this key has yet to be cached.

            # Cache this key with this value.
            self._key_to_value_set(key, value)

            # Return this value.
            return value


    #FIXME: Unit test us up.
    def cache_or_get_cached_func_return_arg(
        self,

        # Mandatory parameters.
        key: Hashable,
        value_factory: Callable[[object], object],
        arg: object,

        # Hidden parameters, localized for negligible efficiency.
        _SENTINEL=SENTINEL,
    ) -> object:
        '''
        Dynamically associate the passed key with the value returned by the
        passed **value factory** (i.e., caller-defined function accepting this
        key and returning the value to be associated with this key) if this
        cache has yet to cache this key (i.e., if this method has yet to be
        passed this key) and, in any case, return the value now guaranteed to be
        associated with this key.

        This method is intentionally implemented as a distinct method from the
        sibling :meth:`.cache_or_get_cached_value` method. Why?
        Efficiency, which is the whole point of caching. If caching isn't
        efficient, there is *no* reason to even cache.

        Caveats
        -------
        **This method intentionally avoids raising a** :exc:`TypeError` **when
        the passed key is unhashable.** If this key is unhashable, this method
        instead creates and returns a new value by calling the passed value
        factory function *without* attempting to cache that value. Although
        non-ideal, generality and stability is preferable to specificity and
        instability by unexpected exceptions.

        Parameters
        ----------
        key : Hashable
            **Key** (i.e., arbitrary hashable object) to return the associated
            value of.
        value_factory : Callable[[object], object]
            **Value factory** (i.e., caller-defined function accepting the
            passed ``arg`` object and dynamically returning the value to be
            associated with this key).
        arg : object
            Arbitrary object to be passed as is to this value factory.

        Returns
        -------
        object
            **Value** (i.e., arbitrary object) associated with this key.
        '''
        # assert isinstance(key, Hashable), f'{repr(key)} unhashable.'
        # assert callable(value_factory), f'{repr(value_factory)} uncallable.'

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize with the cache_or_get_cached_value() method.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # Attempt to...
        try:
            # Thread-safely...
            with self._lock:
                # Value previously cached under this key if any *OR* the
                # sentinel placeholder otherwise.
                value_old = self._key_to_value_get(key, _SENTINEL)

                # If this key has already been cached, return this value as is.
                if value_old is not _SENTINEL:
                    return value_old
                # Else, this key has yet to be cached.

                # New value created by this factory function, localized for
                # negligible efficiency to avoid the unnecessary subsequent
                # dictionary lookup.
                value = value_factory(arg)

                # Cache this key with this value.
                self._key_to_value_set(key, value)

                # Return this value.
                return value
        # If this key is unhashable...
        except TypeError:
            # Create and return a new value via this factory function *WITHOUT*
            # attempting to memoize. While non-ideal, generality and stability
            # is more ideal than raising a fatal exception.
            return value_factory(arg)

    # ..................{ CLEARERS                           }..................
    #FIXME: Unit test us up, please.
    def clear_cache(self) -> None:

        # Thread-safely...
        with self._lock:
            # Clear your head and be at peace, one-liner.
            self._key_to_value.clear()
