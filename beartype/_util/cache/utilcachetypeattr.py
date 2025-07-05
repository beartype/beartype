#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **class attribute caching utilities** (i.e., low-level callables
monkey-patching :mod:`beartype`-specific attributes describing user-defined
pure-Python classes into those classes).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Pretty sure we need to synchronize threaded access to this cache. Types
#and callables are all typically global objects and thus accessible across
#threads, implying caches defined on these objects are also accessible across
#threads, implying access to these caches *MUST* be properly synchronized.

# ....................{ IMPORTS                            }....................
from beartype._cave._cavefast import FunctionType
from beartype._data.kind.datakindiota import SENTINEL
from functools import wraps
from threading import Lock

# ....................{ GETTERS                            }....................
#FIXME: Unit test us up, please.
#FIXME: Refactor to account for "_TYPE_TO_ATTR_NAME_TO_VALUE_NAME", please.
def get_type_attr_cached_or_sentinel(cls: type, attr_name: str) -> object:
    '''
    **Memoized type attribute** (i.e., :mod:`beartype`-specific attribute
    memoizing the prior result of an expensive decision problem unique to the
    passed type) with the passed name previously monkey-patched into this type
    by a prior call to the :func:`.set_type_attr_cached` setter passed the same
    name if such a call occurred *or* the sentinel placeholder otherwise (e.g.,
    if no such call occurred).

    This getter is thread-safe with respect to the corresponding
    :func:`.set_type_attr_cached` setter.

    Caveats
    -------
    **Memoized type attributes are only accessible by calling this getter.**
    Memoized type attributes are *not* monkey-patched directly into types.
    Memoized type attributes are only monkey-patched indirectly into types.
    Specifically, the :func:`.set_type_attr_cached` setter monkey-patches
    memoized type attributes into pure-Python ``__sizeof__()`` dunder methods
    monkey-patched into types. Why? Safety. Monkey-patching attributes directly
    into types would conflict with user expectations, which expect class
    dictionaries to remain untrammelled by third-party decorators.

    Parameters
    ----------
    cls : type
        Type to be inspected.
    attr_name : str
        Unqualified basename of the memoized type attribute to be retrieved.

    Returns
    -------
    object
        Either:

        * If a prior call to the :func:`.set_type_attr_cached` setter passed the
          same name previously monkey-patched this memoized type attribute into
          this type, the value of this attribute.
        * Else, the **sentinel placeholder** (i.e., :data:`.SENTINEL`).
    '''
    assert isinstance(cls, type), f'{repr(cls)} not type.'
    assert isinstance(attr_name, str), f'{repr(attr_name)} not string.'
    assert attr_name.isidentifier(), f'{repr(attr_name)} not Python identifier.'

    # Thread-safely...
    with _TYPE_ATTR_CACHE_LOCK:
        # __sizeof__() dunder method currently declared by this class, which the
        # set_type_attr_cached() setter has possibly wrapped with a pure-Python
        # __sizeof__() dunder method. Why? Tangential reasons that are obscure,
        # profane, and have *NOTHING* to do with the __sizeof__() dunder method
        # itself. Succinctly, we need a reasonably safe place to persist
        # @beartype-specific attributes pertaining to this class.
        #
        # Clearly, the obvious place would be this class itself. However, doing
        # so would fundamentally modify this class and thus *ALL* instances of
        # this class in an unexpected and thus possibly unsafe manner. Consider
        # common use cases like slots, introspection, pickling, and sizing.
        # Clearly, monkey-patching attributes into class dictionaries without
        # the explicit consent of class designers (i.e., users) is an
        # ill-advised approach.
        #
        # A less obvious but safer place is required. A method of this class
        # would be the ideal candidate; whereas everybody cares about object
        # attributes and thus class dictionaries, nobody cares about method
        # attributes. This is why @beartype safely monkey-patches attributes
        # into @beartype-decorated methods. However, which method? Most methods
        # are *NOT* guaranteed to exist across all possible classes. Adding a
        # new method to this class would be no better than adding a new
        # attribute to this class; both modify class dictionaries. Fortunately,
        # Python currently guarantees *ALL* classes to define at least 24 dunder
        # methods as of Python 3.11. How? Via the root "object" superclass.
        # Unfortunately, *ALL* of these methods are C-based and thus do *NOT*
        # directly support monkey-patching: e.g.,
        #     >>> class AhMahGoddess(object): pass
        #     >>> AhMahGoddess.__init__.__beartyped_cls = AhMahGoddess
        #     AttributeError: 'wrapper_descriptor' object has no attribute
        #     '__beartyped_cls'
        #
        # Fortunately, *ALL* of these methods may be wrapped by pure-Python
        # equivalents whose implementations defer to their original C-based
        # methods. Unfortunately, doing so slightly reduces the efficiency of
        # calling these methods. Fortunately, a subset of these methods are
        # rarely called under production workloads; slightly reducing the
        # efficiency of calling these methods is irrelevant to almost all use
        # cases. Of these, the most obscure, largely useless, poorly documented,
        # and single-use is the __sizeof__() dunder method -- which is only ever
        # called by the sys.getsizeof() utility function, which itself is only
        # ever called manually in a REPL or by third-party object sizing
        # packages. In short, __sizeof__() is perfect.
        cls_sizeof = cls.__sizeof__

        # If this method is *NOT* pure-Python, this method is C-based and thus
        # *CANNOT* possibly have been monkey-patched by a prior call to the
        # set_type_attr_cached() setter, which would have necessarily wrapped
        # this non-monkey-patchable C-based method with a monkey-patchable
        # pure-Python equivalent. In this case, return the sentinel placeholder.
        if not isinstance(cls_sizeof, FunctionType):
            return SENTINEL
        # Else, this method is pure-Python and thus *COULD* possibly have been
        # monkey-patched by a prior call to the set_type_attr_cached() setter.

        # Memoized type attribute cache (i.e., dictionary mapping from each type
        # in a type hierarchy passed to this setter to a nested dictionary
        # mapping from the name to value of each memoized type attribute cached
        # by a call to this setter) if the set_type_attr_cached() setter has
        # already been passed this type at least once *OR* "None" (i.e., if that
        # setter has yet to be passed this type). See that setter for details.
        type_to_attr_name_to_value = getattr(
            cls_sizeof, _TYPE_ATTR_CACHE_NAME, None)

        # If this cache does *NOT* exist, the passed type attribute *CANNOT*
        # possibly have been cached by a prior call to that setter. In this
        # case, return the sentinel placeholder.
        if not type_to_attr_name_to_value:
            return SENTINEL
        # Else, this cache exists. This type attribute *COULD* possibly have
        # been cached by a prior call to that setter.

        # Nested dictionary mapping from the name to value of each memoized type
        # attribute cached for this type by a prior call to that setter if this
        # nested dictionary exists *OR* "None" otherwise.
        attr_name_to_value = type_to_attr_name_to_value.get(cls)

        # If this nested dictionary has yet to be created, the passed type
        # attribute *CANNOT* possibly have been cached by a prior call to that
        # setter. In this case, return the sentinel placeholder.
        if not attr_name_to_value:
            return SENTINEL
        # Else, this nested dictionary. This type attribute *COULD* possibly
        # have been cached by a prior call to that setter.

        # Value of this type attribute cached by a prior call to that setter if
        # any *OR* the sentinel placeholder otherwise.
        attr_value = attr_name_to_value.get(attr_name, SENTINEL)

        # Return this value.
        return attr_value

# ....................{ SETTERS                            }....................
#FIXME: Unit test us up, please.
def set_type_attr_cached(
    cls: type, attr_name: str, attr_value: object) -> None:
    '''
    Monkey-patch the **memoized type attribute** (i.e., :mod:`beartype`-specific
    attribute memoizing the prior result of an expensive decision problem unique
    to the passed type) with the passed name and value this type.

    This setter is thread-safe with respect to the corresponding
    :func:`.get_type_attr_cached_or_sentinel` getter.

    Caveats
    -------
    **Memoized type attributes are only mutatable by calling this setter.**
    Memoized type attributes are *not* monkey-patched directly into types.
    Memoized type attributes are only monkey-patched indirectly into types.
    Specifically, this setter monkey-patches memoized type attributes into
    pure-Python ``__sizeof__()`` dunder methods monkey-patched into types. Why?
    Safety. Monkey-patching attributes directly into types would conflict with
    user expectations, which expect class dictionaries to remain untrammelled by
    third-party decorators like :mod:`beartype`.

    Parameters
    ----------
    cls : type
        Type to be inspected.
    attr_name : str
        Unqualified basename of the memoized type attribute to be mutated.
    attr_value : object
        New value of this attribute.
    '''
    assert isinstance(cls, type), f'{repr(cls)} not type.'
    assert isinstance(attr_name, str), f'{repr(attr_name)} not string.'
    assert attr_name.isidentifier(), f'{repr(attr_name)} not Python identifier.'

    # Thread-safely...
    with _TYPE_ATTR_CACHE_LOCK:
        # __sizeof__() dunder method currently declared by this class. See the
        # get_type_attr_cached_or_sentinel() getter for details.
        cls_sizeof_old = cls.__sizeof__

        # If this method is already pure-Python, this method is already
        # monkey-patchable. In this case, monkey-patch this method directly.
        if isinstance(cls_sizeof_old, FunctionType):
            cls_sizeof = cls_sizeof_old  # pyright: ignore
        # Else, this method is *NOT* pure-Python, implying this method is
        # C-based and *NOT* monkey-patchable. In this case...
        else:
            # Avoid circular import dependencies.
            from beartype._util.cls.utilclsset import set_type_attr

            # New pure-Python __sizeof__() dunder method wrapping the original
            # C-based __sizeof__() dunder method declared by this class.
            @wraps(cls_sizeof_old)
            def cls_sizeof(self) -> int:
                return cls_sizeof_old(self)  # type: ignore[call-arg]

            # Replace the original C-based __sizeof__() dunder method with this
            # wrapper. For safety, we intentionally call our high-level
            # set_type_attr() setter rather than attempting to directly set this
            # attribute. The latter approach succeeds for standard pure-Python
            # mutable classes but catastrophically fails for non-standard
            # C-based immutable classes (e.g., "enum.Enum" subclasses).
            set_type_attr(cls, '__sizeof__', cls_sizeof)
        # Else, this method is already pure-Python.
        #
        # In any case, this method is now pure-Python and thus monkey-patchable.

        # Memoized type attribute cache (i.e., dictionary mapping from each type
        # in a type hierarchy passed to this setter to a nested dictionary
        # mapping from the name to value of each memoized type attribute cached
        # by a call to this setter) if this setter has already been passed this
        # type at least once *OR* "None" (i.e., if this setter has yet to be
        # passed this type).
        #
        # Ideally, this dictionary would *NOT* be required. Instead, this setter
        # would simply monkey-patch memoized type attributes directly into this
        # pure-Python __sizeof__() dunder method. Indeed, that overly simplistic
        # approach *DOES* work for a subset of cases: namely, if this type has
        # *NO* subclasses that are also passed to this setter. But if this type
        # his a subclass that is also passed to this setter, that approach would
        # cache the incorrect values. Why? Because subclasses of this type
        # inherit this pure-Python __sizeof__() dunder method and thus *ALL*
        # attributes monkey-patched by this setter into that method: e.g.,
        #     >>> class Superclass(): pass
        #     >>> def patch_sizeof(cls):
        #     ...     sizeof_old = cls.__sizeof__
        #     ...     def sizeof_new(self):
        #     ...         return sizeof_old(self)
        #     ...     cls.__sizeof__ = sizeof_new
        #     >>> Superclass.__sizeof__
        #     <method '__sizeof__' of 'object' objects>
        #     >>> patch_sizeof(Superclass)
        #     >>> Superclass.__sizeof__
        #     <function patch_sizeof.<locals>.sizeof_new at 0x7f1981393110>
        #
        #     >>> class Subclass(Superclass): pass
        #     >>> Subclass.__sizeof__
        #     <function patch_sizeof.<locals>.sizeof_new at 0x7f1981393110>
        #
        # Cache entries *MUST* thus be uniquified across type hierarchies.
        type_to_attr_name_to_value = getattr(
            cls_sizeof, _TYPE_ATTR_CACHE_NAME, None)

        # If *NO* memoized type attribute cache has been monkey-patched into
        # this pure-Python __sizeof__() dunder method yet, do so.
        if type_to_attr_name_to_value is None:
            type_to_attr_name_to_value = cls_sizeof._TYPE_ATTR_CACHE_NAME = {}  # type: ignore[attr-defined]
        # Else, a memoized type attribute cache has already been monkey-patched
        # into this pure-Python __sizeof__() dunder method.
        #
        # In either case, this cache now exists.

        # Nested dictionary mapping from the name to value of each memoized type
        # attribute cached for this type by a prior call to this setter if this
        # nested dictionary exists *OR* "None" otherwise.
        attr_name_to_value = type_to_attr_name_to_value.get(cls)

        # If this nested dictionary has yet to be created, do so.
        if attr_name_to_value is None:
            attr_name_to_value = type_to_attr_name_to_value[cls] = {}
        # Else, this nested dictionary has already been created.
        #
        # In either case, this nested dictionary now exists.

        # Cache this memoized type attribute into this nested dictionary. Phew!
        attr_name_to_value[attr_name] = attr_value  # type: ignore[index, assignment]

# ....................{ PRIVATE ~ globals                  }....................
_TYPE_ATTR_CACHE_LOCK = Lock()
'''
**Non-reentrant annotations dictionary thread lock** (i.e., low-level thread
locking mechanism implemented as a highly efficient C extension, defined as a
global for non-reentrant reuse elsewhere as a context manager).
'''


_TYPE_ATTR_CACHE_NAME = '__beartype_type_attr_cache'
'''
Arbitrary :mod:`beartype`-specific name of the **memoized type attribute cache**
(i.e., dictionary mapping from each type in a type hierarchy passed to the
:func:`set_type_attr_cached` setter to a nested dictionary mapping from the name
to value of each memoized type attribute cached by a prior call to that setter)
monkey-patched into types passed to that setter.
'''
