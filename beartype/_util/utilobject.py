#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **object** utilities.

This private submodule implements supplementary object-handling utility
functions required by various :mod:`beartype` facilities, including callables
generated by the :func:`beartype.beartype` decorator.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from contextlib import AbstractContextManager
from typing import Any

# ....................{ CLASSES                           }....................
class Iota(object):
    '''
    **Iota** (i.e., object minimizing space consumption by guaranteeably
    containing *no* attributes).
    '''

    __slots__ = ()

# ....................{ CONSTANTS                         }....................
SENTINEL = Iota()
'''
Sentinel object of arbitrary value.

This object is internally leveraged by various utility functions to identify
erroneous and edge-case input (e.g., iterables of insufficient length).
'''

# ....................{ TESTERS                           }....................
def is_object_context_manager(obj: object) -> bool:
    '''
    ``True`` only if the passed object is a **context manager** (i.e., object
    defining both the ``__exit__`` and ``__enter__`` dunder methods required to
    satisfy the context manager protocol)..

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a context manager.
    '''

    # One-liners for frivolous inanity.
    return isinstance(obj, AbstractContextManager)


# Note that this tester function *CANNOT* be memoized by the @callable_cached
# decorator, which requires all passed parameters to already be hashable.
def is_object_hashable(obj: object) -> bool:
    '''
    ``True`` only if the passed object is **hashable** (i.e., passable to the
    builtin :func:`hash` function *without* raising an exception and thus
    usable in hash-based containers like dictionaries and sets).

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is hashable.
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
    except:
        return False

    # Else, this object is hashable. Return true.
    return True


def is_object_subclass(obj: object, cls: type) -> bool:
    '''
    ``True`` only if the passed object is a subclass of the passed class.

    Caveats
    ----------
    **This higher-level tester should always be called in lieu of the
    lower-level** :func:`issubclass` **builtin,** which raises an exception
    when the first passed parameter is *not* a class. This tester suffers no
    such deficits, instead safely returning ``False`` when the first passed
    parameter is *not* a class.

    Parameters
    ----------
    obj : object
        Object to be inspected.
    cls : type
        Class to test whether this object is a subclass of.

    Returns
    ----------
    bool
        ``True`` only if this object is a subclass of this class.
    '''
    assert isinstance(cls, type), f'{repr(cls)} not class.'

    # One-liners for tremendous bravery.
    return isinstance(obj, type) and issubclass(obj, cls)

# ....................{ GETTERS ~ name                    }....................
#FIXME: Unit test us up, please.
def get_object_name(obj: Any) -> str:
    '''
    **Fully-qualified name** (i.e., ``.``-delimited string unambiguously
    identifying) the passed object if this object defines either the
    ``__qualname__`` or ``__name__`` dunder attributes *or* raise an exception
    otherwise (i.e., if this object defines *no* such attributes).

    Specifically, this name comprises (in order):

    #. If this object is transitively declared by a module, the absolute name
       of that module.
    #. If this object is transitively declared by another object (e.g., class,
       callable) and thus nested in that object, the unqualified basenames of
       all parent objects transitively declaring this object in that module.
    *. Unqualified basename of this object.

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    str
        Fully-qualified name of this object.

    Raises
    ----------
    AttributeError
        If this object defines neither ``__qualname__`` *nor* ``__name__``
        dunder attributes.
    '''

    # Avoid circular import dependencies.
    from beartype._cave._cavefast import CallableTypes
    from beartype._util.py.utilpymodule import (
        get_object_module_name_or_none,
        get_object_type_module_name_or_none,
    )

    # Fully-qualified name of the module declaring this object if this object
    # is declared by a module *OR* "None" otherwise, constructed as follows:
    # * If this object is callable
    object_module_name = (
        get_object_module_name_or_none(obj)
        if isinstance(object, CallableTypes) else
        get_object_type_module_name_or_none(obj)
    )

    # Lexically scoped name of this object excluding this module name.
    object_scopes_name = get_object_scopes_name(obj)

    # Return either...
    return (
        # If this module name exists, "."-delimited concatenation of this
        # module and object name;
        f'{object_module_name}.{object_scopes_name}'
        if object_module_name is not None else
        # Else, this object name as is.
        object_scopes_name
    )


#FIXME: Unit test us up, please.
def get_object_scopes_name(obj: Any) -> str:
    '''
    **Lexically scoped name** (i.e., ``.``-delimited string unambiguously
    identifying all lexical scopes encapsulating) the passed object if this
    object defines either the ``__qualname__`` or ``__name__`` dunder
    attributes *or* raise an exception otherwise (i.e., if this object defines
    *no* such attributes).

    Specifically, this name comprises (in order):

    #. If this object is transitively declared by another object (e.g., class,
       callable) and thus nested in that object, the unqualified basenames of
       all parent objects transitively declaring this object in that module.
    *. Unqualified basename of this object.

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    str
        Lexically scoped name of this object.

    Raises
    ----------
    AttributeError
        If this object defines neither ``__qualname__`` *nor* ``__name__``
        dunder attributes.
    '''

    # Return the fully-qualified name of this object excluding th name,
    # constructed as follows:
    # * If this object defines the "__qualname__" dunder attribute whose value
    #   is the "."-delimited concatenation of the unqualified basenames of all
    #   parent objects transitively declaring this object, that value with all
    #   meaningless "<locals>" placeholder substrings removed. If this object
    #   is a nested non-method callable (i.e., pure-Python function nested in
    #   one or more parent pure-Python callables), that value contains one such
    #   placeholder for each parent callable containing this callable. Since
    #   placeholders convey no meaningful semantics, placeholders are removed.
    # * Else if this object defines the "__name__" dunder attribute whose value
    #   is the unqualified basename of this ojbect, that value.
    # * Else, an "AttributeError" exception implicitly raised by the attempting
    #   to access a non-existent "__name__" dunder attribute.
    object_scoped_name = getattr(obj, '__qualname__', obj.__name__)

    # Remove all "<locals>" placeholder substrings as discussed above.
    return object_scoped_name.replace('<locals>.', '')

# ....................{ GETTERS ~ type                    }....................
def get_object_type_unless_type(obj: object) -> type:
    '''
    Either the passed object if this object is a class *or* the class of this
    object otherwise (i.e., if this object is *not* a class).

    Note that this function *never* raises exceptions on arbitrary objects,
    since the :func:`type` builtin wisely returns itself when passed itself:
    e.g.,

        >>> type(type(type)) is type
        True

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    type
        Type of this object.
    '''

    return obj if isinstance(obj, type) else type(obj)

# ....................{ GETTERS ~ type : name             }....................
def get_object_type_basename(obj: object) -> str:
    '''
    **Unqualified name** (i.e., non-``.``-delimited basename) of either passed
    object if this object is a class *or* the class of this object otherwise
    (i.e., if this object is *not* a class).

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    str
        Unqualified name of this class.
    '''

    # Elegant simplicity diminishes aggressive tendencies.
    return get_object_type_unless_type(obj).__name__


def get_object_type_name(obj: object) -> str:
    '''
    **Fully-qualified name** (i.e., ``.``-delimited name prefixed by the
    declaring module) of either passed object if this object is a class *or*
    the class of this object otherwise (i.e., if this object is *not* a class).

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    str
        Fully-qualified name of the type of this object.
    '''

    # Avoid circular import dependencies.
    from beartype._util.py.utilpymodule import (
        get_object_type_module_name_or_none)

    # Type of this object.
    cls = get_object_type_unless_type(obj)

    # Unqualified name of this type.
    cls_basename = get_object_type_basename(cls)

    # Fully-qualified name of the module defining this class if this class is
    # defined by a module *OR* "None" otherwise.
    cls_module_name = get_object_type_module_name_or_none(cls)

    # Return either...
    return (
        # The "."-delimited concatenation of this class basename and module
        # name if this module name exists.
        f'{cls_module_name}.{cls_basename}'
        if cls_module_name is not None else
        # This class basename as is otherwise.
        cls_basename
    )
