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
from beartype._util.utilobj import (
    get_object_module_name_or_none, get_object_type)
from typing import Any, TypeVar

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS ~ supported             }....................
_TYPING_OBJECTS_SUPPORTED = frozenset((
    Any,
))
'''
Frozen set of all :mod:`typing` objects (typically, singletons) supported by
the :func:`beartype.beartype` decorator.
'''


_TYPING_OBJECT_TYPES_SUPPORTED = (
    #FIXME: Uncomment after supporting type variables.
    # TypeVar,
)
'''
Tuple of all :mod:`typing` types whose instances are supported by the
:func:`beartype.beartype` decorator.

This container is intentionally declared as a tuple rather than frozen set to
enable testing by the :func:`isinstance` builtin.
'''


_TYPING_NAMES_SUPPORTED = frozenset((
    'typing.Union',
))
'''
Frozen set of the fully-qualified names of all :mod:`typing` types supported by
the :func:`beartype.beartype` decorator.
'''

# ....................{ EXCEPTIONS                        }....................
def die_if_hint_pep(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Typing hint',
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
        exception message raised by this function. Defaults to ``Typing hint``.
    exception_cls : Optional[type]
        Type of the exception to be raised by this function. Defaults to
        :class:`BeartypeDecorHintValuePepException`.

    Raises
    ----------
    exception_cls
        If this object is a `PEP 484`_ type hint.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''
    assert isinstance(hint_label, str), (
        '{!r} not a string.'.format(hint_label))
    assert isinstance(exception_cls, type), (
        '{!r} not a type.'.format(exception_cls))

    # If this hint is a PEP 484 type or object declared by the "typing" module,
    # raise an exception of this class.
    if is_hint_pep(hint):
        raise exception_cls(
            '{} PEP 484 type {!r} unsupported.'.format(hint_label, hint))


@callable_cached
def die_unless_hint_pep(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Typing hint',
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
        exception message raised by this function. Defaults to ``Typing hint``.

    Raises
    ----------
    BeartypeDecorHintValuePepException
        If this object is either not a `PEP 484`_ type *or* is but is currently
        unsupported by :func:`beartype.beartype`.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''
    assert isinstance(hint_label, str), (
        '{!r} not a string.'.format(hint_label))

    # If this hint is *NOT* a PEP 484 type or object declared by the "typing"
    # module, raise an exception.
    if not is_hint_pep(hint):
        raise BeartypeDecorHintValuePepException(
            '{} {!r} not PEP 484-compliant.'.format(hint_label, hint))
    # Else, this hint is a PEP 484 type or object declared by that module.
    #
    # Ergo, this hint is safely hashable and thus testable as is against
    # containers requiring item hashability (e.g., dict keys, set items). By
    # definition, *ALL* PEP 484 types and objects are hashable.

    # If this hint is either...
    if (
        # A supported "typing" singleton *OR*...
        hint in _TYPING_OBJECTS_SUPPORTED or
        # An instance of a supported "typing" type *OR*...
        isinstance(hint, _TYPING_OBJECT_TYPES_SUPPORTED)
    # Then this hint is a supported PEP 484 object. In this case, silently
    # reduce to a noop.
    ):
        return
    # Else, this hint is *NOT* a supported PEP 484 object.

    # Template for unsupported exception messages raised by this function.
    EXCEPTION_MESSAGE_TEMPLATE = '{} currently unsupported by @beartype.'

    # Exception message to be raised below.
    exception_message = ''

    # If this hint is a PEP-484 type variable, note this.
    if is_hint_typing_typevar(hint):
        exception_message = EXCEPTION_MESSAGE_TEMPLATE.format(
            '{} PEP 484 type variable {!r}'.format(hint_label, hint))
    # Else if this hint is a PEP-484 type parametrized by one or more type
    # variables, note this.
    elif is_hint_typing_typevared(hint):
        exception_message = EXCEPTION_MESSAGE_TEMPLATE.format(
            '{} PEP 484 type variable-parametrized generic {!r}'.format(
                hint_label, hint))
    # Else, genericize this message.
    else:
        exception_message = EXCEPTION_MESSAGE_TEMPLATE.format(
            '{} PEP 484 type {!r}'.format(hint_label, hint))

    # Raise this message.
    raise BeartypeDecorHintValuePepException(exception_message)

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

    # Either the passed object if this object is a class *OR* the class of this
    # object otherwise (i.e., if this object is *NOT* a class).
    hint_type = get_object_type(hint)

    # If this type is defined by the stdlib "typing" module, return true.
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

    # For each superclass of this class...
    #
    # This edge case is required to handle user-defined subclasses declared in
    # user-defined modules of superclasses declared by the "typing" module:
    #
    #    # In a user-defined module...
    #    from typing import TypeVar, Generic
    #    T = TypeVar('T')
    #    class UserDefinedGeneric(Generic[T]): pass
    for hint_type_supertype in hint_type.__mro__:
        # If this superclass is defined by "typing", return true.
        if get_object_module_name_or_none(hint_type_supertype) == 'typing':
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

# ....................{ GETTERS ~ private                 }....................
#FIXME: Add support for user-defined types (e.g., "GenericUserDefined"). To do
#so, we'll probably need to refactor this as follows:
#
#* If the call to _get_hint_direct_typing_attr_or_none() returns "None",
#  iteratively walks up "hint.__mro__" as in the is_hint_pep() tester and, for
#  each superclass of this hint, call _get_hint_direct_typing_attr_or_none()
#  again with that superclass until either:
#  * Such a call returns a non-"None" value, which should then be immediately
#    returned from this function.
#  * All such calls return "None", which should then be immediately returned
#    from this function.
#
#Trivial, presumably. Presumably...
@callable_cached
def _get_hint_typing_attr_or_none(hint: object) -> 'NoneTypeOr[object]':
    '''
    **Typing attribute** (i.e., public attribute of the :mod:`typing` module
    uniquely identifying the passed `PEP 484`_-compliant class or object
    defined via the :mod:`typing` module) associated with this class or object
    if any *or* ``None`` otherwise.

    This getter function associates arbitrary `PEP 484`_-compliant classes and
    objects with corresponding public attributes of the :mod:`typing` module,
    which effectively serve as unique pseudo-superclasses of those classes and
    objects. Although these attributes are typically *not* actually
    superclasses (as most :mod:`typing` superclasses are private, fragile, and
    prone to extreme alteration or even removal between major Python versions),
    these attributes are sufficiently unique to enable callers to distinguish
    between numerous broad categories of :mod:`typing` behaviour and logic.

    This getter function is memoized for efficiency.

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

    Returns
    ----------
    NoneTypeOr[object]
        Either:

        * If this object is uniquely identified by a public attribute of the
          :mod:`typing` module, that attribute.
        * Else, ``None``.

    Examples
    ----------

        >>> import typing
        >>> from beartype._util.hint.utilhintpep import _get_hint_typing_attr_or_none
        >>> _get_hint_typing_attr_or_none(typing.Any)
        typing.Any
        >>> _get_hint_typing_attr_or_none(typing.Union[str, typing.Sequence[int]])
        typing.Union
        >>> _get_hint_typing_attr_or_none(typing.Sequence[int])
        typing.Sequence
        >>> T = typing.TypeVar('T')
        >>> _get_hint_typing_attr_or_none(T)
        typing.TypeVar
        >>> class Genericity(typing.Generic[T]): pass
        >>> _get_hint_typing_attr_or_none(Genericity)
        typing.Generic

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # If this hint is a type variable, return the type of all such variables.
    #
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

    # Return the direct typing attribute associated with this class or object
    # if any *OR* "None" otherwise.
    return _get_hint_direct_typing_attr_or_none(hint)


def _get_hint_direct_typing_attr_or_none(hint: object) -> 'NoneTypeOr[object]':
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
