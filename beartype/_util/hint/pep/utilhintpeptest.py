#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint tester utilities** (i.e., callables
validating arbitrary objects to be PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import (
    BeartypeDecorHintValuePepException,
    BeartypeDecorHintValuePepUnsupportedException,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.utilobj import (
    get_object_module_name_or_none,
    get_object_type,
)
from typing import Any, TypeVar, Union

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS ~ supported             }....................
_TYPING_ATTRS_SUPPORTED = frozenset((
    Any,
    Union,
))
'''
Frozen set of all **typing attributes** (i.e., public attributes of the
:mod:`typing` module uniquely identifying PEP-compliant type hints defined via
the :mod:`typing` module) supported by the :func:`beartype.beartype` decorator.

This set is intended to be tested against typing attributes returned by the
:func:`get_hint_typing_attrs_untypevared_or_none` getter function.
'''

# ....................{ EXCEPTIONS                        }....................
#FIXME: Unit test us up.
def die_if_hint_pep(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Annotation',
    exception_cls: type = BeartypeDecorHintValuePepException,
) -> None:
    '''
    Raise an exception if the passed object is a **PEP-compliant type
    hint** (i.e., :mod:`beartype`-agnostic annotation compliant with
    annotation-centric PEPs).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be validated.
    hint_label : Optional[str]
        Human-readable noun prefixing this object's representation in the
        exception message raised by this function. Defaults to 'Annotation'.
    exception_cls : Optional[type]
        Type of the exception to be raised by this function. Defaults to
        :class:`BeartypeDecorHintValuePepException`.

    Raises
    ----------
    exception_cls
        If this object is a PEP-compliant type hint.
    '''

    # If this hint is PEP-compliant, raise an exception of this class.
    if is_hint_pep(hint):
        assert isinstance(hint_label, str), (
            '{!r} not a string.'.format(hint_label))
        assert isinstance(exception_cls, type), (
            '{!r} not a type.'.format(exception_cls))

        raise exception_cls(
            '{} {!r} is PEP-compliant.'.format(hint_label, hint))


#FIXME: Unit test us up.
def die_unless_hint_pep(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Annotation',
) -> None:
    '''
    Raise an exception unless the passed object is a **PEP-compliant type
    hint** (i.e., :mod:`beartype`-agnostic annotation compliant with
    annotation-centric PEPs).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be validated.
    hint_label : Optional[str]
        Human-readable noun prefixing this object's representation in the
        exception message raised by this function. Defaults to 'Annotation'.

    Raises
    ----------
    BeartypeDecorHintValuePepException
        If this object is *not* a PEP-compliant type hint.
    '''

    # If this hint is *NOT* PEP-compliant, raise an exception.
    if not is_hint_pep(hint):
        assert isinstance(hint_label, str), (
            '{!r} not a string.'.format(hint_label))

        raise BeartypeDecorHintValuePepException(
            '{} {!r} not PEP-compliant.'.format(hint_label, hint))


#FIXME: Unit test us up.
@callable_cached
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

    This validator is memoized for efficiency.

    Parameters
    ----------
    hint : object
        Object to be validated.
    hint_label : Optional[str]
        Human-readable noun prefixing this object's representation in the
        exception message raised by this function. Defaults to 'Annotation'.

    Raises
    ----------
    BeartypeDecorHintValuePepUnsupportedException
        If this object is either:

        * *Not* a PEP-compliant type hint.
        * Is a PEP-compliant type hint but is currently unsupported by the
          :func:`beartype.beartype` decorator.
    BeartypeDecorHintValuePep560Exception
        If this object is a user-defined class subclassing one or more
        :mod:`typing` attributes that either:

        * Fail to define the PEP-specific ``__orig_bases__`` dunder
          attribute.
        * Defines that attribute but that attribute describes either:

          * No :mod:`typing` attributes.
          * :data:`SIZE_BIG` or more :mod:`typing` attributes.
    '''
    assert isinstance(hint_label, str), (
        '{!r} not a string.'.format(hint_label))

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilhintpepget import (
        get_hint_typing_attrs_untypevared_or_none)

    # If this hint is *NOT* PEP-compliant, raise an exception.
    die_unless_hint_pep(hint=hint, hint_label=hint_label)
    # Else, this hint is PEP-compliant.

    # Public attribute(s) of the "typing" module uniquely identifying this hint
    # if any *OR* "None" otherwise.
    hint_typing_attrs = get_hint_typing_attrs_untypevared_or_none(hint)

    # If no such attributes exists, raise an exception.
    #
    # Note that this should *NEVER* happen. By definition, *ALL* PEP-compliant
    # hints are uniquely identified by one or public attribute(s) of the
    # "typing" module. Nonetheless, this is the real world. Damn you, Murphy!
    if not hint_typing_attrs:
        raise BeartypeDecorHintValuePepUnsupportedException(
            '{} PEP type {!r} unassociated with "typing" types.'.format(
                hint_label, hint))
    # Else, one or more such attributes exist.

    # Template for unsupported exception messages raised by this function.
    EXCEPTION_MESSAGE_TEMPLATE = '{} currently unsupported by @beartype.'

    # For each such attribute...
    for hint_typing_attr in hint_typing_attrs:
        # If this attribute is unsupported, raise an exception.
        if hint_typing_attr not in _TYPING_ATTRS_SUPPORTED:
            raise BeartypeDecorHintValuePepUnsupportedException(
                EXCEPTION_MESSAGE_TEMPLATE.format(
                    '{} PEP type {!r} supertype {!r}'.format(
                        hint_label, hint, hint_typing_attr)))

    # If this hint is parametrized by one or more type variables, raise an
    # exception. Type variables require non-trivial decorator support that has
    # yet to be fully implemented.
    if is_hint_typing_typevared(hint):
        raise BeartypeDecorHintValuePepUnsupportedException(
            EXCEPTION_MESSAGE_TEMPLATE.format(
                '{} variable-parametrized generic PEP type {!r}'.format(
                    hint_label, hint)))
    # Else, this hint is fully supported. Phew!

# ....................{ TESTERS ~ private                 }....................
#FIXME: *THIS FUNCTION APPEARS TO BE SLIGHTLY BROKEN,* which is bad. What's
#worse is that tests failed to detect this, suggesting tests also need to be
#amended. What's the issue? Walking "__mro__", of course, which is a lie for
#"typing' subtypes. Instead, we need to call the newly defined
#get_hint_typing_supertypes() function and return True only if that tuple is
#non-empty. Trivial, given that function. *sigh*
#FIXME: Detect functions created by "typing.NewType(subclass_name, superclass)"
#somehow, either here or elsewhere. These functions are simply the identity
#function at runtime and thus a complete farce. They're not actually types!
#Ideally, we would replace each such function by the underlying "superclass"
#type originally passed to that function, but we have no idea if that's even
#feasible. Welcome to "typing", friends.
@callable_cached
def is_hint_pep(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a **typing type hint** (i.e.,
    `PEP 484`_-compliant class or object defined via the :mod:`typing` module).

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
        ``True`` only if this object is a :mod:`typing` type hint.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Note that this implementation could probably be reduced to simply calling
    # the get_hint_typing_attrs_untypevared_or_none() function and testing
    # whether the return value is "None" or not. While certainly more compact
    # and convenient than the current approach, that refactored approach would
    # also be considerably more fragile, failure-prone, and subject to
    # whimsical "improvements" in the already overly hostile "typing" API. Why?
    # Because the get_hint_typing_attrs_untypevared_or_none() function:
    #
    # * Parses the machine-readable string returned by the __repr__() dunder
    #   method of "typing" types. Since this string is *NOT* standardized by
    #   PEP 484 or any other PEP, "typing" authors remain free to violate this
    #   method in any manner of their choosing.
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

    #FIXME: Stop doing this, please. We should no longer require this.
    # Either the passed object if this object is a class *OR* the class of this
    # object otherwise (i.e., if this object is *NOT* a class).
    hint_type = get_object_type(hint)

    # If this type is defined by the "typing" module, return true.
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
    if is_hint_typing(hint_type):
        return True
    # Else, this type is *NOT* defined by the "typing" module.

    # For each superclass of this class...
    #
    # This edge case is required to handle user-defined subclasses declared in
    # user-defined modules of superclasses declared by the "typing" module:
    #
    #    # In a user-defined module...
    #    from typing import TypeVar, Generic
    #    T = TypeVar('T')
    #    class UserDefinedGeneric(Generic[T]): pass
    for hint_supertype in hint_type.__mro__:
        # If this superclass is defined by "typing", return true.
        if is_hint_typing(hint_supertype):
            return True

    # Else, neither this type nor any superclass of this type is defined by the
    # "typing" module. Ergo, this is *NOT* a PEP 484-compliant type.
    return False



#FIXME: Unit test us up.
def is_hint_typing(hint_type: type) -> bool:
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

# ....................{ TESTERS ~ typevar                 }....................
def is_hint_typing_typevar(hint: object) -> bool:
    '''
    ``True`` only if the passed object either is a `PEP 484`_ **type variable**
    (i.e., instance of the :mod:`typing.TypeVar` class).

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


#FIXME: Generalize the is_hint_typing_typevared() to also iteratively
#inspect each superclass listed by the newly defined
#utilpep560.get_superclasses_original() function. Given that function,
#generalizing this function becomes thankfully trivial. See the end of this
#submodule for implementation details.
#FIXME: Unit test that up as well.
@callable_cached
def is_hint_typing_typevared(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a `PEP 484`_ type parametrized by one
    or more type variables (e.g., ``typing.List[typing.TypeVar['T']]``).

    This tester is memoized for efficiency.

    Parameters
    ----------
    hint : object
        Object type to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is `PEP 484`_ type parametrized by one or
        more type variables.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    #FIXME: Consider replacing with this more exacting test:
    #return is_hint_pep(hint) and bool(getattr(hint, '__parameters__', ()))

    # Return true only if this is a "typing" type parametrized by one or more
    # type variables, trivially detected by testing whether the tuple of all
    # type variables parametrizing this "typing" type if this type is a generic
    # (e.g., "typing._GenericAlias" subtype) *OR* the empty tuple otherwise is
    # non-empty.
    #
    # Note that the "typing._GenericAlias.__parameters__" dunder attribute
    # tested here is defined by the typing._collect_type_vars() function at
    # subtype declaration time. Yes, this is insane. Yes, this is PEP 484.
    return bool(getattr(hint, '__parameters__', ()))
