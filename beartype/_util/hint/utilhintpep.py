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
from abc import abstractmethod, abstractproperty
from beartype.roar import BeartypeDecorHintValuePepException
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.utilobj import (
    get_object_module_name_or_none, get_object_type)
from types import (
    FunctionType,
    ModuleType,
)
from typing import TypeVar

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
_TYPING_ATTRS_IGNORABLE = frozenset((
    abstractmethod,
    abstractproperty,
))
'''
Frozen set of all **ignorable** :mod:`typing` **attributes** (i.e., incidental
objects erroneously imported into the :mod:`typing` namespace as public
attributes thus technically comprising part of the public :mod:`typing` API).

Thanks again for the non-sane API, guys. *Yikes.*
'''


_TYPING_ATTR_TYPES_IGNORABLE = frozenset((
    bool,
    FunctionType,
    ModuleType,
))
'''
Frozen set of all **ignorable** :mod:`typing` **attribute types** (i.e., types
of incidental objects erroneously imported into the :mod:`typing` namespace as
public attributes thus technically comprising part of the public :mod:`typing`
API).

Thanks again for the non-sane API, guys. *Yikes.*
'''


_TYPING_HINT_TO_NAME = {
    # Key-value pair mapping this public "typing" type to the unqualified name
    # of this type.
    typing_attr: typing_attr_name
    # For the unqualified name and value of all "typing" attributes...
    for typing_attr_name, typing_attr in typing.__dict__.items()
    # If...
    if (
        # This name is public *AND*....
        typing_attr_name[0] != '_' and
        # This value is *NOT* an incidental object erroneously imported into
        # the "typing" namespace as a public attribute.
        typing_attr not in _TYPING_ATTRS_IGNORABLE and
        # This value's type implies this value is *NOT* an incidental object.
        type(typing_attr) not in _TYPING_ATTR_TYPES_IGNORABLE
    )
}
'''
Dictionary mapping all public non-ignorable :mod:`typing` attributes to their
unqualified names.
'''


_TYPING_NAMES_SUPPORTED = frozenset((
    'Any',
    'Union',
))
'''
Frozen set of the unqualified names of all public :mod:`typing` types
explicitly supported by the :func:`beartype.beartype` decorator.
'''

# ....................{ EXCEPTIONS                        }....................
def die_unless_hint_pep(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Typing hint',
) -> None:
    '''
    Raise an exception unless the passed object is a **PEP-compliant type
    hint** (i.e., :mod:`beartype`-agnostic annotation compliant with
    annotation-centric PEPs) currently supported by the
    :func:`beartype.beartype` decorator.

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
        unsupported.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''
    assert isinstance(hint_label, str), (
        '{!r} not a string.'.format(hint_label))

    # If this hint is a PEP-compliant type hint, silently reduce to a noop.
    if is_hint_pep(hint):
        return
    # Else, this object is *NOT* a PEP-compliant type hint. In this case,
    # perform further tests to inform the user of the exact issue herein.

    # If this hint is *NOT* a PEP 484-compliant type or object declared by
    # the stdlib "typing" module, raise an exception.
    if not _is_hint_typing(hint):
        raise BeartypeDecorHintValuePepException(
            '{} {!r} not PEP 484-compliant.'.format(hint_label, hint))
    # Else, this object is a PEP 484-compliant type or object.

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
    elif is_hint_typing_args_typevar(hint):
        exception_message = EXCEPTION_MESSAGE_TEMPLATE.format(
            '{} PEP 484 type variable-parametrized generic {!r}'.format(
                hint_label, hint))
    # Else, genericize this message.
    else:
        exception_message = EXCEPTION_MESSAGE_TEMPLATE.format(
            '{} PEP 484 type {!r}'.format(hint_label, hint))

    # Raise this message.
    raise BeartypeDecorHintValuePepException(exception_message)

# ....................{ TESTERS                           }....................
#FIXME: Unit test us up.
@callable_cached
def is_hint_pep(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a **PEP-compliant type hint** (i.e.,
    :mod:`beartype`-agnostic annotation compliant with annotation-centric PEPs)
    currently supported by the :func:`beartype.beartype` decorator.

    For efficiency, this tester is memoized.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a PEP-compliant type hint.
    '''

    # If this hint is *NOT* a PEP 484-compliant type or object declared by the
    # stdlib "typing" module, return false.
    if not _is_hint_typing(hint):
        return False
    # Else, this hint is PEP 484-compliant.

    #FIXME: Implement us up. To do so, we'll probably want to implement similar
    #iteration as already implemented by _is_hint_typing() -- which suggests we
    #probably want to avoid calling _is_hint_typing() above. Instead, we
    #probably want to define a new _is_hint_typing_supported() function
    #implemented similarly to _is_hint_typing() but additionally testing that
    #the fully-qualified classname of the "typing" type subclassed by the
    #passed hint is in a private set global defined above resembling: e.g.,
    #
    #    _TYPING_SUPPORTED_CLSNAMES = {
    #        'typing.Any',
    #        'typing.Union',
    #        ...
    #    }

    # If this hint is unsupported by the @beartype decorator, return false.
    # is_hint_typing_supported(hint)

    # Return true only if this object is...
    return (
        # Supported by the @beartype decorator *AND*...
        # is_hint_typing_supported(hint) and
        # *NOT*...
        not (
            # A PEP-484 type variable *NOR*...
            is_hint_typing_typevar(hint) or
            # A PEP-484 type parametrized by one or more type variables.
            is_hint_typing_args_typevar(hint)
        )
    )

# ....................{ TESTERS ~ typevar                 }....................
#FIXME: Consider excising. Unsure if we actually require this. *sigh*
@callable_cached
def is_hint_typing_typevarish(hint: object) -> bool:
    '''
    ``True`` only if the passed object is either a `PEP 484`_ **type variable**
    (i.e., instance of the :mod:`typing.TypeVar` class) *or* a `PEP 484`_ type
    parametrized by one or more type variables (e.g.,
    ``typing.List[typing.TypeVar['T']]``).

    For efficiency, this tester is memoized.

    Motivation
    ----------
    Since type variables are not themselves types but rather placeholders
    dynamically replaced with types by type checkers according to various
    arcane heuristics, both type variables and types parametrized by type
    variables warrant special-purpose handling.

    Parameters
    ----------
    hint : object
        Object type to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is either a type variable or `PEP 484`_
        type parametrized by one or more type variables.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Return true only if this type either...
    return (
        # Is a type variable *OR*...
        is_hint_typing_typevar(hint) or
        # This is a "typing" type parametrized by one or more type variables.
        is_hint_typing_args_typevar(hint)
    )


# This tester is intentionally *NOT* memoized with @callable_cached, as the
# implementation trivially reduces to an efficient one-liner.
def is_hint_typing_typevar(hint: object) -> bool:
    '''
    ``True`` only if the passed object either is a `PEP 484`_ **type variable**
    (i.e., instance of the :mod:`typing.TypeVar` class).

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
def is_hint_typing_args_typevar(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a `PEP 484`_ type parametrized by one
    or more type variables (e.g., ``typing.List[typing.TypeVar['T']]``).

    For efficiency, this tester is memoized.

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
    #return _is_hint_typing(hint) and bool(getattr(hint, '__parameters__', ()))

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

# ....................{ TESTERS ~ private                 }....................
# #FIXME: Uncomment once _get_hint_typing_name_or_none() behaves sanely.
# def _is_hint_typing(hint: object) -> bool:
#     '''
#     ``True`` only if the passed object is a **typing type hint** (i.e.,
#     `PEP 484`_-compliant class or object declared by the :mod:`typing` module).
#
#     Parameters
#     ----------
#     hint : object
#         Object to be inspected.
#
#     Returns
#     ----------
#     bool
#         ``True`` only if this object is a typing type hint.
#
#     See Also
#     ----------
#     :func:`_get_hint_typing_name_or_none`
#         Further details.
#
#     .. _PEP 484:
#        https://www.python.org/dev/peps/pep-0484
#     '''
#
#     # Unqualified name of the root typing type of this object if any *OR*
#     # "None" otherwise.
#     #
#     # Note that this tester trivially reduces to the memoized
#     # _get_hint_typing_name_or_none() and is thus *NOT* worth memoization.
#     return _get_hint_typing_name_or_none(hint) is not None

#FIXME: Detect functions created by "typing.NewType(subclass_name, superclass)"
#somehow, either here or elsewhere. These functions are simply the identity
#function at runtime and thus a complete farce. They're not actually types!
#Ideally, we would replace each such function by the underlying "superclass"
#type originally passed to that function, but we have no idea if that's even
#feasible. Welcome to "typing", friends.
@callable_cached
def _is_hint_typing(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a **typing type hint** (i.e.,
    `PEP 484`_-compliant class or object declared by the :mod:`typing` module).

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a typing type hint.

    See Also
    ----------
    :func:`_get_hint_typing_name_or_none`
        Further details.

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

# ....................{ GETTERS ~ private                 }....................
#FIXME: Unit test us up.
#FIXME: Actually, consider removal. Implementing this turns out to be highly
#non-trivial. We *DO* need some means of detecting supported "typing" types,
#however. Doing so for unparametrized types like "typing.Any" is trivial, of
#course. Doing so parametrized types like "typing.List[str]" is less so,
#however, as "typing.List[str] is not typing.List". Surely one can retrieve
#the unparametrized parent type (e.g., "typing.List") given a parametrized
#child type (e.g., "typing.List[str]"). Research us up, please.
#FIXME: If removed, remove all corresponding global constants required to
#implement this function above.
@callable_cached
def _get_hint_typing_name_or_none(hint: object) -> 'NoneTypeOr[ClassType]':
    '''
    **Unqualified name** (i.e., basename excluding the prefixing
    fully-qualified name of the parent module) of the **public root typing
    type** (i.e., first public superclass in the method resolution order (MRO)
    of the passed object declared by the :mod:`typing` module) of this object
    if this object has a public root typing type and is thus a `PEP
    484`_-compliant type hint *or* ``None`` otherwise (i.e., if this object has
    *no* public root typing type and is thus *not* a `PEP 484`_-compliant type
    hint).

    For efficiency, this getter is memoized.

    Motivation
    ----------
    Standard types allow callers to test for compliance with protocols,
    interfaces, and abstract base classes by calling either the
    :func:`isinstance` or :func:`issubclass` builtins. This is the
    well-established Pythonic standard for deciding conformance to an API.

    Insanely, `PEP 484`_ *and* the :mod:`typing` module implementing `PEP 484`_
    reject community standards by explicitly preventing callers from calling
    either the :func:`isinstance` or :func:`issubclass` builtins on `PEP
    484`_ types. Moreover, neither `PEP 484`_ nor :mod:`typing` implement
    public APIs for testing whether arbitrary objects comply with `PEP 484`_ or
    :mod:`typing`.

    Thus this getter function, which "fills in the gaps" by implementing this
    laughably critical oversight.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    NoneTypeOr[ClassType]
        Either:

        * If this object has a public root typing type, unqualified name of
          this type.
        * Else, ``None``.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Unqualified name of this object if this object is a public "typing" type
    # hint *OR* "None" otherwise.
    typing_hint_name_or_none = _TYPING_HINT_TO_NAME.get(hint, None)
    print('_TYPING_TYPE_TO_NAME: {}'.format(_TYPING_HINT_TO_NAME))

    # If this object is a public "typing" type hint, return this name.
    if typing_hint_name_or_none is not None:
        return typing_hint_name_or_none
    # Else, this object is *NOT* a public "typing" type hint.

    # Either the passed object if this object is a class *OR* the class of this
    # object otherwise (i.e., if this object is *NOT* a class).
    hint_type = get_object_type(hint)

    # If...
    #
    # Note that there might exist an alternate means of deciding this
    # condition, documented here merely for completeness:
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
    if (
        # This type is directly defined by the "typing" module *AND*...
        get_object_module_name_or_none(hint_type) == 'typing' and
        # This type is public.
        hint_type.__name__[0] != '_'
    ):
        # Return the unqualified name of this type.
        return hint_type.__name__

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
        # If...
        if (
            # This superclass is directly defined by the "typing" module
            # *AND*...
            get_object_module_name_or_none(hint_supertype) == 'typing' and
            # This superclass is public.
            hint_supertype.__name__[0] != '_'
        ):
            # Return the unqualified name of this superclass.
            return hint_supertype.__name__

    # Else, neither this type nor any superclass of this type is defined by the
    # "typing" module. Ergo, this is *NOT* a PEP 484-compliant type hint.
    return None
