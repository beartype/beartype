#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-compliant code wrapper scope utilities** (i.e.,
functions handling the possibly nested lexical scopes enclosing wrapper
functions generated by the :func:`beartype.beartype` decorator).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Hah-hah! Finally figured out how to do recursive type hints... mostly.
#It's a two-parter consisting of:
#* *PART I.* In the first part:
#  * Refactor our code generation algorithm to additionally maintain a stack of
#    all parent type hints of the currently visited type hint. Note that we need
#    to do this anyway to support the __beartype_hint__() protocol. See "FIXME:"
#    comments in the "beartype.plug._plughintable" submodule pertaining to that
#    protocol for further details on properly building out this stack.
#  * When that algorithm visits a forward reference:
#    * That algorithm calls the express_func_scope_type_ref() function
#      generating type-checking code for that reference. Refactor that call to
#      additionally pass that stack of parent hints to that function.
#    * Refactor the express_func_scope_type_ref() function to:
#      * If the passed forward reference is relative, additionally return that
#        stack in the returned 3-tuple
#        "(forwardref_expr, forwardrefs_class_basename, forwardref_parent_hints)",
#        where "forwardref_parent_hints" is that stack.
#* *PART II.* In the second part:
#  * Refactor the beartype._decor.wrap.wrapmain._unmemoize_func_wrapper_code()
#    function to additionally:
#    * If the passed forward reference is relative *AND* the unqualified
#      basename of an existing attribute in a local or global scope of the
#      currently decorated callable *AND* the value of that attribute is a
#      parent type hint on the stack of parent type hints returned by the
#      previously called express_func_scope_type_ref() function, then
#      *THIS REFERENCE INDICATES A RECURSIVE TYPE HINT.* In this case:
#      * Replace this forward reference with a new recursive type-checking
#        "beartype._check.forward.reference.fwdrefabc.BeartypeForwardRef_{forwardref}"
#        subclass whose is_instance() tester method recursively calls itself
#        indefinitely. If doing so generates a "RecursionError", @beartype
#        considers that the user's problem. *wink*
#
#Done and done. Phew!

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintNonpepException
from beartype.typing import (
    Dict,
    List,
    Optional,
    Tuple,
)
from beartype._cave._cavemap import NoneTypeOr
from beartype._check.forward.reference.fwdrefmake import (
    make_forwardref_indexable_subtype)
from beartype._check.forward.reference.fwdreftest import is_forwardref
from beartype._check.code.snip.codesnipstr import (
    CODE_HINT_REF_TYPE_BASENAME_PLACEHOLDER_PREFIX,
    CODE_HINT_REF_TYPE_BASENAME_PLACEHOLDER_SUFFIX,
)
from beartype._data.cls.datacls import TYPES_SET_OR_TUPLE
from beartype._data.hint.datahinttyping import (
    LexicalScope,
    Pep484585ForwardRef,
    SetOrTupleTypes,
    TypeOrTupleTypes,
    TupleTypes,
)
from beartype._util.cls.pep.utilpep3119 import (
    die_unless_type_isinstanceable,
    die_unless_object_isinstanceable,
)
from beartype._util.cls.utilclstest import is_type_builtin
from beartype._util.func.utilfuncscope import add_func_scope_attr
from beartype._util.hint.pep.proposal.pep484585.utilpep484585ref import (
    get_hint_pep484585_ref_names)
from beartype._util.utilobject import get_object_type_basename
from collections.abc import Set

# ....................{ ADDERS ~ type                      }....................
#FIXME: Unit test us up, please.
def add_func_scope_ref(
    # Mandatory parameters.
    func_scope: LexicalScope,
    ref_module_name: Optional[str],
    ref_name: str,

    # Optional parameters.
    exception_prefix: str = 'Globally or locally scoped forward reference ',
) -> str:
    '''
    Add a new **scoped forward reference proxy** (i.e., new key-value pair of
    the passed dictionary mapping from the name to value of each globally or
    locally scoped attribute externally accessed elsewhere, whose key is a
    machine-readable name internally generated by this function to uniquely
    refer to a new forward reference proxy proxying the class with the passed
    attribute name residing in the module with the passed module name) to the
    passed scope *and* return that name.

    Parameters
    ----------
    func_scope : LexicalScope
        Local or global scope to add this class or tuple of classes to.
    ref_module_name : Optional[str]
        Possibly undefined fully-qualified module name referred to by this
        forward reference.
    ref_name : str
        Possibly unqualified classname referred to by this forward reference.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to a sensible string.

    Returns
    -------
    str
        Name of this forward reference proxy in this scope generated by this
        function.

    Raises
    ------
    _BeartypeUtilCallableException
        If an attribute with the same name as that internally generated by this
        adder but having a different value already exists in this scope. This
        adder uniquifies names by object identifier and should thus *never*
        generate name collisions. This exception is thus intentionally raised
        as a private rather than public exception.
    '''

    # Forward reference proxy referring to this class.
    hint_ref = make_forwardref_indexable_subtype(ref_module_name, ref_name)

    # Return the name of a new parameter passing this forward reference proxy.
    return add_func_scope_attr(
        func_scope=func_scope, attr=hint_ref)


# ....................{ ADDERS ~ type                      }....................
#FIXME: Unit test us up, please.
def add_func_scope_type_or_types(
    # Mandatory parameters.
    func_scope: LexicalScope,
    type_or_types: TypeOrTupleTypes,

    # Optional parameters.
    exception_prefix: str = (
        'Globally or locally scoped class or tuple of classes '),
) -> str:
    '''
    Add a new **scoped class or tuple of classes** (i.e., new key-value pair of
    the passed dictionary mapping from the name to value of each globally or
    locally scoped attribute externally accessed elsewhere, whose key is a
    machine-readable name internally generated by this function to uniquely
    refer to the passed class or tuple of classes and whose value is that class
    or tuple) to the passed scope *and* return that name.

    This function additionally caches this tuple with the beartypistry
    singleton to reduce space consumption for tuples duplicated across the
    active Python interpreter.

    Parameters
    ----------
    func_scope : LexicalScope
        Local or global scope to add this class or tuple of classes to.
    type_or_types : TypeOrTupleTypes
        Arbitrary class or tuple of classes to be added to this scope.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to a sensible string.

    Returns
    -------
    str
        Name of this class or tuple in this scope generated by this function.

    Raises
    ------
    BeartypeDecorHintNonpepException
        If this hint is either:

        * Neither a class nor tuple.
        * A tuple that is empty.
    BeartypeDecorHintPep3119Exception
        If hint is:

        * A class that is *not* isinstanceable (i.e., passable as the second
          argument to the :func:`isinstance` builtin).
        * A tuple of one or more items that are *not* isinstanceable classes.
    _BeartypeUtilCallableException
        If an attribute with the same name as that internally generated by this
        adder but having a different value already exists in this scope. This
        adder uniquifies names by object identifier and should thus *never*
        generate name collisions. This exception is thus intentionally raised
        as a private rather than public exception.
    '''

    # Return either...
    return (
        # If this hint is a class, the name of a new parameter passing this
        # class;
        add_func_scope_type(
            func_scope=func_scope,
            cls=type_or_types,
            exception_prefix=exception_prefix,
        )
        if isinstance(type_or_types, type) else
        # Else, this hint is *NOT* a class. In this case:
        # * If this hint is a tuple of classes, the name of a new parameter
        #   passing this tuple.
        # * Else, raise an exception.
        add_func_scope_types(
            func_scope=func_scope,
            types=type_or_types,
            exception_prefix=exception_prefix,
        )
    )


def add_func_scope_type(
    # Mandatory parameters.
    func_scope: LexicalScope,
    cls: type,

    # Optional parameters.
    exception_prefix: str = 'Globally or locally scoped class ',
) -> str:
    '''
    Add a new **scoped class** (i.e., new key-value pair of the passed
    dictionary mapping from the name to value of each globally or locally scoped
    attribute externally accessed elsewhere, whose key is a machine-readable
    name internally generated by this function to uniquely refer to the passed
    class and whose value is that class) to the passed scope *and* return that
    name.

    Parameters
    ----------
    func_scope : LexicalScope
        Local or global scope to add this class to.
    cls : type
        Arbitrary class to be added to this scope.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to a sensible string.

    Returns
    -------
    str
        Name of this class in this scope generated by this function.

    Raises
    ------
    BeartypeDecorHintPep3119Exception
        If this class is *not* isinstanceable (i.e., passable as the second
        argument to the :func:`isinstance` builtin).
    _BeartypeUtilCallableException
        If an attribute with the same name as that internally generated by this
        adder but having a different value already exists in this scope. This
        adder uniquifies names by object identifier and should thus *never*
        generate name collisions. This exception is thus intentionally raised
        as a private rather than public exception.
    '''

    # If this object is *NOT* an isinstanceable class, raise an exception.
    die_unless_type_isinstanceable(cls=cls, exception_prefix=exception_prefix)
    # Else, this object is an isinstanceable class.

    # Return either...
    return (
        # If this type is a builtin (i.e., globally accessible C-based type
        # requiring *no* explicit importation), the unqualified basename of
        # this type as is, as this type requires no parametrization;
        get_object_type_basename(cls)
        if is_type_builtin(cls) else
        # Else, the name of a new parameter passing this class.
        add_func_scope_attr(
            func_scope=func_scope, attr=cls, exception_prefix=exception_prefix)
    )


def add_func_scope_types(
    # Mandatory parameters.
    func_scope: LexicalScope,
    types: SetOrTupleTypes,

    # Optional parameters.
    is_unique: Optional[bool] = None,
    exception_prefix: str = (
        'Globally or locally scoped set or tuple of classes '),
) -> str:
    '''
    Add a new **scoped tuple of classes** (i.e., new key-value pair of the
    passed dictionary mapping from the name to value of each globally or locally
    scoped attribute externally accessed elsewhere, whose key is a
    machine-readable name internally generated by this function to uniquely
    refer to the passed set or tuple of classes and whose value is that tuple)
    to the passed scope *and* return that machine-readable name.

    This function additionally caches this tuple with the
    :data:`._tuple_union_to_tuple_union` dictionary to reduce space consumption
    for tuples duplicated across the active Python interpreter.

    Parameters
    ----------
    func_scope : LexicalScope
        Local or global scope to add this object to.
    types : SetOrTupleOfTypes
        Set or tuple of arbitrary types to be added to this scope.
    is_unique : Optional[bool]
        Tri-state boolean governing whether this function attempts to
        deduplicate types in the ``types`` iterable. Specifically, either:

        * :data:`True`, in which case the caller guarantees ``types`` to contain
          *no* duplicate types.
        * :data:`False`, in which case this function assumes ``types`` to
          contain duplicate types by internally (in order):

          #. Coercing this tuple into a set, thus implicitly ignoring both
             duplicates and ordering of types in this tuple.
          #. Coercing that set back into another tuple.
          #. If these two tuples differ, the passed tuple contains one or more
             duplicates; in this case, the duplicate-free tuple is cached and
             passed.
          #. Else, the passed tuple contains no duplicates; in this case, the
             passed tuple is cached and passed.

        * :data:`None`, in which case this function reduces this parameter to
          either:

          * :data:`True` if ``types`` is a :class:`tuple`.
          * :data:`False` if ``types`` is a :class:`set`.

        This tri-state boolean does *not* simply enable an edge-case
        optimization, though it certainly does that; this boolean enables
        callers to guarantee that this function caches and passes the passed
        tuple rather than a new tuple internally created by this function.

        Defaults to :data:`None`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to a sensible string.

    Returns
    -------
    str
        Name of this tuple in this scope generated by this function.

    Raises
    ------
    BeartypeDecorHintNonpepException
        If this hint is either:

        * Neither a set nor tuple.
        * A set or tuple that is empty.
    BeartypeDecorHintPep3119Exception
        If one or more items of this hint are *not* isinstanceable classes
        (i.e., classes passable as the second argument to the
        :func:`isinstance` builtin).
    _BeartypeUtilCallableException
        If an attribute with the same name as that internally generated by this
        adder but having a different value already exists in this scope. This
        adder uniquifies names by object identifier and should thus *never*
        generate name collisions. This exception is thus intentionally raised
        as a private rather than public exception.
    '''
    assert isinstance(is_unique, NoneTypeOr[bool]), (
        f'{repr(is_unique)} neither bool nor "None".')

    # ....................{ VALIDATE                       }....................
    # If this container is neither a set nor tuple, raise an exception.
    if not isinstance(types, TYPES_SET_OR_TUPLE):
        msg = f'{exception_prefix}{repr(types)} neither set nor tuple.'
        raise BeartypeDecorHintNonpepException(
            msg)
    # Else, this container is either a set or tuple.
    #
    # If this container is empty, raise an exception.
    if not types:
        msg = f'{exception_prefix}empty.'
        raise BeartypeDecorHintNonpepException(msg)
    # Else, this container is non-empty.
    #
    # If this container only contains one type, register only this type.
    if len(types) == 1:
        return add_func_scope_type(
            # The first and only item of this container, accessed as either:
            # * If this container is a tuple, that item with fast indexing.
            # * If this container is a set, that item with slow iteration.
            cls=types[0] if isinstance(types, tuple) else next(iter(types)),
            func_scope=func_scope,
            exception_prefix=exception_prefix,
        )
    # Else, this container either contains two or more types.

    # If the caller did *NOT* explicitly pass the "is_unique" parameter, default
    # this parameter to true *ONLY* if this container is a set.
    if is_unique is None:
        is_unique = isinstance(types, set)
    # Else, the caller explicitly passed the "is_unique" parameter.
    #
    # In either case, "is_unique" is now a proper bool.
    assert isinstance(is_unique, bool)

    # ....................{ FORWARDREF                     }....................
    # True only if this container contains one or more beartype-specific forward
    # reference proxies. Although these proxies are technically isinstanceable
    # classes, attempting to pass these proxies as the second parameter to the
    # isinstance() builtin also raises exceptions when the underlying
    # user-defined classes proxied by these proxies have yet to be declared.
    # Since these proxies are thus *MUCH* more fragile than standard classes, we
    # reduce the likelihood of exceptions by deprioritizing these proxies in
    # this container (i.e., moving these proxies to the end of this container).
    is_types_ref = False

    # For each type in this container...
    for cls in types:
        # If this type is a beartype-specific forward reference proxy...
        if is_forwardref(cls):
            # print(f'Found forward reference proxy {repr(cls)}...')
            # Note that this container contains at least one such proxy.
            is_types_ref = True

            # Halt iteration.
            break

    # If this container contains at least one such proxy...
    if is_types_ref:
        # List of all such proxies in this container.
        #
        # Note that we intentionally avoid instantiating this pair of lists
        # above in the common case that this container contains no such proxies.
        types_ref: List[type] = []

        # List of all other types in this container (i.e., normal types that are
        # *NOT* beartype-specific forward reference proxies).
        types_nonref: List[type] = []

        # For each type in this container...
        for cls in types:
            # If this type is such a proxy, append this proxy to the list of all
            # such proxies.
            if is_forwardref(cls):
                types_ref.append(cls)
            # Else, this type is *NOT* such a proxy. In this case...
            else:
                # print(f'Appending non-forward reference proxy {repr(cls)}...')

                # If this non-proxy is *NOT* an isinstanceable class, raise an
                # exception.
                #
                # Note that the companion "types_ref" tuple is intentionally
                # *NOT* validated above. Why? Because doing so would prematurely
                # invoke the __instancecheck__() dunder method on the metaclass
                # of the proxies in that tuple, which would then erroneously
                # attempt to resolve the possibly undefined types to which those
                # proxies refer. Instead, simply accept that tuple of proxies as
                # is for now and defer validating those proxies for later.
                die_unless_type_isinstanceable(
                    cls=cls, exception_prefix=exception_prefix)

                # Append this proxy to the list of all non-proxy types
                types_nonref.append(cls)

        # If the caller guaranteed these tuples to be duplicate-free,
        # efficiently concatenate these lists into a tuple such that all
        # non-proxy types appear *BEFORE* all proxy types.
        if is_unique:
            types = tuple(types_nonref + types_ref)
        # Else, the caller failed to guarantee these tuples to be
        # duplicate-free. In this case, coerce these tuples into (in order):
        # * Sets, thus ignoring duplicates and ordering.
        # * Back into duplicate-free tuples.
        else:
            types = tuple(set(types_nonref)) + tuple(set(types_ref))
        # Else, the caller guaranteed these tuples to be duplicate-free.
    # Else, this container contains *NO* such proxies. In this case, preserve
    # the ordering of items in this container as is.
    else:
        # If this container is a set, coerce this frozenset into a tuple.
        if isinstance(types, Set):
            types = tuple(types)
        # Else, this container is *NOT* a set. By elimination, this container
        # should now be a tuple.
        #
        # In either case, this container should now be a tuple.

        # If this container is *NOT* a tuple or is a tuple containing one or
        # more items that are *NOT* isinstanceable classes, raise an exception.
        die_unless_object_isinstanceable(
            obj=types, exception_prefix=exception_prefix)
        # Else, this container is a tuple of only isinstanceable classes.

        # If the caller failed to guarantee this tuple to be duplicate-free,
        # coerce this tuple into (in order):
        # * A set, thus ignoring duplicates and ordering.
        # * Back into a duplicate-free tuple.
        if not is_unique:
            # print(f'Uniquifying type tuple {repr(types)} to...')
            types = tuple(set(types))
            # print(f'...uniquified type tuple {repr(types)}.')
        # Else, the caller guaranteed this tuple to be duplicate-free.

    # In either case, this container is now guaranteed to be a tuple containing
    # only duplicate-free classes.
    assert isinstance(types, tuple), (
        f'{exception_prefix}{repr(types)} not tuple.')

    # ....................{ CACHE                          }....................
    # If this tuple has *NOT* already been cached, do so.
    if types not in _tuple_union_to_tuple_union:
        _tuple_union_to_tuple_union[types] = types
    # Else, this tuple has already been cached. In this case, deduplicate this
    # tuple by reusing the previously cached tuple.
    else:
        types = _tuple_union_to_tuple_union[types]

    # ....................{ RETURN                         }....................
    # Return the name of a new parameter passing this tuple.
    return add_func_scope_attr(
        attr=types, func_scope=func_scope, exception_prefix=exception_prefix)


# ....................{ EXPRESSERS ~ type                  }....................
def express_func_scope_type_ref(
    # Mandatory parameters.
    func_scope: LexicalScope,
    forwardref: Pep484585ForwardRef,
    forwardrefs_class_basename: Optional[set],

    # Optional parameters.
    exception_prefix: str = 'Globally or locally scoped forward reference ',
) -> Tuple[str, Optional[set]]:
    '''
    Express the passed :pep:`484`- or :pep:`585`-compliant **forward reference**
    (i.e., fully-qualified or unqualified name of an arbitrary class that
    typically has yet to be declared) as a Python expression evaluating to this
    forward reference when accessed via the beartypistry singleton added as a
    new key-value pair of the passed dictionary, whose key is the string
    :attr:`beartype._check.checkmagic.ARG_NAME_TYPISTRY` and whose value is the
    beartypistry singleton.

    Parameters
    ----------
    func_scope : LexicalScope
        Local or global scope to add this forward reference to.
    forwardref : Pep484585ForwardRef
        Forward reference to be expressed relative to this scope.
    forwardrefs_class_basename : Optional[set]
        Set of all existing **relative forward references** (i.e., unqualified
        basenames of all types referred to by all relative forward references
        relative to this scope) if any *or* :data:`None` otherwise (i.e., if no
        relative forward references have been expressed relative to this scope).
    exception_prefix : str, optional
        Human-readable substring describing this forward reference in exception
        exception message. Defaults to a sensible string.

    Returns
    -------
    Tuple[str, Optional[set]]
        2-tuple ``(forwardref_expr, forwardrefs_class_basename)``, where:

        * ``forwardref_expr`` is the Python expression evaluating to this
          forward reference when accessed via the beartypistry singleton added
          to this scope.
        * ``forwardrefs_class_basename`` is either:

          * If this forward reference is a fully-qualified classname, the
            passed ``forwardrefs_class_basename`` set as is.
          * If this forward reference is an unqualified classname, either:

            * If the passed ``forwardrefs_class_basename`` set is *not*
              :data:`None`, this set with this classname added to it.
            * Else, a new set containing only this classname.

    Raises
    ------
    BeartypeDecorHintForwardRefException
        If this forward reference is *not* actually a forward reference.
    '''

    # Possibly undefined fully-qualified module name and possibly unqualified
    # classname referred to by this forward reference.
    ref_module_name, ref_name = get_hint_pep484585_ref_names(
        hint=forwardref, exception_prefix=exception_prefix)

    # If either...
    if (
        # This reference was instantiated with a module name...
        ref_module_name or
        # This classname contains one or more "." characters and is thus already
        # (...hopefully) fully-qualified...
        '.' in ref_name
    # Then this classname is either absolute *OR* relative to some module. In
    # either case, the class referred to by this reference can now be
    # dynamically imported at a later time. In this case...
    ):
        # Name of the hidden parameter providing this forward reference
        # proxy to be passed to this wrapper function.
        ref_expr = add_func_scope_ref(
            func_scope=func_scope,
            ref_module_name=ref_module_name,
            ref_name=ref_name,
            exception_prefix=exception_prefix,
        )
    # Else, this classname is unqualified. In this case...
    else:
        assert isinstance(forwardrefs_class_basename, NoneTypeOr[set]), (
            f'{repr(forwardrefs_class_basename)} neither set nor "None".')

        # If this set of unqualified classnames referred to by all relative
        # forward references has yet to be instantiated, do so.
        if forwardrefs_class_basename is None:
            forwardrefs_class_basename = set()
        # In any case, this set now exists.

        # Add this unqualified classname to this set.
        forwardrefs_class_basename.add(ref_name)

        # Placeholder substring to be replaced by the caller with a Python
        # expression evaluating to this unqualified classname canonicalized
        # relative to the module declaring the currently decorated callable
        # when accessed via the private "__beartypistry" parameter.
        ref_expr = (
            f'{CODE_HINT_REF_TYPE_BASENAME_PLACEHOLDER_PREFIX}'
            f'{ref_name}'
            f'{CODE_HINT_REF_TYPE_BASENAME_PLACEHOLDER_SUFFIX}'
        )

    # Return a 2-tuple of this expression and set of unqualified classnames.
    return ref_expr, forwardrefs_class_basename


# ....................{ PRIVATE ~ globals                  }....................
_tuple_union_to_tuple_union: Dict[TupleTypes, TupleTypes] = {}
'''
**Tuple union cache** (i.e., dictionary mapping from each tuple union passed to
the :func:`.add_func_scope_types` adder to that same union, preventing tuple
unions from being duplicated across calls to that adder).

This cache serves a dual purpose. Notably, this cache both enables:

* External callers to iterate over all previously instantiated forward reference
  proxies. This is particularly useful when responding to module reloading,
  which requires that *all* previously cached types be uncached.
* A minor reduction in space complexity by de-duplicating duplicating tuple
  unions. Since the existing ``callable_cached`` decorator could trivially do so
  as well, however, this is only a negligible side effect.
'''
