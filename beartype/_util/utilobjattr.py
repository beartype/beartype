#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **object attribute utilities** (i.e., low-level callables handling
arbitrary attributes of objects in a general-purpose manner).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
# from beartype._cave._cavefast import MethodBoundInstanceDunderCType
from beartype._cave._cavemap import NoneTypeOr
from beartype._data.func.datafunc import OBJECT_SLOT_WRAPPERS
from beartype._data.kind.datakindmap import FROZENDICT_EMPTY
from beartype._data.typing.datatyping import (
    DictStrToAny,
    FrozenSetStrs,
    ListStrs,
)
from collections.abc import Callable
from inspect import getattr_static
from typing import Optional

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please.
def is_object_attr_names_all(
    # Mandatory parameters.
    obj: object,
    attr_names_all: FrozenSetStrs,

    # Optional parameters.
    obj_dir: Optional[ListStrs] = None,
) -> bool:
    '''
    :data:`True` only if the passed arbitrary object defines *all* attributes
    whose names are in the passed frozen set.

    Equivalently, this tester returns :data:`True` only if the intersection of
    this passed set with a similar frozen set coerced from the passed
    ``obj_dir`` parameter is exactly this passed set.

    This tester is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator), as this tester efficiently reduces to a set
    intersection one-liner.

    Parameters
    ----------
    obj : object
        Object to be introspected.
    attr_names_all : FrozenSetStrs
        Maximal frozen set of the names of all **requisite attributes** (i.e.,
        maximum subset of attributes that *must* be bound to this object).
    obj_dir : Optional[list[str]], default: None
        List of the names of all relevant attributes bound to this object to be
        tested against *or* :data:`None`, in which case this list defaults to
        the names of *all* attributes bound to this object by calling the
        :func:`dir` builtin on this object. Defaults to :data:`None`. See also
        :func:`.get_object_attr_name_to_value` for further details.

    Returns
    -------
    bool
        :data:`True` only if this object defines *all* such attributes.
    '''
    assert isinstance(obj_dir, NoneTypeOr[list]), (
        f'{repr(obj_dir)} neither list of strings nor "None".')
    assert isinstance(attr_names_all, frozenset), (
        f'{repr(attr_names_all)} not frozen set.')

    # If the caller passed *NO* list of attribute names, default this to the
    # list of *ALL* attribute names bound to this object.
    if obj_dir is None:
        obj_dir = dir(obj)
    # Else, the caller passed a list of attribute names.

    # Return true only if the intersection of the passed set of the names of all
    # relevant attributes bound to this object with the set of the names of all
    # attributes bound to this object is the former set.
    return len(attr_names_all) == len(attr_names_all & frozenset(obj_dir))


#FIXME: Unit test us up, please.
def is_object_attr_names_any(
    # Mandatory parameters.
    obj: object,
    attr_names_any: FrozenSetStrs,

    # Optional parameters.
    obj_dir: Optional[ListStrs] = None,
) -> bool:
    '''
    :data:`True` only if the passed arbitrary object defines at least one
    attribute whose name is in the passed frozen set.

    Equivalently, this tester returns :data:`True` only if the intersection of
    this passed set with a similar frozen set coerced from the passed
    ``obj_dir`` parameter is non-empty.

    This tester is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator), as this tester efficiently reduces to a set
    intersection one-liner.

    Parameters
    ----------
    obj : object
        Object to be introspected.
    attr_names_any : FrozenSetStrs
        Minimal frozen set of the names of any **requisite attributes** (i.e.,
        minimum subset of attributes that *must* be bound to this object).
    obj_dir : Optional[list[str]], default: None
        List of the names of all relevant attributes bound to this object to be
        tested against *or* :data:`None`, in which case this list defaults to
        the names of *all* attributes bound to this object by calling the
        :func:`dir` builtin on this object. Defaults to :data:`None`. See also
        :func:`.get_object_attr_name_to_value` for further details.

    Returns
    -------
    bool
        :data:`True` only if this object defines *any* such attribute.
    '''
    assert isinstance(obj_dir, NoneTypeOr[list]), (
        f'{repr(obj_dir)} neither list of strings nor "None".')
    assert isinstance(attr_names_any, frozenset), (
        f'{repr(attr_names_any)} not frozen set.')

    # If the caller passed *NO* list of attribute names, default this to the
    # list of *ALL* attribute names bound to this object.
    if obj_dir is None:
        obj_dir = dir(obj)
    # Else, the caller passed a list of attribute names.

    # Return true only if the intersection of the passed set of the names of all
    # relevant attributes bound to this object with the set of the names of all
    # attributes bound to this object is non-empty.
    return bool(attr_names_any & frozenset(obj_dir))

# ....................{ GETTERS                            }....................
def get_object_attr_name_to_value(
    # Mandatory parameters.
    obj: object,

    # Optional parameters.
    obj_dir: Optional[ListStrs] = None,
    predicate: Optional[Callable[[str, object], bool]] = None,
    predicate_attr_names_all: Optional[FrozenSetStrs] = None,
    predicate_attr_names_any: Optional[FrozenSetStrs] = None,
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

    This getter is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator), as doing so would prohibit keyword
    parameters and thus render calls to this getter largely unreadable.
    Efficiency *is* important, but codebase maintainability even more so.

    Caveats
    -------
    **This getter exhibits linear time complexity** :math:`O(n)` for :math:`n`
    the number of attributes transitively defined by the passed object
    (including both the type of that object and all superclasses of that type).
    This getter should thus be called with some measure of caution and, ideally,
    only by memoized, cached, or otherwise efficient callers.

    Parameters
    ----------
    obj : object
        Object to be introspected.
    obj_dir : Optional[list[str]], default: None
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
          :func:`dir` builtin on this object. Note that :func:`dir`:

          * Only introspects attributes statically registered by the internal
            dictionary of this object (e.g., ``__dict__`` in unslotted objects,
            ``__slots__`` in slotted objects).
          * Thus silently ignores *all* attributes dynamically defined by the
            ``__getattr__()`` method or related runtime magic of this object.

        Defaults to :data:`None`.
    predicate: Optional[Callable[[str, object], bool]], default: None
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

        Callers passing this parameter may consider also passing a
        ``predicate_attr_names_*`` parameter as a useful optimization. Defaults
        to :data:`None`.
    predicate_attr_names_all : Optional[FrozenSetStrs], default: None
        Either:

        * Maximal frozen set of the names of all **requisite attributes** (i.e.,
          maximal superset of attributes that *must* be bound to this object).
          If the intersection of this set with a similar frozen set coerced from
          the passed ``obj_dir`` parameter is anything less than ``obj_dir``,
          this getter efficiently reduces to a noop by immediately returning the
          empty frozen dictionary. Note that this is merely an optimization
          against worst-case pathological behaviour -- albeit a useful one.
        * :data:`None`, in which this getter does *not* attempt to reduce to
          such a noop.

        Defaults to :data:`None`.
    predicate_attr_names_any : Optional[FrozenSetStrs], default: None
        Either:

        * Minimal frozen set of the names of any **requisite attributes** (i.e.,
          minimum subset of attributes that *must* be bound to this object). If
          the intersection of this set with a similar frozen set coerced from
          the passed ``obj_dir`` parameter is empty, this getter efficiently
          reduces to a noop by immediately returning the empty frozen
          dictionary. Note that this is merely an optimization against
          worst-case pathological behaviour -- albeit a useful one.
        * :data:`None`, in which this getter does *not* attempt to reduce to
          such a noop.

        Defaults to :data:`None`.

    Returns
    -------
    DictStrToAny
        Either:

        * If the caller passed a ``predicate_attr_names_*`` parameter whose
          intersection with a similar frozen set coerced from the passed
          ``obj_dir`` parameter is either empty *or* that ``obj_dir`` parameter
          (conditionally depending on which ``predicate_attr_names_*`` parameter
          was passed), the empty frozen dictionary singleton
          :data:`.FROZENDICT_EMPTY`.
        * Else, a mutable dictionary mapping from the name to explicit value of
          each attribute bound to the passed object whose name and/or value
          matches the passed predicate (in ascending lexicographic order of
          attribute name).
    '''
    assert isinstance(obj_dir, NoneTypeOr[list]), (
        f'{repr(obj_dir)} neither list of strings nor "None".')
    assert isinstance(predicate, NoneTypeOr[Callable]), (
        f'{repr(predicate)} neither callable nor "None".')
    assert isinstance(predicate_attr_names_all, NoneTypeOr[frozenset]), (
        f'{repr(predicate_attr_names_all)} neither frozen set nor "None".')
    assert isinstance(predicate_attr_names_any, NoneTypeOr[frozenset]), (
        f'{repr(predicate_attr_names_any)} neither frozen set nor "None".')

    # ....................{ PREAMBLE                       }....................
    # If the caller passed *NO* list of attribute names, default this to the
    # list of *ALL* attribute names bound to this object.
    if obj_dir is None:
        obj_dir = dir(obj)
    # Else, the caller passed a list of attribute names.

    # If either...
    if (
        (
            # The caller passed a maximal frozen set of the names of all
            # requisite attributes *AND*...
            predicate_attr_names_all is not None and
            # This object defines less than *ALL* of these attributes...
            not is_object_attr_names_all(
                obj=obj,
                obj_dir=obj_dir,
                attr_names_all=predicate_attr_names_all,
            )
        # *OR*...
        ) or (
            # The caller passed a minimal frozen set of the names of any
            # requisite attributes *AND*...
            predicate_attr_names_any is not None and
            # This object defines *NONE* of these attributes...
            not is_object_attr_names_any(
                obj=obj,
                obj_dir=obj_dir,
                attr_names_any=predicate_attr_names_any,
            )
        )
    ):
        # In either case, efficiently reduce to a noop by safely returning the
        # empty frozen dictionary singleton.
        return FROZENDICT_EMPTY
    # Else, the total number of attribute names in the intersection of the set
    # of of the names of all requisite attributes with the set of the names of
    # all attributes bound to this object is the number of requisite attribute
    # names. This implies this object defines *ALL* of the requisite attributes.
    #
    # Note that this does *NOT* necessarily imply these attributes all
    # satisfy the passed predicate (if any). Further disambiguation is required.

    # ....................{ LOCALS                         }....................
    # Dictionary mapping from the name of each attribute of the passed object
    # satisfying the passed predicate to the corresponding explicit value of
    # that attribute.
    attrs_name_to_value = None  # type: ignore[assignment]

    # ....................{ PREDICATE                      }....................
    # If the caller passed a predicate...
    if predicate:
        # Initialize this dictionary to the empty dictionary.
        attrs_name_to_value = {}

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
                attrs_name_to_value[attr_name] = attr_value
            # Else, this attribute fails to match this predicate. In this case,
            # silently ignore this attribute.
    # Else, the caller passed *NO* predicate. In this case...
    else:
        # Trivially define this dictionary via a dictionary comprehension.
        attrs_name_to_value = {
            attr_name: getattr_static(obj, attr_name)
            for attr_name in obj_dir
        }

    # ....................{ RETURN                         }....................
    # Return this dictionary.
    return attrs_name_to_value

# ....................{ GETTERS ~ explicit : methods       }....................
def get_object_method_name_to_value(obj: object, **kwargs) -> DictStrToAny:
    '''
    Dictionary mapping from the name to **explicit value** (i.e., value
    retrieved *without* implicitly calling the :func:`property`-decorated method
    implementing this attribute if this attribute is a property) of each method
    bound to the passed object.

    Parameters
    ----------
    obj : object
        Object to be introspected.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`.get_object_attr_name_to_value` getter underlying this getter.

    Caveats
    -------
    **This getter intentionally returns unbound pure-Python method functions
    rather than bound C-based method descriptors.** In theory, the latter
    approach would be marginally more useful. In practice, the standard
    :func:`.getattr_static` getter underlying this getter only supports the
    former approach. It is what it is.

    **This getter intentionally omits uncallable methods.** This includes most
    C-based method descriptors, most of which are uncallable depending on the
    version of the active Python interpreter. This *particularly* includes all
    C-based slot wrappers implicitly inherited by all classes from the root
    :class:`object` superclass (e.g., the :meth:`object.__str__` dunder method).
    The default implementations of slot wrappers have no intrinsic value in any
    meaningful context and only serve to obfuscate *actual* methods of
    general-purpose interest to most callers.

    Returns
    -------
    DictStrToAny
        Dictionary mapping from the name to explicit value of each method bound
        to the passed object.

    See Also
    --------
    :func:`.get_object_attr_name_to_value`
        Further details.
    '''

    # This is why we predicate, folks.
    return get_object_attr_name_to_value(
        obj=obj,
        predicate=_is_object_attr_callable_not_object_slot_wrapper,
        **kwargs
    )


#FIXME: Unit test us up, please. *sigh*
def get_object_nonmethod_name_to_value(obj: object, **kwargs) -> DictStrToAny:
    '''
    Dictionary mapping from the name to **explicit value** (i.e., value
    retrieved *without* implicitly calling the :func:`property`-decorated method
    implementing this attribute if this attribute is a property) of each
    non-method attribute bound to the passed object.

    Parameters
    ----------
    obj : object
        Object to be introspected.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`.get_object_attr_name_to_value` getter underlying this getter.

    Caveats
    -------
    **This getter intentionally includes uncallable methods.** This includes
    most C-based method descriptors, most of which are uncallable depending on
    the version of the active Python interpreter. Why? Because some of these
    method descriptors are actually C extension-specific unbound property method
    descriptors describing properties semantically equivalent to non-method
    attributes. Python. It do be like that.

    Returns
    -------
    DictStrToAny
        Dictionary mapping from the name to explicit value of each non-method
        bound to the passed object.

    See Also
    --------
    :func:`.get_object_attr_name_to_value`
        Further details.
    '''

    # Predicate and listen! @leycec back with a brand new QA mission! *barf*
    return get_object_attr_name_to_value(
        obj=obj, predicate=_is_object_attr_uncallable, **kwargs)

# ....................{ PRIVATE ~ testers                  }....................
def _is_object_attr_callable_not_object_slot_wrapper(
    attr_name: str, attr_value: object) -> bool:
    '''
    Predicate suitable for passing as the ``predicate`` parameter to the
    :func:`.get_object_attr_name_to_value` getter, returning
    :data:`True` only if the passed attribute value is both callable and *not*
    an **object slot wrapper** (i.e., low-level C-based callable bound to the
    root :class:`object` superclass, defining a trivial and thus mostly useless
    default implementation of a dunder method).
    '''
    # print(f'OBJECT_SLOT_WRAPPERS: {OBJECT_SLOT_WRAPPERS}')

    # If this attribute value is uncallable, return false immediately.
    if not callable(attr_value):
        return False
    # Else, this attribute value is callable.

    # Return true only if this callable is *NOT* an "object" slot wrapper.
    #
    # Note that:
    # * Although all standard callables are hashable, some user-defined
    #   callables are unhashable. Examples of unhashable callables include:
    #   * Unhashable pseudo-callables (i.e., unhashable objects whose classes
    #     define the __call__() dunder methods).
    # * The beartype._util.utilobject.is_object_hashable() tester is *NOT*
    #   necessarily safely importable here, due to chicken-and-egg issues. Ergo,
    #   we manually guard against unhashable callables.
    try:
        return attr_value not in OBJECT_SLOT_WRAPPERS
    # If doing so raises *ANY* exception, this callable is unhashable. However,
    # *ALL* "object" slot wrappers are hashable. It follows that this callable
    # is *NOT* an "object" slot wrapper. Despite being unhashable, this callable
    # *COULD* be of interest to the caller.
    except Exception:
        pass

    # Return true as a fallback.
    return True


def _is_object_attr_uncallable(attr_name: str, attr_value: object) -> bool:
    '''
    Predicate suitable for passing as the ``predicate`` parameter to the
    :func:`.get_object_attr_name_to_value` getter, returning
    :data:`True` only if the passed attribute value is uncallable.
    '''

    # Return true only if the passed attribute value is uncallable.
    return not callable(attr_value)
