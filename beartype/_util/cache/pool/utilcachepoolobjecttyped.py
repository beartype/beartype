#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Typed object pool** (i.e., submodule whose thread-safe API caches previously
instantiated objects of arbitrary types for space- and time-efficient reuse by
the :func:`beartype.beartype` decorator across decoration calls).

This private submodule is *not* intended for importation by downstream callers.

Caveats
----------
**This submodule only pools objects defining an** ``__init__()`` **method
accepting no parameters.** Why? Because this submodule unconditionally pools
all objects of the same types under those types. This submodule provides *no*
mechanism for pooling objects of the same types under different parameters
instantiated with those parameters and thus only implements a coarse- rather
than fine-grained object cache. If insufficient, consider defining a new
submodule implementing a fine-grained object cache unique to those objects. For
example:

* This submodule unconditionally pools all instances of the
  :class:`beartype._decor._data.BeartypeData` class under that type.
* The parallel :mod:`beartype._util.cache.pool.utilcachepoollistfixed`
  submodule conditionally pools every instance of the
  :class:`beartype._util.cache.pool.utilcachepoollistfixed.FixedList` class of
  the same length under that length.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.cache.pool.utilcachepool import KeyPool
from beartype.roar import _BeartypeUtilCachedObjectTypedException

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ SINGLETONS ~ private              }....................
_object_typed_pool = KeyPool(item_maker=lambda cls: cls())
'''
Thread-safe **typed object pool** (i.e., :class:`KeyPool` singleton caching
previously instantiated objects of the same types under those types).

Caveats
----------
**Avoid accessing this private singleton externally.** Instead, call the public
:func:`acquire_object_typed` and :func:`release_object_typed` functions, which
efficiently validate both input *and* output to conform to sane expectations.
'''

# ....................{ (ACQUIRERS|RELEASERS)             }....................
def acquire_object_typed(cls: type) -> object:
    '''
    Acquire an arbitrary object of the passed type.

    Caveats
    ----------
    **The contents of this object are arbitrary.** Callers should make *no*
    assumptions as to this object's state, but should instead reinitialize this
    object immediately after acquiring this object.

    Parameters
    ----------
    cls : type
        Type of the object to be acquired.

    Returns
    ----------
    object
        Arbitrary object of this type.

    Raises
    ----------
    _BeartypeUtilCachedObjectTypedException
        If this type is *not* actually a type.
    '''

    # If this type is *NOT* actually a type, raise an exception.
    if not isinstance(cls, type):
        raise _BeartypeUtilCachedObjectTypedException(
            '{!r} not a class.'.format(cls))

    # Thread-safely acquire an object of this type.
    object_typed = _object_typed_pool.acquire(cls)
    assert isinstance(object_typed, cls), (
        '{!r} not a {!r}.'.format(object_typed, cls))

    # Return this object.
    return object_typed


def release_object_typed(obj: object) -> None:
    '''
    Release the passed object acquired by a prior call to the
    :func:`acquire_object_typed` function.

    Caveats
    ----------
    **This object is not safely accessible after calling this function.**
    Callers should make *no* attempts to read, write, or otherwise access this
    object, but should instead nullify *all* variables referring to this object
    immediately after releasing this object (e.g., by setting these variables
    to the ``None`` singleton *or* by deleting these variables).

    Parameters
    ----------
    obj : object
        Previously acquired object to be released.
    '''

    # Thread-safely release this object.
    _object_typed_pool.release(key=obj.__class__, item=obj)
