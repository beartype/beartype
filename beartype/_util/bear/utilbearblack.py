#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
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
from beartype._data.conf.dataconfblack import (
    BLACKLIST_MODULE_NAME_TO_TYPE_NAMES,
    BLACKLIST_PACKAGE_NAMES,
)

# ....................{ TESTERS ~ object                   }....................
def is_object_blacklisted(obj: object) -> bool:
    '''
    :data:`True` only if the passed object (e.g., callable, class) is
    **beartype-blacklisted** (i.e., resides in a third-party package or modules
    well-known to be hostile to runtime type-checking and thus :mod:`beartype`).

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

    # Avoid circular import dependencies.
    from beartype._util.module.utilmodget import get_object_module_name_or_none

    # Type of this object.
    obj_type = obj.__class__

    # Fully-qualified name of the package or module defining this object's type
    # if any *OR* "None" otherwise (e.g., if this type is defined in-memory).
    obj_type_module_name = get_object_module_name_or_none(obj_type)

    # If this type fails to provide this name, silently reduce to a noop.
    if not obj_type_module_name:
        # print(f'Ignoring unmoduled object {repr(obj)}!')
        return False
    # Else, this type provides this name.

    #FIXME: [SPEED] Globalize the dict.get() bound method called here. *shrug*
    # Frozen set of the unqualified basenames of all beartype-blacklisted types
    # defined by that package or module if any *OR* "None" otherwise (if that
    # package or module defines *NO* beartype-blacklisted types).
    blacklist_obj_type_names = BLACKLIST_MODULE_NAME_TO_TYPE_NAMES.get(
        obj_type_module_name)
    # print(f'obj: {obj}')
    # print(f'obj_type_module_name: {obj_type_module_name}')
    # print(f'blacklist_obj_type_names: {blacklist_obj_type_names}')
    # raise ValueError('ugh')

    # If...
    #
    # Note that this test is faster than subsequent tests and thus intentionally
    # performed first.
    if (
        # That package or module defines beartype-blacklisted types *AND*...
        blacklist_obj_type_names and
        # The unqualified basename of this object's type is blacklisted...
        obj_type.__name__ in blacklist_obj_type_names
    ):
        # Then immediately return true.
        return True
    # Else, this object's type is *NOT* beartype-blacklisted. However, this
    # object could still be beartype-blacklisted in some way. Continue testing!

    # Fully-qualified name of the package or module defining this object if any
    # *OR* "None" otherwise (e.g., if this object is defined in-memory).
    obj_module_name = get_object_module_name_or_none(obj)

    # If this object fails to provide this name, silently reduce to a noop.
    if not obj_module_name:
        # print(f'Ignoring unmoduled object {repr(obj)}!')
        return False
    # Else, this object provides this name and is thus *PROBABLY* either a
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

    # Return false as a feeble fallback.
    return False
