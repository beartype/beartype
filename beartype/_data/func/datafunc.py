#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable globals** (i.e., global constants describing various
well-known functions and methods).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ FROZENSETS                         }....................
OBJECT_SLOT_WRAPPERS = frozenset(
    # This slow wrapper.
    object_attr_value
    # For the name of each attribute defined by the root "object" superclass...
    for object_attr_name, object_attr_value in object.__dict__.items()
    # If the value of this attribute is callable and thus a low-level C-based
    # slot wrapper whose default implementation is mostly useless.
    if callable(object_attr_value)
)
'''
Frozen set of all **object slot wrappers** (i.e., low-level C-based callables
bound to the root :class:`object` superclass providing mostly useless default
implementations of popular dunder methods).

The default implementations of object slot wrappers have no intrinsic value in
any meaningful context and only serve to obfuscate actually intrinsically
valuable methods declared by concrete subclasses. Detecting and ignoring object
slot wrappers is thus a common desire.
'''
