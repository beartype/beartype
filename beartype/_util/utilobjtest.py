#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **object testers** (i.e., low-level callables detecting various
properties of arbitrary objects in a general-purpose manner).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.cls.datacls import TYPES_CONTEXTMANAGER_FAKE
from beartype._data.cls.pep.pep544.dataclspep544descriptor import (
    Pep544DescriptorData,
    Pep544DescriptorNondata,
)
from beartype._data.typing.datatypingport import TypeIs
from collections.abc import Hashable
from contextlib import AbstractContextManager

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please. *sigh*
def is_object_context_manager(obj: object) -> TypeIs[AbstractContextManager]:
    '''
    :data:`True` only if the passed object is a **context manager** (i.e.,
    object defining both the ``__exit__`` and ``__enter__`` dunder methods
    required to satisfy the context manager protocol).

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a context manager.
    '''

    # Return true only if...
    return (
        # This object satisfies the context manager protocol (i.e., defines both
        # the __enter__() and __exit__() dunder methods) *AND*...
        isinstance(obj, AbstractContextManager) and
        # This object is *NOT* a "fake" context manager (i.e., defines erroneous
        # __enter__() and __exit__() dunder methods trivially reducing to noops
        # and also emitting non-fatal deprecation warnings).
        not isinstance(obj, TYPES_CONTEXTMANAGER_FAKE)
    )


# Note that this tester function *CANNOT* be memoized by the @callable_cached
# decorator, which requires all passed parameters to already be hashable.
def is_object_hashable(obj: object) -> TypeIs[Hashable]:
    '''
    :data:`True` only if the passed object is **hashable** (i.e., passable to
    the builtin :func:`hash` function *without* raising an exception and thus
    usable in hash-based containers like dictionaries and sets).

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is hashable.
    '''

    # Attempt to hash this object. If doing so raises *any* exception
    # whatsoever, this object is by definition unhashable.
    #
    # Note that there also exists a "collections.abc.Hashable" superclass.
    # Sadly, this superclass is mostly useless for all practical purposes. Why?
    # Because user-defined classes are free to subclass that superclass
    # despite overriding the __hash__() dunder method implicitly called by the
    # builtin hash() function to raise exceptions: e.g.,
    #
    #     from collections.abc import Hashable
    #     class HashUmUp(Hashable):
    #         def __hash__(self):
    #             raise ValueError('uhoh')
    #
    # Note also that we catch all possible exceptions rather than merely the
    # standard "TypeError" exception raised by unhashable builtin types (e.g.,
    # dictionaries, lists, sets). Why? For the same exact reason as above.
    try:
        hash(obj)
    # If this object is unhashable, return false.
    except Exception:
        return False

    # Else, this object is hashable. Return true.
    return True

# ....................{ TESTERS ~ descriptor               }....................
def is_object_descriptor_data_instance(obj: object) -> bool:
    '''
    :data:`True` only if the passed object is a **data descriptor instance**
    (i.e., object whose type defines both the ``__get__`` and ``__set__`` dunder
    methods required to satisfy the data descriptor protocol).

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a data descriptor.

    See Also
    --------
    https://docs.python.org/3/howto/descriptor.html
        Python's official descriptor guide.
    '''

    # Return true only if this object satisfies the data descriptor protocol by
    # defining both the __get__() and __set__() dunder methods.
    return isinstance(obj, Pep544DescriptorData)  # type: ignore[misc]


def is_object_descriptor_nondata_instance(obj: object) -> bool:
    '''
    :data:`True` only if the passed object is a **non-data descriptor instance**
    (i.e., object whose type defines only the ``__get__`` but *not* ``__set__``
    dunder methods required to satisfy the non-data descriptor protocol).

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a non-data descriptor.

    See Also
    --------
    https://docs.python.org/3/howto/descriptor.html
        Python's official descriptor guide.
    '''

    # Return true only if...
    return (
        # This object satisfies the non-data descriptor protocol by defining at
        # least the __get__() dunder method *AND*...
        isinstance(obj, Pep544DescriptorNondata) and not  # type: ignore[misc]
        # This object violates the data descriptor protocol by failing to also
        # define the __set__() dunder method.
        isinstance(obj, Pep544DescriptorData)  # type: ignore[misc]
    )
