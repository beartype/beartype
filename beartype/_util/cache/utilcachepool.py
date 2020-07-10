#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype key pool type** (i.e., object caching class implemented as a
dictionary of lists of arbitrary objects to be cached, where objects cached to
the same list are typically of the same type

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.cave import CallableTypes, HashableType
from collections import defaultdict

# ....................{ CLASSES                           }....................
#FIXME: Unit test us up.
class KeyPool(object):
    '''
    **Key pool** (i.e., object cache implemented as a dictionary of lists of
    arbitrary objects to be cached, where objects cached to the same list are
    typically of the same type).

    Caveats
    ----------
    For genericity, **key pools are not thread-safe.** Callers are thus advised
    to isolate global key pools behind either:

    * **Thread-local storage** (i.e., :class:`threading.local` namespaces),
      which maximize time-efficiency at a cost in space-consumption. Since
      `Python implements thread-local storage with platform-native support
      under all major platforms <thread-local storage nativity_>`__,
      thread-local storage is typically even faster to access than storage
      locked with the low-level :class:`threading.Lock` primitive.
    * **Thread-locking primitives** (e.g., :class:`threading.Lock`,
      :class:`threading.RLock`), which maximize space-efficiency at a cost in
      time-consumption.

    .. _thread-local storage nativity:
       https://stackoverflow.com/a/45315342/2809027

    Attributes
    ----------
    _key_to_pool : dict
        Dictionary mapping from **arbitrary keys** (i.e., hashable objects) to
        lists of zero or more arbitrary objects cached under those keys. For
        both efficiency and simplicity, this dictionary is defined as a
        :class:`defaultdict` implicitly initializing missing keys on initial
        access to the empty list.
    _pool_item_maker : CallableTypes
        Caller-defined factory callable internally called by the
        :meth:`acquire` method on attempting to acquire a non-existent object
        from an **empty pool. See :meth:`__init__` for further details.
    '''

    # ..................{ CLASS VARIABLES                   }..................
    # Slot *ALL* instance variables defined on this object to minimize space
    # and time complexity across frequently called @beartype decorations.
    __slots__ = ('_key_to_pool', '_pool_item_maker',)

    # ..................{ INITIALIZER                       }..................
    def __init__(self, pool_item_maker: CallableTypes) -> None:
        '''
        Initialize this key pool with the passed factory callable.

        Parameters
        ----------
        pool_item_maker : CallableTypes
            Caller-defined factory callable internally called by the
            :meth:`acquire` method on attempting to acquire a non-existent
            object from an **empty pool** (i.e., either a missing key *or* an
            empty list of an existing key of the underlying
            :attr:`_key_to_pool` dictionary). That method initializes the empty
            pool in question by calling this factory with the key associated
            with that pool and appending the object created and returned by
            this factory to that pool. This factory is thus expected to have a
            signature resembling:

            .. code-block:: python

               from beartype.cave import HashableType
               def pool_item_maker(key: HashableType) -> object: ...
        '''
        assert callable(pool_item_maker), '{!r} not callable.'.format(pool_item_maker)

        # Classify these parameters as instance variables.
        self._pool_item_maker = pool_item_maker

        # Initialize all remaining instance variables.
        self._key_to_pool = defaultdict(default_factory=lambda: [])

    # ..................{ ACQUIRERS                         }..................
    def acquire(self, key: HashableType) -> object:
        '''
        Acquire an arbitrary object associated with the passed **arbitrary
        key** (i.e., hashable object).

        Specifically, this method tests whether there exists a non-empty list
        previously associated with this key. If so, this method pops the last
        item from that list and returns that item; else (i.e., if there either
        exists no such list or such a list exists but is empty), this method
        effectively (in order):

        #. If no such list exists, creates a new empty list associated with
           this key.
        #. Creates a new object to be returned by calling the user-defined
           :meth:`_pool_item_maker` factory callable.
        #. Appends this object to this list.
        #. Returns this object.

        Parameters
        ----------
        key : HashableType
            Hashable object associated with the pool item to be acquired.

        Returns
        ----------
        object
            Pool item associated with this hashable object.

        Raises
        ----------
        TypeError
            If this key is unhashable and thus *not* a key.
        '''

        # List associated with this key.
        #
        # If this is the first access of this key, this "defaultdict"
        # implicitly creates a new list and associates this key with that list;
        # else, this is the list previously associated with this key.
        #
        # Note that this statement implicitly raises a "TypeError" exception if
        # this key is unhashable, which is certainly more efficient than our
        # explicitly validating this constraint.
        pool = self._key_to_pool[key]

        # Return...
        return (
            # A new object associated with this key...
            self._pool_item_maker(key)
            # If the list associated with this key is empty (i.e., this method
            # has been called more frequently than the corresponding release()
            # method for this key)...
            if not pool
            # Else, the list associated with this key is non-empty (i.e., this
            # method has been called less frequently than the corresponding
            # release() method for this key). In this case, pop (i.e., remove)
            # and return the last item from this list.
            else pool.pop()
        )


    def release(self, key: HashableType, pool_item: object) -> None:
        '''
        Release the passed object previously associated with the passed
        **arbitrary key** (i.e., hashable object) by a prior call to the
        :meth:`release` method passed the same key.

        Specifically, this method tests whether there exists a list
        previously associated with this key. If not, this method creates a new
        empty list associated with this key. In either case, this method then
        appends this object to this list.

        Parameters
        ----------
        key : HashableType
            Hashable object previously associated with this pool item.
        pool_item : object
            Arbitrary object previously associated with this key.

        Raises
        ----------
        TypeError
            If this key is unhashable and thus *not* a key.
        '''

        # The best things in life are free or one-liners. This is the latter.
        self._key_to_pool[key].append(pool_item)
