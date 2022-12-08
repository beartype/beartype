#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **weak reference** (i.e., references to objects explicitly
allowing those objects to be garbage-collected at *any* time) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
# from beartype.roar._roarexc import (
#     _BeartypeUtilPathException,
#     _BeartypeUtilPythonException,
# )
from beartype.typing import (
    Tuple,
)
# from beartype._util.cache.utilcachecall import callable_cached
# from platform import python_implementation
# from sys import executable as sys_executable
from weakref import ref as weakref_ref

# ....................{ GETTERS                            }....................
def make_obj_weakref_and_repr(obj: object) -> Tuple[object, str]:
    '''
    2-tuple ``(weakref, repr)`` weakly referring to the passed object.

    Parameters
    ----------
    obj : object
        Arbitrary object to be weakly referred to.

    Returns
    ----------
    Tuple[object, str]
        2-tuple ``(weakref, repr)`` weakly referring to this object such that:

        * ``weakref`` is either:

          * If this object supports weak references, a **weak reference** (i.e.,
            :class:`weakref.ref` instance) to this object.
          * If this object prohibits weak references (e.g., due to being a
            common C-based variable-sized container like a tuple or string),
            ``None``.

        * ``repr`` is the machine-readable representation of this object,
          truncated to ~10KB to minimize space consumption in the worst case of
          an obscenely large object.
    '''

    # Avoid circular import dependencies.
    from beartype._util.text.utiltextrepr import represent_object

    # Weak reference to this object if this object supports weak references *OR*
    # "None" otherwise (e.g., if this object is a variable-sized container).
    obj_weakref = None

    # Machine-readable representation of this object truncated to minimize space
    # consumption for the worst case of an obscenely large object.
    obj_repr = represent_object(
        obj=obj,
        # Store at most 1KB of the full representation, which should
        # certainly suffice for most use cases. Note that the
        # default of 96B is far too small to be useful here.
        max_len=1000,
    )

    # If this object is "None", substitute "None" for this non-"None"
    # placeholder. Since the "weakref.ref" class ambiguously returns "None" when
    # this object has already been garbage-collected, this placeholder enables
    # subsequent calls to the get_obj_weakref_or_repr() getter to disambiguate
    # between these two common edge cases.
    if obj is None:
        obj_weakref = _WEAKREF_NONE
    # Else, this object is *NOT* "None". In this case...
    else:
        # Attempt to classify a weak reference to this object for safety.
        try:
            obj_weakref = weakref_ref(obj)
        # If doing so raises a "TypeError", this object *CANNOT* be weakly
        # referred to. Sadly, builtin variable-sized C-based types (e.g.,
        # "dict", "int", "list", "tuple") *CANNOT* be weakly referred to. This
        # constraint is officially documented by the "weakref" module:
        #     Several built-in types such as list and dict do not directly
        #     support weak references but can add support through subclassing.
        #     CPython implementation detail: Other built-in types such as tuple
        #     and int do not support weak references even when subclassed.
        #
        # Since this edge case is common, permitting this exception to unwind
        # the call stack is unacceptable; likewise, even coercing this exception
        # into non-fatal warnings would generic excessive warning spam and is
        # thus also unacceptable. The only sane solution remaining is to
        # silently store the machine-readable representation of this object and
        # return that rather than this object from the "object" property.
        except TypeError:
            pass

    return obj_weakref, obj_repr



#FIXME: Unit test us up, please.
def get_weakref_obj_or_repr(obj_weakref: object, obj_repr: str) -> object:
    '''
    Object weakly referred to by the passed object if this object is indeed a
    weak reference to another existing object *or* the passed machine-readable
    representation otherwise (i.e., if this object is either ``None`` *or* is a
    weak reference to a dead garbage-collected object).

    This function is typically passed the pair of objects returned by a prior
    call to the companion :func:`make_obj_weakref_and_repr` function.

    Parameters
    ----------
    obj_weakref : object
        Either:

        * If the **referent** (i.e., target object being weakly referred to) is
          the ``None`` singleton, the :data:`_WEAKREF_NONE` placeholder.
        * Else if the referent supports weak references, a weak reference to
          that object.
        * Else, ``None``.
    obj_repr : str
        Machine-readable representation of that object, typically truncated to
        some number of characters to avoid worst-case space consumption.

    Returns
    ----------
    object
        Either:

        * If this weak reference is the :data:`_WEAKREF_NONE` placeholder, the
          ``None`` singleton.
        * Else if this referent support weak references, either:

          * If this referent is still alive (i.e., has yet to be
            garbage-collected), this referent.
          * Else, this referent is now dead (i.e., has already been
            garbage-collected). In this case, the passed representation.

        * Else, this referent does *not* support weak references (i.e., this
          weak reference is ``None``). In this case, the passed representation.
    '''
    assert isinstance(obj_repr, str), f'{repr(obj_repr)} not string.'

    # Object to be returned.
    obj = None

    # If this object is the singleton placeholder implying this object to
    # have been "None" when previously passed to the make_obj_weakref_and_repr()
    # factory, substitute this placeholder for "None". See that factory.
    #
    # Else, this object is *NOT* that placeholder. In this case...
    if obj_weakref is not _WEAKREF_NONE:
        #FIXME: Raise a proper private exception instead, please.
        assert isinstance(obj_weakref, weakref_ref), (
            f'{repr(obj_weakref)} neither weak reference nor "None".')

        # Culprit weakly referred to by this weak reference if this object
        # is still alive *OR* "None" otherwise (i.e., if this object has
        # already been garbage-collected).
        obj = obj_weakref()

        # If this object has already been garbage-collected, fallback to the
        # machine-readable representation of this object instead.
        if obj is None:
            obj = obj_repr
        # Else, this object is still alive.

    # Return this object.
    return obj

# ....................{ PROPERTIES ~ constants             }....................
_WEAKREF_NONE = object()
'''
Singleton substitute for the ``None`` singleton, enabling
:class:`BeartypeCallHintViolation` exceptions to differentiate between weak
references to ``None`` and weak references whose referents are already dead
(i.e., have already been garbage-collected).
'''
