#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **object utilities** (i.e., low-level callables handling arbitrary
objects in a general-purpose manner).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilObjectNameException
from beartype.typing import (
    Any,
    Callable,
    List,
    Optional,
)
from beartype._data.cls.datacls import TYPES_CONTEXTMANAGER_FAKE
from beartype._data.hint.datahinttyping import DictStrToAny
from contextlib import AbstractContextManager
from inspect import getattr_static

# ....................{ CLASSES                            }....................
class Iota(object):
    '''
    **Iota** (i.e., object minimizing space consumption by guaranteeably
    containing *no* attributes).
    '''

    __slots__ = ()

# ....................{ CONSTANTS                          }....................
SENTINEL = Iota()
'''
Sentinel object of arbitrary value.

This object is internally leveraged by various utility functions to identify
erroneous and edge-case input (e.g., iterables of insufficient length).
'''

# ....................{ TESTERS                            }....................
def is_object_context_manager(obj: object) -> bool:
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
def is_object_hashable(obj: object) -> bool:
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
    except:
        return False

    # Else, this object is hashable. Return true.
    return True

# ....................{ GETTERS ~ attribute                }....................
def get_object_attrs_name_to_value_explicit(
    # Mandatory parameters.
    obj: object,

    # Optional parameters.
    obj_dir: Optional[List[str]] = None,
    predicate: Optional[Callable[[str, object], bool]] = None
) -> DictStrToAny:
    '''
    Dictionary mapping from the name to **explicit value** (i.e., value
    retrieved *without* implicitly calling the :func:`property`-decorated method
    implementing this attribute if this attribute is a property) of each
    attribute bound to the passed object whose name and/or value matches the
    passed predicate (in ascending lexicographic order of attribute name).

    This getter thus returns a dictionary such that each value is:

    * If the corresponding attribute is a **property** (i.e., method decorated
      by the standard :func:`property` decorator), the low-level data descriptor
      underlying this property rather than the high-level value returned by
      implicitly querying that data descriptor. Doing so avoids unexpected
      exceptions and is thus *significantly* safer.
    * Else, the value of this attribute as is.

    This getter is substantially safer than all known alternatives (e.g., the
    standard :func:`inspect.getmembers` getter), all of which implicitly call
    the low-level method implementing each high-level property of the passed
    object and hence raise exceptions when any such method raises exceptions. By
    compare, this getter *never* raises unexpected exceptions. Unless properties
    are of interest, callers are strongly encouraged to call this getter rather
    than unsafe alternatives.

    Caveats
    -------
    **This getter exhibits linear time complexity** :math:`O(n)` for :math:`n`
    the number of attributes transitively defined by the passed object
    (including both the type of that object and all superclasses of that type).
    This getter should thus be called with some measure of caution.

    **This getter only introspects attributes statically registered by the
    internal dictionary of this object** (e.g., ``__dict__`` in unslotted
    objects, ``__slots__`` in slotted objects). This getter thus silently
    ignores *all* attributes dynamically defined by the ``__getattr__()`` method
    or related runtime magic of this object.

    Parameters
    ----------
    obj : object
        Object to be introspected.
    obj_dir : Optional[List[str]]
        Either:

        * List of the names of all relevant attributes bound to this object.
          Callers may explicitly pass this list to either:

          * Consider only the proper subset of object attributes satisfying some
            external predicate. Doing so avoids the need to pass a ``predicate``
            callback, which can be surprisingly expensive in time to repeatedly
            call for each attribute.
          * Optimize away repeated calls to the :func:`dir` builtin, which are
            surprisingly expensive in both time and space.

        * :data:`None`, in which case this getter defaults this list to the
          names of *all* attributes bound to this object by calling the
          :func:`dir` builtin on this object.

        Defaults to :data:`None`.
    predicate: Optional[Callable[[str, object], bool]]
        Either:

        * Callable iteratively passed both the name and explicit value of each
          attribute bound to this object, returning :data:True` only if that
          name and/or value matches this predicate. This getter calls this
          callable for each attribute bound to this object and, if this callable
          returns :data:`True`, adds this name and explicit value to the
          returned dictionary as a new key-value pair. This predicate is
          expected to have a signature resembling:

          .. code-block:: python

             def predicate(attr_name: str, attr_value: object) -> bool: ...

        * :data:`None`, in which case this getter unconditionally adds *all*
          attributes bound to this object to this dictionary.

        Defaults to :data:`None`.

    Returns
    -------
    DictStrToAny
        Dictionary mapping from the name to explicit value of each attribute
        bound to the passed object whose name and/or value matches the passed
        predicate (in ascending lexicographic order of attribute name).
    '''
    assert obj_dir is None or isinstance(obj_dir, list), (
        f'{repr(obj_dir)} neither list of strings nor "None".')
    assert predicate is None or callable(predicate), (
        f'{repr(predicate)} neither callable nor "None".')

    # Dictionary mapping from the name of each attribute of the passed object
    # satisfying the passed predicate to the corresponding explicit value of
    # that attribute.
    attrs_name_to_value_explicit = None  # type: ignore[assignment]

    # If the caller passed *NO* list of attribute names, default this to the
    # list of *ALL* attribute names bound to this object.
    if obj_dir is None:
        obj_dir = dir(obj)
    # Else, the caller passed a list of attribute names.

    # If the caller passed a predicate...
    if predicate:
        # Initialize this dictionary to the empty dictionary.
        attrs_name_to_value_explicit = {}

        # Ideally, this function would be reimplemented in terms of the
        # iter_attrs_implicit_matching() function calling the canonical
        # inspect.getmembers() function. Dynamic inspection is surprisingly
        # non-trivial in the general case, particularly when virtual base
        # classes rear their diamond-studded faces. Moreover, doing so would
        # support edge-case attributes when passed class objects, including:
        # * Metaclass attributes of the passed class.
        #
        # Sadly, inspect.getmembers() internally accesses attributes via the
        # dangerous getattr() builtin rather than the safe
        # inspect.getattr_static() function. This function explicitly requires
        # the latter and hence *MUST* reimplement rather than defer to
        # inspect.getmembers(). (Sadness reigns.)
        #
        # For the same reason, the unsafe vars() builtin cannot be called
        # either. Since that builtin fails for builtin containers (e.g., "dict",
        # "list"), this is not altogether a bad thing.
        for attr_name in obj_dir:
            # Value of this attribute guaranteed to be statically rather than
            # dynamically retrieved. The getattr() builtin performs the latter,
            # dynamically calling this attribute's getter if this attribute is
            # a property. Since that call could conceivably raise unwanted
            # exceptions *AND* since this function explicitly ignores
            # properties, static attribute retrievable is unavoidable.
            attr_value = getattr_static(obj, attr_name)

            # If this attribute matches this predicate...
            if predicate(attr_name, attr_value):
                # Add the name and explicit value of this attribute to this
                # dictionary as a new key-vaue pair. Note that, due to the above
                # assignment, this iteration *CANNOT* reasonably be optimized
                # into a dictionary comprehension.
                attrs_name_to_value_explicit[attr_name] = attr_value
            # Else, this attribute fails to match this predicate. In this case,
            # silently ignore this attribute.
    # Else, the caller passed *NO* predicate. In this case...
    else:
        # Trivially define this dictionary via a dictionary comprehension.
        attrs_name_to_value_explicit = {
            attr_name: getattr_static(obj, attr_name)
            for attr_name in obj_dir
        }

    # Return this dictionary.
    return attrs_name_to_value_explicit


def get_object_methods_name_to_value_explicit(
    # Mandatory parameters.
    obj: object,

    # Optional parameters.
    obj_dir: Optional[List[str]] = None,
) -> DictStrToAny:
    '''
    Dictionary mapping from the name to **explicit value** (i.e., value
    retrieved *without* implicitly calling the :func:`property`-decorated method
    implementing this attribute if this attribute is a property) of each method
    bound to the passed object.

    Parameters
    ----------
    obj : object
        Object to be introspected.
    obj_dir : Optional[List[str]]
        See also the :func:`.get_object_attrs_name_to_value_explicit` getter.

    Caveats
    -------
    **This getter intentionally returns unbound pure-Python method functions
    rather than bound C-based method descriptors.** In theory, the latter
    approach would be marginally more useful. In practice, the standard
    :func:`.getattr_static` getter underlying this getter only supports the
    former approach. It is what it is.

    Returns
    -------
    DictStrToAny
        Dictionary mapping from the name to explicit value of each methods bound
        to the passed object.

    Methods
    -------
    :func:`.get_object_attrs_name_to_value_explicit`
        Further details.
    '''

    # This is why we predicate, folks.
    return get_object_attrs_name_to_value_explicit(
        obj=obj,
        obj_dir=obj_dir,
        predicate=_is_object_attr_callable,
    )


def _is_object_attr_callable(attr_name: str, attr_value: object) -> bool:
    '''
    Predicate suitable for passing as the ``predicate`` parameter to the
    :func:`get_object_attrs_name_to_value_explicit` getter, returning
    :data:`True` only if the passed attribute value is callable.
    '''

    #Trivialize us up the predicate.
    return callable(attr_value)

# ....................{ GETTERS ~ name                     }....................
def get_object_name(obj: Any) -> str:
    '''
    **Fully-qualified name** (i.e., ``.``-delimited string unambiguously
    identifying) of the passed object if this object defines either the
    ``__qualname__`` or ``__name__`` dunder attributes *or* raise an exception
    otherwise (i.e., if this object defines *no* such attributes).

    Specifically, this name comprises (in order):

    #. If this object is transitively declared by a module, the absolute name
       of that module.
    #. If this object is transitively declared by another object (e.g., class,
       callable) and thus nested in that object, the unqualified basenames of
       all parent objects transitively declaring this object in that module.
    #. Unqualified basename of this object.

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    -------
    str
        Fully-qualified name of this object.

    Raises
    ------
    _BeartypeUtilObjectNameException
        If this object defines neither ``__qualname__`` *nor* ``__name__``
        dunder attributes.
    '''

    # Avoid circular import dependencies.
    from beartype._cave._cavefast import CallableOrClassTypes
    from beartype._util.module.utilmodget import (
        get_object_module_name_or_none,
        get_object_type_module_name_or_none,
    )

    # Lexically scoped name of this object excluding this module name if this
    # object is named *OR* raise an exception otherwise.
    object_scopes_name = get_object_basename_scoped(obj)

    # Fully-qualified name of the module declaring this object if this object
    # is declared by a module *OR* "None" otherwise, specifically defined as:
    # * If this object is either a callable or class, the fully-qualified name
    #   of the module declaring this object.
    # * Else, the fully-qualified name of the module declaring the class of
    #   this object.
    object_module_name = (
        get_object_module_name_or_none(obj)
        if isinstance(object, CallableOrClassTypes) else
        get_object_type_module_name_or_none(obj)
    )

    # Return either...
    return (
        # If this module name exists, "."-delimited concatenation of this
        # module and object name;
        f'{object_module_name}.{object_scopes_name}'
        if object_module_name is not None else
        # Else, this object name as is.
        object_scopes_name
    )

# ....................{ GETTERS ~ basename                 }....................
def get_object_basename_scoped(obj: Any) -> str:
    '''
    **Lexically scoped name** (i.e., ``.``-delimited string unambiguously
    identifying all lexical scopes encapsulating) the passed object if this
    object defines either the ``__qualname__`` or ``__name__`` dunder attributes
    *or* raise an exception otherwise (i.e., if this object defines *no* such
    attributes).

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    -------
    str
        Lexically scoped name of this object.

    Raises
    ------
    _BeartypeUtilObjectNameException
        If this object defines neither ``__qualname__`` *nor* ``__name__``
        dunder attributes.

    See Also
    --------
    :func:`.get_object_basename_scoped_or_none`
        Further details.
    '''

    # Fully-qualified name of this object excluding its module name.
    object_scoped_name = get_object_basename_scoped_or_none(obj)

    # If this object is unnamed, raise a human-readable exception. The default
    # "AttributeError" exception raised by attempting to directly access either
    # the "obj.__name__" or "obj.__qualname__" attributes is sufficiently
    # non-explanatory to warrant replacement by our explanatory exception.
    if object_scoped_name is None:
        raise _BeartypeUtilObjectNameException(
            f'{repr(obj)} unnamed '
            f'(i.e., declares neither "__name__" nor "__qualname__" '
            f'dunder attributes).'
        )
    # Else, this object is named.

    # Remove all "<locals>" placeholder substrings as discussed above.
    return object_scoped_name.replace('<locals>.', '')


#FIXME: Unit test us up, please.
def get_object_basename_scoped_or_none(obj: Any) -> Optional[str]:
    '''
    **Lexically scoped name** (i.e., ``.``-delimited string unambiguously
    identifying all lexical scopes encapsulating) the passed object if this
    object defines either the ``__qualname__`` or ``__name__`` dunder attributes
    *or* :data:`None` otherwise (i.e., if this object defines *no* such
    attributes).

    Specifically, this name comprises (in order):

    #. If this object is transitively declared by another object (e.g., class,
       callable) and thus nested in that object, the unqualified basenames of
       all parent objects transitively declaring this object in that module.
       For usability, these basenames intentionally omit the meaningless
       placeholder ``"<locals>"`` substrings artificially injected by Python
       itself into the original ``__qualname__`` instance variable underlying
       this getter: e.g.,

       .. code-block:: python

          >>> from beartype._util.utilobject import get_object_basename_scoped
          >>> def muh_func():
          ...     def muh_closure(): pass
          ...     return muh_closure()
          >>> muh_func().__qualname__
          'muh_func.<locals>.muh_closure'  # <-- bad Python
          >>> get_object_basename_scoped(muh_func)
          'muh_func.muh_closure'  # <-- good @beartype

    #. Unqualified basename of this object.

    Caveats
    -------
    **The higher-level** :func:`get_object_name` **getter should typically be
    called instead of this lower-level getter.** This getter unsafely:

    * Requires the passed object to declare dunder attributes *not* generally
      declared by arbitrary instances of user-defined classes.
    * Omits the fully-qualified name of the module transitively declaring this
      object and thus fails to return fully-qualified names.

    **This high-level getter should always be called in lieu of directly
    accessing the low-level** ``__qualname__`` **dunder attribute on objects.**
    That attribute contains one meaningless ``"<locals>"`` placeholder
    substring conveying *no* meaningful semantics for each parent callable
    lexically nesting this object.

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    -------
    Optional[str]
        Either:

        * If this object defines at least one of the ``__qualname__`` or
          ``__name__`` dunder attributes, the lexically scoped name of this
          object.
        * Else, :data:`None`.

    Raises
    ------
    _BeartypeUtilObjectNameException
        If this object defines neither ``__qualname__`` *nor* ``__name__``
        dunder attributes.
    '''

    # Fully-qualified name of this object excluding its module name as follows:
    # * If this object defines the "__qualname__" dunder attribute whose value
    #   is the "."-delimited concatenation of the unqualified basenames of all
    #   parent objects transitively declaring this object, that value with all
    #   meaningless "<locals>" placeholder substrings removed. If this object
    #   is a nested non-method callable (i.e., pure-Python function nested in
    #   one or more parent pure-Python callables), that value contains one such
    #   placeholder for each parent callable containing this callable. Since
    #   placeholders convey no meaningful semantics, placeholders are removed.
    # * Else if this object defines the "__name__" dunder attribute whose value
    #   is the unqualified basename of this object, that value.
    # * Else, "None".
    object_scoped_name = getattr(
        obj, '__qualname__', getattr(
            obj, '__name__', None))

    # Return either...
    return (
        # If this name exists, all "<locals>" placeholder substrings globally
        # removed from this name as discussed above;
        object_scoped_name.replace('<locals>.', '')
        if object_scoped_name else
        # Else, either "None" or the empty string.
        object_scoped_name
    )

# ....................{ GETTERS ~ filename                 }....................
def get_object_filename_or_none(obj: object) -> Optional[str]:
    '''
    Filename of the module or script physically declaring the passed object if
    this object is either a callable or class physically declared on-disk *or*
    :data:`None` otherwise (i.e., if this object is neither a callable nor
    class *or* is either a callable or class dynamically declared in-memory).

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    -------
    Optional[str]
        Either:

        * If this object is either a callable or class physically declared
          on-disk, the filename of the module or script physically declaring
          this object.
        * Else, :data:`None`.
    '''

    # Avoid circular import dependencies.
    from beartype._util.cls.utilclsget import get_type_filename_or_none
    from beartype._util.func.utilfuncfile import get_func_filename_or_none
    from beartype._util.func.utilfunctest import is_func_python

    # Return either...
    return (
        # If this object is a pure-Python class, the absolute filename of the
        # source module file defining that class if that class was defined
        # on-disk *OR* "None" otherwise (i.e., if that class was defined
        # in-memory);
        get_type_filename_or_none(obj)
        if isinstance(obj, type) else
        # If this object is a pure-Python callable, the absolute filename of the
        # absolute filename of the source module file defining that callable if
        # that callable was defined on-disk *OR* "None" otherwise (i.e., if that
        # callable was defined in-memory);
        get_func_filename_or_none(obj)
        if is_func_python(obj) else
        # Else, "None".
        None
    )

# ....................{ GETTERS ~ type                     }....................
def get_object_type_unless_type(obj: object) -> type:
    '''
    Either the passed object if this object is a class *or* the class of this
    object otherwise (i.e., if this object is *not* a class).

    Note that this function *never* raises exceptions on arbitrary objects, as
    the :obj:`type` builtin wisely returns itself when passed itself: e.g.,

    .. code-block:: python

        >>> type(type(type)) is type
        True

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    -------
    type
        Type of this object.
    '''

    return obj if isinstance(obj, type) else type(obj)

# ....................{ GETTERS ~ type : name              }....................
def get_object_type_basename(obj: object) -> str:
    '''
    **Unqualified name** (i.e., non-``.``-delimited basename) of either the
    passed object if this object is a class *or* the class of this object
    otherwise (i.e., if this object is *not* a class).

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    -------
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
    -------
    str
        Fully-qualified name of the type of this object.
    '''

    # Avoid circular import dependencies.
    from beartype._util.module.utilmodget import (
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
