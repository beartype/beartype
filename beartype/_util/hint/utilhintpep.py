#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint utilities.**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
import typing
from beartype.roar import BeartypeDecorHintValuePepException
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cache.list.utillistfixedpool import (
    acquire_fixed_list, release_fixed_list)
from beartype._util.utilobj import (
    SENTINEL,
    get_object_module_name_or_none,
    get_object_type,
)
from typing import Any, TypeVar, Union

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
_GET_HINT_TYPING_ATTRS_OR_NONE_SUPERCLASSES_MAX = 64
'''
Maximum number of :mod:`typing` superclasses the
:func:`get_hint_typing_attrs_or_none` getter function permits user-defined
classes to subclass.
'''

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
:func:`get_hint_typing_attrs_or_none` getter function.
'''

# ....................{ EXCEPTIONS                        }....................
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
    BeartypeDecorHintValuePepException
        If this object is either:

        * *Not* a PEP-compliant type.
        * Is a PEP-compliant type but is either:

          * Currently unsupported by :func:`beartype.beartype`.
          * A user-defined class subclassing one or more :mod:`typing`
            superclasses that either:

            * Fails to define the PEP-specific ``__orig_bases__`` dunder
              attribute.
            * Defines that attribute but that attribute contains either:

              * No :mod:`typing` superclasses.
              * :data:`_GET_HINT_TYPING_ATTRS_OR_NONE_SUPERCLASSES_MAX` or more
                :mod:`typing` superclasses. The
                :mod:`get_hint_typing_attrs_or_none` function underlying this
                function internally reuses fixed lists of this size to
                efficiently iterate these superclasses.
    '''
    assert isinstance(hint_label, str), (
        '{!r} not a string.'.format(hint_label))

    # If this hint is *NOT* PEP-compliant, raise an exception.
    die_unless_hint_pep(hint=hint, hint_label=hint_label)
    # Else, this hint is PEP-compliant.

    # Public attribute(s) of the "typing" module uniquely identifying this hint
    # if any *OR* "None" otherwise.
    hint_typing_attrs = get_hint_typing_attrs_or_none(hint)

    # If no such attributes exists, raise an exception.
    #
    # Note that this should *NEVER* happen. By definition, *ALL* PEP-compliant
    # hints are uniquely identified by one or public attribute(s) of the
    # "typing" module. Nonetheless, this is the real world. Damn you, Murphy!
    if not hint_typing_attrs:
        raise BeartypeDecorHintValuePepException(
            '{} PEP type {!r} unassociated with "typing" types.'.format(
                hint_label, hint))
    # Else, one or more such attributes exist.

    # Template for unsupported exception messages raised by this function.
    EXCEPTION_MESSAGE_TEMPLATE = '{} currently unsupported by @beartype.'

    # If two or more such attributes exist...
    if isinstance(hint_typing_attrs, tuple):
        # For each such attribute...
        for hint_typing_attr in hint_typing_attrs:
            # If this attribute and thus this hint is unsupported, raise an
            # exception.
            if hint_typing_attr not in _TYPING_ATTRS_SUPPORTED:
                raise BeartypeDecorHintValuePepException(
                    EXCEPTION_MESSAGE_TEMPLATE.format(
                        '{} PEP type {!r} supertype {!r}'.format(
                            hint_label, hint, hint_typing_attr)))
    # Else, only one such attribute exists.
    #
    # If this attribute and thus this hint is unsupported, raise an exception.
    # Note that, as there exists a one-to-one relationship between this hint
    # and this attribute, this attribute need *NOT* be formatted into this
    # exception message as well.
    elif hint_typing_attrs not in _TYPING_ATTRS_SUPPORTED:
        raise BeartypeDecorHintValuePepException(
            EXCEPTION_MESSAGE_TEMPLATE.format(
                '{} PEP type {!r}'.format(hint_label, hint)))
    # Else, this hint is superficially supported. This does *NOT* necessarily
    # imply this hint to be fully supported.

    # If this hint is parametrized by one or more type variables, raise an
    # exception. Type variables require non-trivial decorator support that has
    # yet to be fully implemented.
    if is_hint_typing_typevared(hint):
        raise BeartypeDecorHintValuePepException(
            EXCEPTION_MESSAGE_TEMPLATE.format(
                '{} variable-parametrized generic PEP type {!r}'.format(
                    hint_label, hint)))
    # Else, this hint is fully supported. Phew!

# ....................{ TESTERS ~ private                 }....................
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
    # the get_hint_typing_attrs_or_none() function and testing whether the
    # return value is "None" or not. While certainly more compact and
    # convenient than the current approach, that refactored approach would also
    # be considerably more fragile, failure-prone, and subject to whimsical
    # "improvements" in the already overly hostile "typing" API. Why? Because
    # the get_hint_typing_attrs_or_none() function:
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
    if get_object_module_name_or_none(hint_type) == 'typing':
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
        if get_object_module_name_or_none(hint_supertype) == 'typing':
            return True

    # Else, neither this type nor any superclass of this type is defined by the
    # "typing" module. Ergo, this is *NOT* a PEP 484-compliant type.
    return False

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

# ....................{ GETTERS ~ attrs                   }....................
#FIXME: To be genuinely useful during our breadth-first traversal of
#PEP-compliant type hints, this getter should probably be mildly refactored to
#return a dictionary mapping from each typing attribute to the original
#parametrized "typing" superclass associated with that attribute if the type
#hint is a user-defined subclass of one or more "typing" superclasses: e.g.,
#
#        >>> import typing
#        >>> from beartype._util.hint.utilhintpep import get_hint_typing_attrs_or_none
#        >>> T = typing.TypeVar('T')
#        >>> class Duplicity(typing.Iterable[T], typing.Container[T]): pass
#        # This is what this function currently returns.
#        >>> get_hint_typing_attrs_or_none(Duplicity)
#        (typing.Iterable, typing.Container)
#        # This is what this function should return instead.
#        >>> get_hint_typing_attrs_or_none(Duplicity)
#        {typing.Iterable: typing.Iterable[T],
#         typing.Container: typing.Container[T]}
#
#The latter is strongly preferable, as it preserves essential metadata required
#for code generation during breadth-first traversals.
#FIXME: Actually, we probably want to also refactor this getter to return a
#2-dictionary "{hint_typing_attr: hint}" when passed a user-defined class
#subclassing exactly one "typing" superclass: e.g.,
#
#        >>> import collections.abc, typing
#        >>> from beartype._util.hint.utilhintpep import get_hint_typing_attrs_or_none
#        >>> T = typing.TypeVar('T')
#        >>> class Genericity(collections.abc.Sized, typing.Generic[T]): pass
#        # This is what this function currently returns.
#        >>> get_hint_typing_attrs_or_none(Genericity)
#        typing.Generic
#        # This is what this function should return instead.
#        >>> get_hint_typing_attrs_or_none(Duplicity)
#        {typing.Generic: typing.Generic[T]}
#FIXME: Actually, rather than heavily refactor this function, we probably just
#want to copy-and-paste this function's implementation modified to suite the
#specific needs of our breadth-first traversal. Maybe. This function's current
#implementation is suitable for other needs (e.g., die_unless_hint_pep_supported()) and
#should thus probably be preserved as is. *shrug*

@callable_cached
def get_hint_typing_attrs_or_none(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Annotation',
) -> 'NoneTypeOr[object]':
    '''
    **Typing attribute(s)** (i.e., public attribute(s) of the :mod:`typing`
    module uniquely identifying the passed PEP-compliant type hint defined via
    the :mod:`typing` module) associated with this class or object if any *or*
    ``None`` otherwise.

    This getter function associates arbitrary PEP-compliant classes and objects
    with corresponding public attributes of the :mod:`typing` module, which
    effectively serve as unique pseudo-superclasses of those classes and
    objects. These attributes are typically *not* superclasses, as most actual
    :mod:`typing` superclasses are private, fragile, and prone to extreme
    alteration or even removal between major Python versions. Nonetheless,
    these attributes are sufficiently unique to enable callers to distinguish
    between numerous broad categories of :mod:`typing` behaviour and logic.

    For efficiency, this getter function is memoized and returns either:

    * A single typing attribute if the passed object is associated with exactly
      a single typing attribute. This minimizes memoization space costs for the
      common case by avoiding unnecessary tuple instantiations as well forcing
      callers to handle this common case *without* iteration, which is
      surprisingly slow in Python.
    * A tuple of one or more typing attributes if the passed object is
      associated with one or more typing attributes.

    Motivation
    ----------
    As the :func:`is_hint_pep` tester function attests, both `PEP 484` and
    the :mod:`typing` module implementing `PEP 484` are functionally deficient
    with respect to their public APIs. Neither provide external callers any
    means of deciding the types of arbitrary `PEP 484`_-compliant classes or
    objects. For example, there exists no standard means of identifying the
    parametrized subtype ``typing.List[int]`` as a parametrization of the
    unparameterized base type ``type.List``.

    Thus this function, which "fills in the gaps" by implementing this
    laughably critical oversight.

    Parameters
    ----------
    hint : object
        Object to be inspected.
    hint_label : Optional[str]
        Human-readable noun prefixing this object's representation in the
        exception message raised by this function. Defaults to 'Annotation'.

    Returns
    ----------
    NoneTypeOr[object]
        Either:

        * If this object is uniquely identified by:

          * One public attribute of the :mod:`typing` module, that attribute.
          * One or more public attributes of the :mod:`typing` module, a tuple
            listing these attributes in the same order (e.g., superclass order
            for user-defined types).

        * Else, ``None``.

    Raises
    ----------
    BeartypeDecorHintValuePepException
        If this object is PEP-compliant but this function erroneously fails to
        decide the :mod:`typing` attributes associated with this object due to
        this object being a user-defined class subclassing one or more
        :mod:`typing` superclasses that either:

        * Fails to define the PEP-specific ``__orig_bases__`` dunder attribute.
        * Defines that attribute but that attribute contains either:

          * No :mod:`typing` superclasses.
          * :data:`_GET_HINT_TYPING_ATTRS_OR_NONE_SUPERCLASSES_MAX` or more
            :mod:`typing` superclasses. This getter function internally reuses
            fixed lists of this size to efficiently iterate these superclasses.

    Examples
    ----------

        >>> import typing
        >>> from beartype._util.hint.utilhintpep import get_hint_typing_attrs_or_none
        >>> get_hint_typing_attrs_or_none(typing.Any)
        typing.Any
        >>> get_hint_typing_attrs_or_none(typing.Union[str, typing.Sequence[int]])
        typing.Union
        >>> get_hint_typing_attrs_or_none(typing.Sequence[int])
        typing.Sequence
        >>> T = typing.TypeVar('T')
        >>> get_hint_typing_attrs_or_none(T)
        typing.TypeVar
        >>> class Genericity(typing.Generic[T]): pass
        >>> get_hint_typing_attrs_or_none(Genericity)
        typing.Generic
        >>> class Duplicity(typing.Iterable[T], typing.Container[T]): pass
        >>> get_hint_typing_attrs_or_none(Duplicity)
        (typing.Iterable, typing.Container)

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''
    assert isinstance(hint_label, str), (
        '{!r} not a string.'.format(hint_label))

    # If this hint is *NOT* PEP-compliant, return "None".
    if not is_hint_pep(hint):
        return None
    # Else, this hint is PEP-compliant.

    # If this hint is a type variable, return the type of all such variables.
    # Note that:
    #
    # * This condition is tested for first due to the efficiency of this test
    #   rather than due to an expectation of type variables being more common
    #   than other PEP 484 objects and types.
    # * Unlike most PEP 484 objects and types, the TypeVar.__repr__() dunder
    #   method insanely returns a string prefixed by "~" rather than "typing.".
    #   Notably:
    #      >>> from typing import TypeVar
    #      >>> repr(TypeVar('T'))
    #      ~T
    #   Of course, that brazenly violates Pythonic standards. __repr__() is
    #   generally assumed to return an evaluatable Python expression that,
    #   when evaluated, creates an object equal to the original object.
    #   Instead, this API was designed by incorrigible monkeys who profoundly
    #   hate the Python language. This is why we can't have sane things.
    if isinstance(hint, TypeVar):
        return TypeVar
    # Else, this hint is *NOT* a type variable.

    # Direct typing attribute associated with this hint if this hint is
    # directly defined by the "typing" module *OR* "None" otherwise.
    hint_direct_typing_attr = get_hint_direct_typing_attr_or_none(hint)

    # If this attribute exists, return this attribute.
    if hint_direct_typing_attr:
        return hint_direct_typing_attr
    # Else, no such attribute exists. In this case, this hint is *NOT* directly
    # declared by the "typing" module. Since this hint is PEP-compliant, this
    # hint *MUST* necessarily be a user-defined class subclassing one or more
    # "typing" superclasses: e.g.,
    #
    #    # In a user-defined module...
    #    from typing import TypeVar, Generic
    #    T = TypeVar('T')
    #    class UserDefinedGeneric(Generic[T]): pass

    # Either the passed object if this object is a class *OR* the class of this
    # object otherwise (i.e., if this object is *NOT* a class).
    hint_type = get_object_type(hint)

    # Original superclasses of this class before the "typing" module
    # destructively erased these superclasses if this class declares the
    # "typing"-specific "__orig_bases__" dunder attribute preserving these
    # original superclasses *OR* the sentinel placeholder otherwise.
    #
    # You are probably now agitatedly cogitating to yourself in the darkness:
    # "But @leycec: what do you mean 'destructively erased'? Surely no public
    # API defined by the Python stdlib would be so malicious as to silently
    # modify the tuple of base classes listed by a user-defined subclass?"
    #
    # Let me tell you what now. As we've established both above and elsewhere
    # throughout this codebase, PEP 484 and friends are fundamentally insane.
    # In this case, PEP 484 is insane by subjecting parametrized "typing" types
    # employed as base classes to "type erasure," because "it is common
    # practice in languages with generics (e.g. Java, TypeScript)." Since Java
    # and TypeScript are both terrible languages, blindly recapitulating bad
    # mistakes baked into those languages is an equally bad mistake. In this
    # case, "type erasure" means that the "typing" module intentionally
    # destroys runtime type information for nebulous and largely unjustifiable
    # reasons (i.e., Big Daddy Java and TypeScript do it, so it must be
    # unquestionably good).
    #
    # Specifically, the "typing" module intentionally munges all "typing" types
    # used as base classes in user-defined subclasses as follows:
    #
    # * All base classes whose origin is a builtin container (e.g.,
    #   "typing.List[T]") are reduced to that container (e.g., "list").
    # * All base classes derived from an abstract base class declared by the
    #   "collections.abc" subpackage (e.g., "typing.Iterable[T]") are reduced
    #   to that abstract base class (e.g., "collections.abc.Iterable").
    # * All surviving base classes that are parametrized (e.g.,
    #   "typing.Generic[S, T]") are stripped of that parametrization (e.g.,
    #   "typing.Generic").
    #
    # Since there exists no counterpart to the "typing.Generic" superclass,
    # the "typing" module preserves that superclass in unparametrized form.
    # All other superclasses are reduced to non-"typing" counterparts.
    #
    # The standard "__mro__" dunder attribute of user-defined subclasses with
    # one or more "typing" superclasses reflects this erasure, while thankfully
    # preserving the original tuple of user-defined superclasses for those
    # subclasses in a "typing"-specific "__orig_bases__" dunder attribute:
    # e.g.,
    #
    #     # This is type erasure.
    #     >>> UserDefinedGeneric.__mro__
    #     (list, collections.abc.Iterable, Generic)
    #     # This is type preservation.
    #     >>> UserDefinedGeneric.__orig_bases__
    #     (List[T], Iterable[T], Generic[T])
    #     # Guess which we prefer?
    #
    # Ergo, we ignore the useless standard "__mro__" tuple in favour of the
    # actually useful (albeit non-standard) "__orig_bases__" tuple.
    #
    # Welcome to "typing" hell, where even "typing" types lie broken and
    # misshapen on the killing floor of overzealous theorists.

    #FIXME: Sadly, this is optimistically naive. O.K., it's just broken. The
    #"__orig_bases__" dunder attribute doesn't actually compute the original
    #MRO; it just preserves the original bases as directly listed in this
    #subclass declaration. What we need, however, is the actual original MRO as
    #that subclass *WOULD* have had had "typing" not subjected it to malignant
    #type erasure. That's... non-trivial but feasible to compute, so let's do
    #that. Specifically, let's:
    #
    #* Define a new "beartype._util.pep.utilpep560" submodule:
    #  * Define a new get_superclasses_original() function with signature:
    #    @callablecached
    #    def get_superclasses_original(obj: object) -> frozenset
    #    This function intentionally does *NOT* bother returning a proper MRO.
    #    While we certainly could do so (e.g., by recursively replacing in the
    #    "__mro__" of this object all bases modified via type erasure with
    #    those listed in the "__orig_bases__" attribute of each superclass),
    #    doing so would both be highly non-trivial and overkill. All we really
    #    require is the set of all original superclasses of this class. Since
    #    PEP 560 is (of course) awful, it provides no API for obtaining any of
    #    this. Fortunately, this shouldn't be *TERRIBLY* hard. We just need to
    #    implement (wait for it) a breadth-first traversal using fixed lists.
    #    This might resemble:
    #    * If the type of the passed object does *NOT* have the
    #      "__orig_bases__" attribute defined, just:
    #      return frozenset(obj.__mro__)
    #    * Else:
    #      * Acquire a fixed list of sufficient size (e.g., 64). We probably
    #        want to make this a constant in "utilcachelistfixedpool" for reuse
    #        everywhere, as this is clearly becoming a common idiom.
    #      * Slice-assign "__orig_bases__" into this list.
    #      * Maintain two simple 0-based indices into this list:
    #        * "bases_index_curr", the current base being visited.
    #        * "bases_index_last", the end of this list also serving as the
    #          list position to insert newly discovered bases at.
    #      * Iterate over this list and keep slice-assigning from either
    #        "__orig_bases__" (if defined) or "__mro__" (otherwise) into
    #        "list[bases_index_last:len(__orig_bases__)]". Note that this has
    #        the unfortunate disadvantage of temporarily iterating over
    #        duplicates, but... *WHO CARES.* It still works and we subsequently
    #        eliminate duplicates at the end.
    #      * Return a frozenset of this list, thus implicitly eliminating
    #        duplicate superclasses.
    hint_supertypes = getattr(hint_type, '__orig_bases__', SENTINEL)

    # If this user-defined subclass subclassing one or more "typing"
    # superclasses failed to preserve the original tuple of these superclasses
    # against type erasure, something has gone wrong. Raise us an exception!
    if hint_supertypes is SENTINEL:
        raise BeartypeDecorHintValuePepException(
            '{} PEP type {!r} subclasses no "typing" types.'.format(
                hint_label, hint))
    # Else, this subclass preserved this tuple against type erasure.

    # If this user-defined subclass subclassing more than the maximum number of
    # "typing" superclasses supported by this function, raise an exception.
    # This function internally reuses fixed lists of this size to efficiently
    # iterate these superclasses.
    if len(hint_supertypes) > _GET_HINT_TYPING_ATTRS_OR_NONE_SUPERCLASSES_MAX:
        raise BeartypeDecorHintValuePepException(
            '{} PEP type {!r} subclasses more than {} "typing" types.'.format(
                hint_label,
                hint,
                _GET_HINT_TYPING_ATTRS_OR_NONE_SUPERCLASSES_MAX))
    # Else, this user-defined subclass subclassing less than or equal to this
    # maximum number of "typing" superclasses supported by this function.

    # Fixed list of all typing attributes associated with this subclass.
    hint_typing_attrs = acquire_fixed_list(
        size=_GET_HINT_TYPING_ATTRS_OR_NONE_SUPERCLASSES_MAX)

    # 0-based index of the current item of this list to insert the next typing
    # attribute discovered by iteration below at.
    hint_typing_attrs_index = 0

    # For each original superclass of this class...
    for hint_supertype in hint_supertypes:
        # Direct typing attribute associated with this superclass if any *OR*
        # "None" otherwise.
        hint_typing_attr = get_hint_direct_typing_attr_or_none(hint_supertype)
        # print('hint supertype: {!r} -> {!r}'.format(hint_supertype, hint_direct_typing_attr))

        # If this attribute exists...
        if hint_typing_attr:
            # Insert this attribute at the current item of this list.
            hint_typing_attrs[hint_typing_attrs_index] = hint_typing_attr

            # Increment this index to the next item of this list.
            hint_typing_attrs_index += 1
        # Else, no such attribute exists.

    # Tuple sliced from the prefix of this list assigned to above.
    hint_typing_attrs_tuple = tuple(
        hint_typing_attrs[:hint_typing_attrs_index])

    # Release and nullify this list *AFTER* defining this tuple.
    release_fixed_list(hint_typing_attrs)
    del hint_typing_attrs

    # If this tuple is empty, raise an exception. By the above constraints,
    # this tuple should contain one or more typing attributes.
    if hint_typing_attrs_index == 0:
        raise BeartypeDecorHintValuePepException(
            '{} PEP type {!r} unassociated with "typing" types.'.format(
                hint_label, hint))
    # Else, this tuple is non-empty.

    # If this tuple contains one typing attribute, return only that attribute
    # *NOT* contained within a tuple to minimize memoized space costs.
    if hint_typing_attrs_index == 1:
        return hint_typing_attr

    # Else, this tuple contains ore or more typing attributes. In this case,
    # return this tuple as is.
    return hint_typing_attrs_tuple


def get_hint_direct_typing_attr_or_none(hint: object) -> 'NoneTypeOr[object]':
    '''
    **Direct typing attribute** (i.e., public attribute of the :mod:`typing`
    module directly identifying the passed `PEP 484`_-compliant class or object
    defined via the :mod:`typing` module *without* regard to any superclasses
    of this class or this object's class) associated with this class or object
    if any *or* ``None`` otherwise.

    This getter function is *only* intended to be called by the parent
    :func:`_get_hint_typing_attr_or_none` function.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    NoneTypeOr[object]
        Either:

        * If this object is directly identified by a public attribute of the
          :mod:`typing` module, that attribute.
        * Else, ``None``.
    '''

    # Machine-readable string representation of this hint also serving as the
    # fully-qualified name of the public "typing" attribute uniquely associated
    # with this hint (e.g., "typing.Tuple[str, ...]").
    #
    # Although the "typing" module provides *NO* sane public API, it does
    # reliably implement the __repr__() dunder method across most objects and
    # types to return a string prefixed "typing." regardless of Python version.
    # Ergo, this string is effectively the *ONLY* sane means of deciding which
    # broad category of behaviour an arbitrary PEP 484 type hint conforms to.
    typing_attr_name = repr(hint)

    # If this representation is prefixed by "typing.", this is a class or
    # object declared by the "typing" module. In this case...
    if typing_attr_name.startswith('typing.'):
        # Strip the now-harmful "typing." prefix from this representation.
        # Preserving this prefix would raise an "AttributeError" exception from
        # the subsequent call to the getattr() builtin.
        typing_attr_name = typing_attr_name[7:]  # hardcode us up the bomb

        # 0-based index of the first "[" delimiter in this representation if
        # any *OR* -1 otherwise.
        typing_attr_name_bracket_index = typing_attr_name.find('[')

        # If this representation contains such a delimiter, this is a
        # parametrized type hint. In this case, reduce this representation to
        # its unparametrized form by truncating the suffixing parametrization
        # from this representation (e.g., from
        # "typing.Union[str, typing.Sequence[int]]" to merely "typing.Union").
        #
        # Note that this is the common case and thus explicitly tested first.
        if typing_attr_name_bracket_index > 0:
            typing_attr_name = typing_attr_name[
                :typing_attr_name_bracket_index]
        # Else, this representation contains no such a delimiter and is thus
        # already unparametrized as desired. In this case, preserve this
        # representation as is.

        # Return the "typing" attribute with this name if any *OR* implicitly
        # raise an "AttributeError" exception. Since this is an unlikely edge
        # case, we avoid performing any deeper validation here.
        return getattr(typing, typing_attr_name)
    # Else, this hint is *NOT* a class or object declared by the "typing"
    # module.

    # Ergo, this hint is unassociated with a public "typing" attribute.
    return None
