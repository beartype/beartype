#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Fixed list pool** (i.e., submodule whose thread-safe API caches previously
instantiated fixed lists of various lengths for space- and time-efficient reuse
by the :func:`beartype.beartype` decorator across decoration calls).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.cache.utilcachepool import KeyPool
from beartype._util.cache.list.utillistfixed import FixedList

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GLOBALS                           }....................
_fixed_list_pool = KeyPool(pool_item_maker=FixedList)
'''
Non-thread-safe **fixed list pool** (i.e., :class:`KeyPool` singleton caching
previously instantiated :class:`FixedList` instances of various lengths).
'''

# ....................{ FUNCTIONS                         }....................
def acquire_fixed_list(size: int) -> FixedList:
    '''
    Acquire an arbitrary **fixed list** (i.e., :class:`list` constrained to a
    fixed length defined at instantiation time) with the passed length.

    Caveats
    ----------
    **The contents of this list are arbitrary.** Callers should make *no*
    assumptions as to this list's initial items, but should instead
    reinitialize this list immediately after acquiring this list with standard
    list slice syntax: e.g.,

        >>> from beartype._util.cache.list.utillistfixedpool import acquire_fixed_list
        >>> fixed_list = acquire_fixed_list(size=5)
        >>> fixed_list[:] = ('Dirty', 'Deads', 'Done', 'Dirt', 'Cheap',)

    Parameters
    ----------
    size : int
        Length to constrain the fixed list to be acquired to.

    Returns
    ----------
    FixedList
        Arbitrary fixed list with this length.

    Raises
    ----------
    _BeartypeFixedListException
        If this length is either not an integer *or* is but is
        **non-positive** (i.e., is less than or equal to 0).
    '''

    # Acquire a fixed list of this length in a thread-safe manner.
    fixed_list = _fixed_list_pool.acquire(size)
    assert isinstance(fixed_list, FixedList), (
        '{!r} not a fixed list.'.format(fixed_list))

    # Return this list.
    return fixed_list


def release_fixed_list(fixed_list: FixedList) -> None:
    '''
    Release the passed fixed list acquired by a prior call to the
    :meth:`acquire` method.

    Caveats
    ----------
    **This list is not safely accessible after calling this function.** Callers
    should make *no* attempts to read, write, or otherwise access this list,
    but should instead nullify *all* variables referring to this list
    immediately after releasing this list (e.g., by setting these variables to
    the ``None`` singleton, by deleting these variables): e.g.,

        >>> from beartype._util.cache.list.utillistfixedpool import (
        ...     acquire_fixed_list, release_fixed_list)
        >>> fixed_list = acquire_fixed_list(size=7)
        >>> fixed_list[:] = ('If', 'You', 'Want', 'Blood', "You've", 'Got', 'It',)
        >>> release_fixed_list(fixed_list)
        # Either do this...
        >>> fixed_list = None
        # Or do this.
        >>> del fixed_list

    Parameters
    ----------
    fixed_lists : FixedList
        Fixed list to be released.
    '''
    assert isinstance(fixed_list, FixedList), (
        '{!r} not a fixed list.'.format(fixed_list))

    # Release this fixed list in a thread-safe manner.
    _fixed_list_pool.release(len(fixed_list), fixed_list)
