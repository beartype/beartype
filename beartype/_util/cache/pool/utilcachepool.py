#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype key pool type** (i.e., object caching class implemented as a
dictionary of lists of arbitrary objects to be cached, where objects cached to
the same list are typically of the same type).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................

# ....................{ IMPORTS                           }....................
from collections import defaultdict
from threading import Lock

from beartype.roar import _BeartypeUtilKeyPoolException
# ....................{ CLASSES                           }....................
class KeyPool(object):
    '''
    Thread-safe **key pool** (i.e., object cache implemented as a dictionary of
    lists of arbitrary objects to be cached, where objects cached to the same
    list are typically of the same type).

    Key pools are thread-safe by design and thus safely usable as module-scoped
    globals accessed from module-scoped callables.

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
    _thread_lock : Lock
        **Non-reentrant instance-specific thread lock** (i.e., low-level thread
        locking mechanism implemented as a highly efficient C extension,
        defined as an instance variable for non-reentrant reuse by the public
        API of this class). Although CPython, the canonical Python interpreter,
        *does* prohibit conventional multithreading via its Global Interpreter
        Lock (GIL), CPython still coercively preempts long-running threads at
        arbitrary execution points. Ergo, multithreading concerns are *not*
        safely ignorable -- even under CPython.
    _object_ids_acquired : dict
        Dict mapping from **arbitrary keys** (i.e, hashable objects) to a
        boolean indicating whether the object is currently acquired.
        For efficiency and simplicity, this dictionary is defined as a 
        :class: `defaultdict` implicitly initializing missing keys on initial
        access to True.
    '''

    # ..................{ CLASS VARIABLES                   }..................
    # Slot *ALL* instance variables defined on this object to minimize space
    # and time complexity across frequently called @beartype decorations.
    __slots__ = ('_key_to_pool', '_pool_item_maker', '_thread_lock',
            '_object_ids_acquired')

    # ..................{ INITIALIZER                       }..................
    def __init__(self, item_maker: 'CallableTypes') -> None:
        '''
        Initialize this key pool with the passed factory callable.

        Parameters
        ----------
        item_maker : CallableTypes
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
               def item_maker(key: HashableType) -> object: ...
        '''
        assert callable(item_maker), (
            '{!r} not callable.'.format(item_maker))

        # Classify these parameters as instance variables.
        self._pool_item_maker = item_maker

        # Initialize all remaining instance variables.
        #
        # Note that "defaultdict" instances *MUST* be initialized with
        # positional rather than keyword parameters. For unknown reasons,
        # initializing such an instance with a keyword parameter causes that
        # instance to silently behave like a standard dictionary instead: e.g.,
        #
        #     >>> dd = defaultdict(default_factory=list)
        #     >>> dd['ee']
        #     KeyError: 'ee'
        self._key_to_pool = defaultdict(list)
        self._thread_lock = Lock()
        self._object_ids_acquired = defaultdict(bool)

    # ..................{ METHODS                           }..................
    def acquire(self, key: 'HashableType' = None) -> object:
        '''
        Acquire an arbitrary object associated with the passed **arbitrary
        key** (i.e., hashable object).

        Specifically, this method tests whether there exists a non-empty list
        previously associated with this key. If so, this method pops the last
        item from that list and returns that item; else (i.e., if there either
        exists no such list or such a list exists but is empty), this method
        effectively (in order):

        #. If no such list exists, create a new empty list associated with
           this key.
        #. Create a new object to be returned by calling the user-defined
           :meth:`_pool_item_maker` factory callable.
        #. Append this object to this list.
        #. Add/Update acquisition state of the object to True
        #. Returns this object.

        Parameters
        ----------
        key : Optional[HashableType]
            Hashable object associated with the pool item to be acquired.
            Defaults to ``None``.

        Returns
        ----------
        object
            Pool item associated with this hashable object.

        Raises
        ----------
        TypeError
            If this key is unhashable and thus *not* a key.
        '''

        # In a thread-safe manner...
        with self._thread_lock:
            # List associated with this key.
            #
            # If this is the first access of this key, this "defaultdict"
            # implicitly creates a new list and associates this key with that
            # list; else, this is the list previously associated with this key.
            #
            # Note that this statement implicitly raises a "TypeError"
            # exception if this key is unhashable, which is certainly more
            # efficient than our explicitly validating this constraint.
            pool = self._key_to_pool[key]

            # Arbitrary object associated with this key, defined as either...
            pool_item = (
                # A new object associated with this key...
                self._pool_item_maker(key)
                # If the list associated with this key is empty (i.e., this
                # method has been called more frequently than the corresponding
                # release() method for this key)...
                if not pool
                # Else, the list associated with this key is non-empty (i.e.,
                # this method has been called less frequently than the
                # corresponding release() method for this key). In this case,
                # pop (i.e., remove) and return the last item from this list.
                else pool.pop()
            )

            self._object_ids_acquired[id(pool_item)] = True

            return pool_item

    def release(self, item: object, key: 'HashableType' = None) -> None:
        '''
        Release the passed object acquired by a prior call to the
        :meth:`acquire` method passed the same passed **arbitrary key** (i.e.,
        hashable object).

        Specifically, this method tests whether there exists a list
        previously associated with this key. If not, this method creates a new
        empty list associated with this key. In either case, this method then
        appends this object to this list.

        Parameters
        ----------
        item : object
            Arbitrary object previously associated with this key.
        key : Optional[HashableType]
            Hashable object previously associated with this pool item. Defaults
            to ``None``.

        Raises
        ----------
        TypeError
            Occurs if the key is unhashable (i.e. *not* a key).
        _BeartypeUtilKeyPoolException
            Occurs if the object is not acquired and thus ineligible for release
        '''

        if not self._object_ids_acquired.get(id(item)):
            raise _BeartypeUtilKeyPoolException(
                    f"Attempted release of an unacquired object")
        
        # In a thread-safe manner...
        #
        # The best things in life are free or two-liners. This is the latter.
        with self._thread_lock:
            # Append this object to the list associated with this key.
            self._key_to_pool[key].append(item)
        
        self._object_ids_acquired[id(item)] = False
