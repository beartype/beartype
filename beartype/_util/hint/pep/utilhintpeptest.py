#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint tester utilities** (i.e., callables
validating arbitrary objects to be PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
#FIXME: Generalize the die_unless_hint_pep_supported() and
#is_hint_pep_supported() functions to perform a genuine breadth-first traversal
#over all transitive arguments of the passed hint. Currently, these functions
#only shallowly inspect the first level of arguments of this hint. For
#example, if the "typing.Iterable" type is currently unsupported, then:
#    import typing
#    >>> hint_pep_unsupported = typing.Union[
#    ...     int, typing.Dict[str, typing.Iterable[str]]]
#    # This is what currently happens.
#    >>> is_hint_pep_supported(hint_pep_unsupported)
#    True
#    # This is what should happen instead.
#    >>> is_hint_pep_supported(hint_pep_unsupported)
#    False
#
#To implement this sanely, we'll probably want to define a new higher-level
#get_hint_pep_typing_deep_attrs_argless_to_args() getter calling the lower-level
#get_hint_pep_typing_attrs_argless_to_args() getter via a breadth-first traversal.
#For disambiguity, the latter getter should be renamed to
#get_hint_pep_typing_flat_attrs_argless_to_args().

# ....................{ IMPORTS                           }....................
from beartype.roar import (
    BeartypeDecorHintPepException,
    BeartypeDecorHintPepUnsupportedException,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.utilobject import (
    get_object_module_name_or_none,
    get_object_type,
)
from typing import Any, TypeVar, Union

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS ~ supported             }....................
_TYPING_ATTRS_ARGLESS_SUPPORTED = frozenset((
    Any,
    Union,
))
'''
Frozen set of all **argumentless typing attributes** (i.e., public attributes
of the :mod:`typing` module uniquely identifying PEP-compliant type hints
sans arguments) supported by the :func:`beartype.beartype` decorator.

This set is intended to be tested against typing attributes returned by the
:func:`get_hint_pep_typing_attrs_argless_to_args` getter function.
'''

# ....................{ EXCEPTIONS                        }....................
def die_if_hint_pep(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Type hint',
    exception_cls: type = BeartypeDecorHintPepException,
) -> None:
    '''
    Raise an exception if the passed object is a **PEP-compliant type
    hint** (i.e., :mod:`beartype`-agnostic annotation compliant with
    annotation-centric PEPs).

    This validator is effectively (but technically *not*) memoized. See the
    :func:`beartype._util.hint.utilhinttest.die_unless_hint` validator.

    Parameters
    ----------
    hint : object
        Object to be validated.
    hint_label : Optional[str]
        Human-readable label prefixing this object's representation in the
        exception message raised by this function. Defaults to 'Annotation'.
    exception_cls : Optional[type]
        Type of the exception to be raised by this function. Defaults to
        :class:`BeartypeDecorHintPepException`.

    Raises
    ----------
    exception_cls
        If this object is a PEP-compliant type hint.
    '''

    # If this hint is PEP-compliant, raise an exception of this class.
    if is_hint_pep(hint):
        assert isinstance(hint_label, str), (
            '{!r} not string.'.format(hint_label))
        assert isinstance(exception_cls, type), (
            '{!r} not a type.'.format(exception_cls))

        raise exception_cls(
            '{} {!r} is PEP-compliant.'.format(hint_label, hint))


def die_unless_hint_pep(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Type hint',
) -> None:
    '''
    Raise an exception unless the passed object is a **PEP-compliant type
    hint** (i.e., :mod:`beartype`-agnostic annotation compliant with
    annotation-centric PEPs).

    This validator is effectively (but technically *not*) memoized. See the
    :func:`beartype._util.hint.utilhinttest.die_unless_hint` validator.

    Parameters
    ----------
    hint : object
        Object to be validated.
    hint_label : Optional[str]
        Human-readable label prefixing this object's representation in the
        exception message raised by this function. Defaults to 'Annotation'.

    Raises
    ----------
    BeartypeDecorHintPepException
        If this object is *not* a PEP-compliant type hint.
    '''

    # If this hint is *NOT* PEP-compliant, raise an exception.
    if not is_hint_pep(hint):
        assert isinstance(hint_label, str), (
            '{!r} not string.'.format(hint_label))

        raise BeartypeDecorHintPepException(
            '{} {!r} not PEP-compliant.'.format(hint_label, hint))


def die_unless_hint_pep_supported(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Annotation',
) -> None:
    '''
    Raise an exception unless the passed object is a **PEP-compliant supported
    type hint** (i.e., :mod:`beartype`-agnostic annotation compliant with
    annotation-centric PEPs currently supported by the
    :func:`beartype.beartype` decorator).

    This validator is effectively (but technically *not*) memoized. See the
    :func:`beartype._util.hint.utilhinttest.die_unless_hint` validator.

    Caveats
    ----------
    **This validator only shallowly validates this object.** If this object is
    a subscripted PEP-compliant type hint (e.g., ``Union[str, List[int]]``),
    this validator ignores all subscripted arguments (e.g., ``List[int]``) on
    this hint and may thus return false positives for hints that are directly
    supported but whose subscripted arguments are not.

    To deeply validate this object, iteratively call this validator during a
    recursive traversal over each subscripted argument of this object.

    Parameters
    ----------
    hint : object
        Object to be validated.
    hint_label : Optional[str]
        Human-readable label prefixing this object's representation in the
        exception message raised by this function. Defaults to 'Annotation'.

    Raises
    ----------
    BeartypeDecorHintPepException
        If this object is *not* a PEP-compliant type hint.
    BeartypeDecorHintPepUnsupportedException
        If this object is a PEP-compliant type hint but is currently
        unsupported by the :func:`beartype.beartype` decorator.
    '''

    # If this object is a supported PEP-compliant type hint, reduce to a noop.
    #
    # Note that this memoized call is intentionally passed positional rather
    # than keyword parameters to maximize efficiency.
    if is_hint_pep_supported(hint):
        return
    # Else, this object is *NOT* a supported PEP-compliant type hint. In this
    # case, subsequent logic raises an exception specific to the passed
    # parameters.
    assert isinstance(hint_label, str), (
        '{!r} not string.'.format(hint_label))

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with is_hint_pep_supported() below.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilhintpepget import (
        get_hint_pep_typing_attrs_argless_to_args)

    # If this hint is *NOT* PEP-compliant, raise an exception.
    die_unless_hint_pep(hint=hint, hint_label=hint_label)
    # Else, this hint is PEP-compliant.

    # Substring suffixing exception messages raised by this function.
    EXCEPTION_MESSAGE_SUFFIX = 'currently unsupported by @beartype.'

    #FIXME: Remove *AFTER* implementing support for type variables.
    # If this hint is parametrized by one or more type variables, raise an
    # exception. Type variables require non-trivial decorator support that has
    # yet to be fully implemented.
    if is_hint_pep_typevared(hint):
        raise BeartypeDecorHintPepUnsupportedException(
            '{} "TypeVar"-parametrized generic PEP type {!r} {}'.format(
                hint_label, hint, EXCEPTION_MESSAGE_SUFFIX))

    # Dictionary mapping each argumentless public attribute of the "typing"
    # module uniquely identifying this hint if any to the tuple of those
    # arguments *OR* "None" otherwise.
    hint_typing_attrs_argless_to_args = (
        get_hint_pep_typing_attrs_argless_to_args(hint))

    # If no such attributes exists, raise an exception.
    #
    # Note that this should *NEVER* happen. By definition, *ALL* PEP-compliant
    # hints are uniquely identified by one or public attribute(s) of the
    # "typing" module. Nonetheless, this is the real world. Damn you, Murphy!
    if not hint_typing_attrs_argless_to_args:
        raise BeartypeDecorHintPepUnsupportedException(
            '{} PEP type {!r} unassociated with "typing" types.'.format(
                hint_label, hint))
    # Else, one or more such attributes exist.

    # For each argumentless typing attribute associated with this hint...
    for hint_typing_attr_argless in hint_typing_attrs_argless_to_args.keys():
        # If this attribute is unsupported, raise an exception.
        if hint_typing_attr_argless not in _TYPING_ATTRS_ARGLESS_SUPPORTED:
            raise BeartypeDecorHintPepUnsupportedException(
                '{} PEP type {!r} supertype {!r} {}'.format(
                    hint_label,
                    hint,
                    hint_typing_attr_argless,
                    EXCEPTION_MESSAGE_SUFFIX,
                ))

    # Else something unknown has gone awfully awry. Raise a fallback exception!
    raise BeartypeDecorHintPepUnsupportedException(
        '{} PEP type {!r} {}'.format(
            hint_label, hint, EXCEPTION_MESSAGE_SUFFIX))

# ....................{ TESTERS                           }....................
@callable_cached
def is_hint_pep(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a **PEP-compliant type hint** (i.e.,
    object either directly defined by the :mod:`typing` module *or* whose type
    subclasses one or more classes directly defined by the :mod:`typing`
    module).

    This tester is memoized for efficiency.

    Motivation
    ----------
    Standard Python types allow callers to test for compliance with protocols,
    interfaces, and abstract base classes by calling either the
    :func:`isinstance` or :func:`issubclass` builtins. This is the
    well-established Pythonic standard for deciding conformance to an API.

    Insanely, `PEP 484`_ *and* the :mod:`typing` module implementing `PEP 484`_
    reject community standards by explicitly preventing callers from calling
    either the :func:`isinstance` or :func:`issubclass` builtins on most but
    *not* all `PEP 484`_ objects and types. Moreover, neither `PEP 484`_ nor
    :mod:`typing` implement public APIs for testing whether arbitrary objects
    comply with `PEP 484`_ or :mod:`typing`.

    Thus this function, which "fills in the gaps" by implementing this
    laughably critical oversight.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a PEP-compliant type hint.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Note that this implementation could probably be reduced to simply calling
    # the get_hint_pep_typing_attrs_argless_to_args() function and testing
    # whether the return value is "None" or not. While certainly more compact
    # and convenient than the current approach, that refactored approach would
    # also be considerably more fragile, failure-prone, and subject to
    # whimsical "improvements" in the already overly hostile "typing" API. Why?
    # Because the get_hint_pep_typing_attrs_argless_to_args() function:
    #
    # * Parses the machine-readable string returned by the __repr__() dunder
    #   method of "typing" types. Since that string is *NOT* standardized by
    #   PEP 484 or any other PEP, "typing" authors remain free to violate this
    #   pseudo-standard in any manner and at any time of their choosing.
    # * Suffers common edge cases for "typing" types whose __repr__() dunder
    #   methods fail to comply with the non-standard implemented by their
    #   sibling types. This includes the common "TypeVar" type.
    # * Calls this tester function to decide whether the passed object is a
    #   PEP 484 type hint or not before subjecting that object to further
    #   introspection, which would clearly complicate implementing this tester
    #   function in terms of that getter function.
    #
    # In contrast, the current approach only tests the standardized "__name__"
    # and "__module__" dunder attributes and is thus significantly more robust
    # against whimsical destruction by "typing" authors.

    # Either the passed object if this object is a class *OR* the class of this
    # object otherwise (i.e., if this object is *NOT* a class).
    hint_type = get_object_type(hint)

    # Return true only if either...
    #
    # Note that there might exist an alternate means of deciding this boolean,
    # documented here merely for completeness:
    #
    #     try:
    #         isinstance(obj, object)
    #         return False
    #     except TypeError as type_error:
    #         return str(type_error).endswith(
    #             'cannot be used with isinstance()')
    #
    # The above effectively implements an Aikido throw by using the fact that
    # "typing" types prohibit isinstance() calls against those types. While
    # clever (and deliciously obnoxious), the above logic:
    #
    # * Requires catching exceptions in the common case and is thus *MUCH* less
    #   efficient than the preferable approach implemented here.
    # * Assumes that *ALL* "typing" types prohibit such calls. Sadly, only a
    #   proper subset of such types prohibit such calls.
    # * Assumes that those "typing" types that do prohibit such calls raise
    #   exceptions with reliable messages across *ALL* Python versions.
    #
    # In short, no general-purpose clever solution exists. *sigh*
    return (
        # If this type is defined by the "typing" module, return true.
        is_hint_pep_typing(hint_type) or
        # Else, this type is *NOT* defined by the "typing" module.
        #
        # For each superclass of this class, if this superclass is defined by
        # the "typing" module, return true.
        #
        # This edge case is required to handle user-defined classes subclassing
        # "typing" types. Typically, iterating over the "__mro__" dunder attribute
        # is a bad idea for such classes. Why? Because the "typing" module subjects
        # these classes to "type erasure," an invasive process silently replacing
        # most "typing" types specified as superclasses of user-defined classes
        # (e.g., "List[int]") with parallel non-"typing" types (e.g., "list").
        #
        # Thankfully, the "typing" module *ALSO* silently injects the
        # "typing.Generic" superclass back into subclasses subject to type erasure.
        # This guarantees the method-resolution order (MRO) of *ALL* "typing" types
        # (including both types directly defined by the "typing" module and
        # user-defined classes subclassing those types) contain at least one type
        # directly defined by the "typing" module -- even after type erasure: e.g.,
        #
        #    >>> import typing
        #    >>> T = typing.TypeVar('T')
        #    >>> class CustomGeneric(typing.Iterable[T], typing.Container[t]): pass
        #    (__main__.CustomGeneric,
        #     collections.abc.Iterable,
        #     collections.abc.Container,
        #     typing.Generic,
        #     object)
        #
        # Note the removal of the "typing.Iterable" and "typing.Container" types
        # and insertion of the "typing.Generic" type in the above example.
        any(
            is_hint_pep_typing(hint_supertype)
            for hint_supertype in hint_type.__mro__
        )
        # Else, neither this type nor any superclass of this type is defined by
        # the "typing" module. Ergo, this is *NOT* a PEP-compliant type hint.
    )


@callable_cached
def is_hint_pep_supported(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a **PEP-compliant supported type
    hint** (i.e., :mod:`beartype`-agnostic annotation compliant with
    annotation-centric PEPs currently supported by the
    :func:`beartype.beartype` decorator).

    This tester is memoized for efficiency.

    Caveats
    ----------
    **This tester only shallowly inspects this object.** If this object is a
    subscripted PEP-compliant type hint (e.g., ``Union[str, List[int]]``), this
    tester ignores all subscripted arguments (e.g., ``List[int]``) on this hint
    and may thus return false positives for hints that are directly supported
    but whose subscripted arguments are not.

    To deeply inspect this object, iteratively call this tester during a
    recursive traversal over each subscripted argument of this object.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a supported PEP-compliant type hint.
    '''

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with die_unless_hint_pep_supported().
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # If this hint is either...
    if (
        # Not PEP-compliant *OR*...
        not is_hint_pep(hint) or

        #FIXME: Remove *AFTER* implementing support for type variables.
        # PEP-compliant but parametrized by one or more type variables...
        #
        # Type variables require non-trivial decorator support that has
        # yet to be fully implemented.
        is_hint_pep_typevared(hint)
    # Return false.
    ):
        return False
    # Else, this hint is PEP-compliant and *NOT* parametrized by one or more
    # type variables.

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilhintpepget import (
        get_hint_pep_typing_attrs_argless_to_args)

    # Dictionary mapping each argumentless public attribute of the "typing"
    # module uniquely identifying this hint if any to the tuple of those
    # arguments *OR* "None" otherwise.
    hint_typing_attrs_argless_to_args = (
        get_hint_pep_typing_attrs_argless_to_args(hint))

    # Return true only if...
    return all(
        # This attribute is supported...
        hint_typing_attr_argless in _TYPING_ATTRS_ARGLESS_SUPPORTED
        # For each argumentless typing attribute associated with this hint.
        for hint_typing_attr_argless in (
            hint_typing_attrs_argless_to_args.keys())
    )


#FIXME: Unit test us up.
def is_hint_pep_typing(hint_type: type) -> bool:
    '''
    ``True`` only if the passed object is defined by the :mod:`typing` module.

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is defined by the :mod:`typing` module.
    '''

    # Return true only if this type is defined by the "typing" module.
    #
    # Note that there might exist an alternate means of deciding this boolean,
    # documented here merely for completeness:
    #
    #     try:
    #         isinstance(obj, object)
    #         return False
    #     except TypeError as type_error:
    #         return str(type_error).endswith(
    #             'cannot be used with isinstance()')
    #
    # The above effectively implements an Aikido throw by using the fact that
    # "typing" types prohibit isinstance() calls against those types. While
    # clever (and deliciously obnoxious), the above logic:
    #
    # * Requires catching exceptions in the common case and is thus *MUCH* less
    #   efficient than the preferable approach implemented here.
    # * Assumes that *ALL* "typing" types prohibit such calls. Sadly, only a
    #   proper subset of such types prohibit such calls.
    # * Assumes that those "typing" types that do prohibit such calls raise
    #   exceptions with reliable messages across *ALL* Python versions.
    #
    # In short, there is no general-purpose clever solution. *sigh*
    return get_object_module_name_or_none(hint_type) == 'typing'

# ....................{ TESTERS ~ newtype                 }....................
#FIXME: Unit test us up.
#FIXME: Actually call this tester elsewhere to generate code type-checking
#these outrageously silly objects by simply type-checking the PEP-noncompliant
#type stored in the "__supertype__" dunder attribute: e.g.,
#    >>> from typing import NewType
#    >>> UserId = t.NewType('UserId', int)
#    >>> UserId.__supertype__
#    int

def is_hint_newtype(hint: object) -> bool:
    '''
    ``True`` only if the passed object either is a `PEP 484`_ **new type
    alias** (i.e., closure generated by the :mod:`typing.NewType` closure
    factory).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **New type aliases are a complete farce and thus best avoided.**
    Specifically, these PEP-compliant type hints are *not* actually types but
    rather **identity closures** that return their passed parameters as is.
    Instead, where distinct types are:

    * *Not* required, simply annotate parameters and return values with the
      desired superclasses.
    * Required, simply:

      * Subclass the desired superclasses as usual.
      * Annotate parameters and return values with those subclasses.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a new type alias.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Return true only if this hint is a "NewType"-generated closure.
    #
    # Note that this test derives from the observation that the concatenation
    # of this object's "__qualname__" and "__module" dunder attributes suffices
    # to produce a string unambiguously identifying whether this hint is a
    # "NewType"-generated closure: e.g.,
    #
    #    >>> from typing import NewType
    #    >>> UserId = t.NewType('UserId', int)
    #    >>> UserId.__qualname__
    #    >>> 'NewType.<locals>.new_type'
    #    >>> UserId.__module__
    #    >>> 'typing'
    #
    # Lastly, note that "__qualname__" is safely available under Python >= 3.3.
    return (hint.__module__ + hint.__qualname__).startswith('typing.NewType.')

# ....................{ TESTERS ~ typevar                 }....................
def is_hint_pep_typevar(hint: object) -> bool:
    '''
    ``True`` only if the passed object either is a `PEP 484`_ **type variable**
    (i.e., instance of the :class:`TypeVar` class).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Motivation
    ----------
    Since type variables are not themselves types but rather placeholders
    dynamically replaced with types by type checkers according to various
    arcane heuristics, both type variables and types parametrized by type
    variables warrant special-purpose handling.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a type variable.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Return true only if this is a type variable.
    return isinstance(hint, TypeVar)


def is_hint_pep_typevared(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a PEP-compliant type hint
    parametrized by one or more **type variables** (i.e., instances of the
    :class:`TypeVar` class).

    This tester detects both:

    * **Direct parametrizations** (i.e., cases in which this object itself is
      directly parametrized by type variables).
    * **Superclass parametrizations** (i.e., cases in which this object is
      indirectly parametrized by one or more superclasses of its class being
      directly parametrized by type variables).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object type to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a PEP-compliant type hint parametrized
        by one or more type variables.

    Examples
    ----------

        >>> import typing
        >>> from beartype._util.hint.pep.utilhintpeptest import (
        ...     is_hint_pep_typevared)
        >>> T = typing.TypeVar('T')
        >>> class UserList(typing.List[T]): pass
        # Unparametrized type hint.
        >>> is_hint_pep_typevared(typing.List[int])
        False
        # Directly parametrized type hint.
        >>> is_hint_pep_typevared(typing.List[T])
        True
        # Superclass-parametrized type hint.
        >>> is_hint_pep_typevared(UserList)
        True
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilhintpepget import get_hint_pep_typevars

    # Return true only if this is a "typing" type parametrized by one or more
    # type variables, trivially detected by testing whether the tuple of all
    # type variables parametrizing this "typing" type if this type is a generic
    # (e.g., "typing._GenericAlias" subtype) *OR* the empty tuple otherwise is
    # non-empty.
    #
    # Note that:
    #
    # * The "typing._GenericAlias.__parameters__" dunder attribute tested here
    #   is defined by the typing._collect_type_vars() function at subtype
    #   declaration time. Yes, this is insane. Yes, this is PEP 484.
    # * This trivial test implicitly handles superclass parametrizations.
    #   Thankfully, the "typing" module percolates the "__parameters__" dunder
    #   attribute from "typing" pseudo-superclasses to user-defined subclasses
    #   during PEP 560-style type erasure. Finally: they did something right.
    return bool(get_hint_pep_typevars(hint))
