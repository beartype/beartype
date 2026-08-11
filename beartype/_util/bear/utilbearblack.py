#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **beartype blacklist utilities** (i.e., low-level callables
detecting whether passed objects are blacklisted and thus ignorable with respect
to :mod:`beartype`-specific type-checking, typically due to residing in
third-party packages or modules well-known to be hostile to runtime
type-checking and thus :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.shame.module.datashamemod import BLACKLIST_PACKAGE_NAMES
from beartype._data.shame.module.datashamemodtype import (
    BLACKLIST_MODULE_NAME_TO_TYPE_NAMES,
    BLACKLIST_TYPE_MRO_ROOT_MODULE_NAME_TO_TYPE_NAMES,
)
from threading import Lock
from weakref import WeakKeyDictionary

# ....................{ TESTERS                            }....................
def is_object_blacklisted(obj: object) -> bool:
    '''
    :data:`True` only if the passed arbitrary user-defined object (typically but
    *not* necessarily a callable or class) is **beartype-blacklisted** (i.e.,
    resides in a third-party package or modules well-known to be hostile to
    runtime type-checking and thus :mod:`beartype`).

    This tester is both thread-safe and memoized. Clearly, thread-safety is
    essential. Is memoization? It is. Although many user-defined objects passed
    to this callable are defined and decorated by the :func:`beartype.beartype`
    only once (and thus do *not* benefit from memoization), some user-defined
    objects are repeatedly passed to this callable across many decorations by
    the :func:`beartype.beartype` decorator (and thus *do* benefit from
    memoization). Which objects? Superclasses. They're reused across each of
    their user-defined subclasses, each of which is decorated by the
    :func:`beartype.beartype` decorator. See below for uglier details.

    Caveats
    -------
    This tester is internally memoized via a thread-safe global
    :class:`weakref.WeakKeyDictionary` instance for efficiency. Since the passed
    object is both arbitrary and user-defined, this memoization is careful to
    hold weak rather than strong references to that object. The usual
    :func:`beartype._util.cache.utilcachecall.callable_cached` decorator
    commonly employed throughout the :mod:`beartype` codebase to trivially
    memoize callables is thus wholly inappropriate here. Doing so would hold an
    unbounded number of strong references to arbitrary user-defined objects,
    resulting in a catastrophic explosion in space consumption under normal use
    cases. Interestingly, most objects do *not* accept weak references and thus
    *cannot* be memoized under this scheme. Thankfully, most objects passed to
    this tester (i.e., callables, classes) do. The sole exceptions are slotted
    classes, most of which do not. Python: "Why, bro? Why?"

    For example, consider closures automatically decorated under
    :mod:`beartype.claw` import hooks by the :func:`beartype.beartype`
    decorator; those closures are newly created on each call of their parent
    callable and would thus be held indefinitely as strong references by such an
    inappropriate memoization scheme. And... that's exactly what just happened,
    which is why this tester was completely refactored to avoid those horrors.

    Parameters
    ----------
    obj : object
        Arbitrary object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is beartype-blacklisted.

    See Also
    --------
    :data:`.BLACKLIST_PACKAGE_NAMES`
        Detailed discussion of beartype-blacklisting.
    '''

    # In a non-reentrant thread lock isolated to this tester...
    with _is_object_blacklisted_lock:
        # True only if this object is beartype-blacklisted, initialized to false
        # for safety.
        is_obj_blacklisted: bool | None = False

        # Attempt to...
        try:
            # Memoized boolean previously returned by the first prior call of
            # this tester passed this object if this tester has already been
            # passed this object and this object accepts weak references *OR*
            # either:
            # * If this tester has *NOT* already been passed this object,
            #   "None". Defaulting to "None" rather than false enables
            #   subsequent logic to reuse memoized false values.
            # * If this object refuses weak references, a "TypeError" exception.
            is_obj_blacklisted = _object_to_is_blacklisted.get(obj, None)

            # If this tester has *NOT* already been passed this object...
            if is_obj_blacklisted is None:
                # True only if this object is beartype-blacklisted.
                is_obj_blacklisted = _is_object_blacklisted(obj)

                # If this memoization dictionary contains more than this maximum
                # number of key-value pairs, efficiently clear this dictionary.
                # Doing so reverts this cache back to the empty dictionary by
                # removing all existing key-value pairs. This could be
                # considered a crude (albeit efficient) facsimile of a least
                # recently used (LRU) cache (albeit without that whole least
                # recently used part).
                if (
                    len(_object_to_is_blacklisted) >=
                    _OBJECT_TO_IS_BLACKLISTED_LEN_MAX
                ):
                    _object_to_is_blacklisted.clear()
                # Else, this memoization dictionary contains fewer than this
                # maximum number of key-value pairs. In this case, preserve the
                # existing contents of this dictionary.

                # Memoize this boolean for subsequent lookup by future calls.
                _object_to_is_blacklisted[obj] = is_obj_blacklisted
            # Else, this tester has already been passed this object. In this
            # case, trivially return the boolean memoized by the first prior
            # call of this tester passed this object.
        # If this object refuses weak references, the WeakKeyDictionary.get()
        # method called above raises a "TypeError" exception: e.g.,
        #     >>> from weakref import WeakKeyDictionary
        #     >>> weak_sauce = WeakKeyDictionary()
        #     >>> weak_sauce[['Lists', 'refuse']] = 'weak references, yo!'
        #     Traceback (most recent call last):
        #       File "<python-input-2>", line 1, in <module>
        #         weak_sauce[['Lists', 'refuse']] = 'weak references, yo!'
        #         ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
        #       File "../3.15.0/lib/python3.15/weakref.py", line 335, in __setitem__
        #         self.data[ref(key, self._remove)] = value
        #                   ~~~^^^^^^^^^^^^^^^^^^^
        #     TypeError: cannot create weak reference to 'list' object
        #
        # In this case, trivially assume this tester has yet to be passed this
        # object. Don't blame us. Blame Guido. Weak references are weak sauce.
        except TypeError:
            # True only if this object is beartype-blacklisted.
            is_obj_blacklisted = _is_object_blacklisted(obj)

    # Return true only if this object is beartype-blacklisted.
    return is_obj_blacklisted

# ....................{ PRIVATE ~ testers                  }....................
def _is_object_blacklisted(obj: object) -> bool:
    '''
    :data:`True` only if the passed arbitrary user-defined object (typically but
    *not* necessarily a callable or class) is **beartype-blacklisted** (i.e.,
    resides in a third-party package or modules well-known to be hostile to
    runtime type-checking and thus :mod:`beartype`).

    This tester is unmemoized and thus intended to be called directly *only* by
    the higher-level memoized :func:`.is_object_blacklisted` tester.

    Parameters
    ----------
    obj : object
        Arbitrary object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is beartype-blacklisted.
    '''

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype._util.module.utilmodget import get_object_module_name_or_none

    # ....................{ PHASES                         }....................
    # This tester is internally implemented as a series of sequential phases --
    # each increasingly more time- and/or space-complex than the last and thus
    # intentionally ordered from least to most complex.

    # ....................{ PHASE ~ type -> module         }....................
    # In this early phase, we efficiently test whether the combination of the
    # fully-qualified name of the module defining the type of the passed object
    # *AND* the unqualified basename of that type is known to be blacklisted.

    # Type of this object.
    obj_type = obj.__class__

    # Fully-qualified name of the package or module defining this object's type
    # if any *OR* "None" otherwise (e.g., if this type is defined in-memory).
    obj_type_module_name = get_object_module_name_or_none(obj_type)

    # If this type defines *NO* module name, this type is *NOT* blacklisted.
    # Why? Because the only types that @beartype blacklists are all defined in
    # modules that physically exist and thus have names. But this type has *NO*
    # module name! In this case, silently reduce to a noop.
    if not obj_type_module_name:
        # print(f'Ignoring unmoduled object {repr(obj)}!')
        return False
    # Else, this type defines this name.

    #FIXME: [SPEED] Globalize the dict.get() bound method called here. *shrug*
    # Frozen set of the unqualified basenames of all beartype-blacklisted types
    # defined by that package or module if any *OR* "None" otherwise (if that
    # package or module defines *NO* beartype-blacklisted types).
    blacklist_obj_type_names = BLACKLIST_MODULE_NAME_TO_TYPE_NAMES.get(
        obj_type_module_name)
    # print(f'obj: {obj}')
    # print(f'obj_type_module_name: {obj_type_module_name}')
    # print(f'blacklist_obj_type_names: {blacklist_obj_type_names}')

    # If...
    if (
        # That package or module defines beartype-blacklisted types *AND*...
        blacklist_obj_type_names and
        # The unqualified basename of this object's type is blacklisted...
        obj_type.__name__ in blacklist_obj_type_names
    ):
        # print(f'Object {obj} blacklisted via "type -> module" heuristic!')

        # Then immediately return true.
        return True
    # Else, this object's type is *NOT* beartype-blacklisted. However, this
    # object could still be beartype-blacklisted in some way. Continue testing!

    # ....................{ PHASE ~ type -> mro -> module  }....................
    # In this early phase, we efficiently test whether the combination of the
    # fully-qualified name of the module defining the type of the passed object
    # *AND* the unqualified basename of that type is known to be blacklisted
    # such that that type masquerades as the low-level user-defined callable it
    # wraps and is thus *ONLY* accessible as the root method-resolution order
    # (MRO) item (i.e., second-to-last item of the "__mro__" dunder dictionary
    # of this type, thus ignoring the ignorable "object" guaranteed to be the
    # last item of all such dictionaries).
    #
    # @beartype doesn't make the rules. It only complains about and breaks them.

    # MRO of this type.
    #
    # Note that all types are guaranteed to have a root MRO item *EXCEPT* the
    # "object" superclass, whose simplistic "(object,)" MRO lacks a root item.
    # While we could manually exclude this superclass, the existence of even a
    # single exception to this guarantee suggests that devious users could
    # circumvent this guarantee... somehow. Users are devious. Who can fathom
    # their ways? For safety, we assume this guarantee to *NOT* globally hold.
    obj_type_mro = obj_type.__mro__

    # If this MRO contains two or more items, this type is *NOT* the trivial
    # "object" superclass or something like that superclass. In this case...
    if len(obj_type_mro) >= 2:
        # Root MRO item of this type, ignoring the trivial "object" superclass.
        obj_type_mro_root = obj_type_mro[-2]

        # Fully-qualified name of the package or module defining this object's
        # root MRO type if any *OR* "None" otherwise (e.g., if this type is
        # defined in-memory).
        obj_type_mro_root_module_name = get_object_module_name_or_none(
            obj_type_mro_root)

        # If this type defines this name...
        if obj_type_mro_root_module_name:
            #FIXME: [SPEED] Globalize the dict.get() bound method called here.
            # Frozen set of the unqualified basenames of all
            # beartype-blacklisted types defined by that package or module if
            # any *OR* "None" otherwise (if that package or module defines *NO*
            # beartype-blacklisted types).
            blacklist_obj_type_mro_root_type_names = (
                BLACKLIST_TYPE_MRO_ROOT_MODULE_NAME_TO_TYPE_NAMES.get(
                    obj_type_mro_root_module_name))
            # print(f'obj: {obj}')
            # print(f'obj_type_mro_root_module_name: {obj_type_mro_root_module_name}')
            # print(f'blacklist_obj_type_mro_root_type_names: {blacklist_obj_type_mro_root_type_names}')

            # If...
            if (
                # That package or module defines beartype-blacklisted types
                # *AND*...
                blacklist_obj_type_mro_root_type_names and
                # The unqualified basename of this object's type is
                # blacklisted...
                obj_type_mro_root.__name__ in (
                    blacklist_obj_type_mro_root_type_names)
            ):
                # print(f'Object {obj} blacklisted via "type -> mro -> module" heuristic!')

                # Then immediately return true.
                return True
            # Else, this object's type is *NOT* beartype-blacklisted. However,
            # this object could still be beartype-blacklisted in some way.
            # Continue testing!
        # Else, this type defines *NO* module name. This object's type is *NOT*
        # beartype-blacklisted. However, this object could still be
        # beartype-blacklisted in some way. Continue testing!
    # Else, this type is the trivial "object" superclass or something like that
    # superclass.

    # ....................{ PHASE ~ package                }....................
    # In this late phase, we inefficiently test whether the combination of the
    # fully-qualified name of the top-level root package directly defining the
    # passed object is known to be blacklisted. This heuristic is less
    # efficient, as stripping this package name from this module name
    # constitutes a string-munging operation [read: *SLOW*].

    # Fully-qualified name of the package or module defining this object if any
    # *OR* "None" otherwise (e.g., if this object is defined in-memory).
    obj_module_name = get_object_module_name_or_none(obj)

    # If this object defines *NO* module name, silently reduce to a noop.
    if not obj_module_name:
        # print(f'Ignoring unmoduled object {repr(obj)}!')
        return False
    # Else, this object defines this name and is thus *PROBABLY* either a
    # pure-Python class or callable.

    # Fully-qualified name of the top-level root package or module transitively
    # containing that package or module (e.g., "some_package" when
    # "obj_module_name" is "some_package.some_module.some_submodule").
    #
    # Note this has been profiled to be the fastest one-liner for parsing the
    # first "."-suffixed substring from a "."-delimited string.
    obj_package_name = obj_module_name.partition('.')[0]
    # print(f'Testing package {repr(obj_package_name)} for blacklisting...')

    # If this package is globally beartype-blacklisted, immediately return true.
    if obj_package_name in BLACKLIST_PACKAGE_NAMES:
        return True
    # Else, this package is *NOT* globally beartype-blacklisted. However, this
    # object could still be specifically beartype-blacklisted. Continue testing!

    # ....................{ FALLBACK                       }....................
    # Return false as a feeble fallback.
    return False

# ....................{ PRIVATE ~ constants                }....................
_OBJECT_TO_IS_BLACKLISTED_LEN_MAX = 8192
'''
Maximum number of key-value pairs that the :func:`.is_object_blacklisted` tester
permits the :data:`._object_to_is_blacklisted` dictionary to contain.

That tester utilizes this magic number to effectively coerce that dictionary
into a crude (but efficient) facsimile of a least recently used (LRU) cache.
This number exhibits a tug-of-war between competing tradeoffs. Specifically, as
this number increases:

* The average-case efficiency of that tester increases (i.e., time decreases).
* The average-case consumption of that tester increases (i.e., space increases).
'''

# ....................{ PRIVATE ~ globals                  }....................
_is_object_blacklisted_lock = Lock()
'''
**Non-reentrant beartype blacklist thread lock** (i.e., low-level thread locking
mechanism implemented as a highly efficient C extension, defined as an global
for non-reentrant reuse elsewhere as a context manager).
'''


_object_to_is_blacklisted: WeakKeyDictionary[object, bool] = WeakKeyDictionary()
'''
Dictionary mapping from each weakly referenceable object passed to the private
:func:`._is_object_blacklisted` tester to the boolean returned by that tester,
effectively memoizing the higher-level :func:`.is_object_blacklisted` tester
internally calling that lower-level tester.
'''
