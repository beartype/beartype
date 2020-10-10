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
    BeartypeDecorHintPepException,
    BeartypeDecorHintPepUnsupportedException,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.pep.utilhintpepdata import TYPING_ATTRS_SUPPORTED
from beartype._util.utilobject import (
    get_object_module_name_or_none,
    get_object_type,
)
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_7
from typing import Generic, TypeVar

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
_EXCEPTION_MESSAGE_UNSUPPORTED_SUFFIX = 'currently unsupported by @beartype.'
'''
Substring suffixing exception messages raised by functions validating objects
to be supported by the :func:`beartype.beartype` decorator.
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

# ....................{ EXCEPTIONS                        }....................
def die_unless_hint_pep_supported(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Annotated',
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
    **This function should never be called to validate argumentless**
    :mod:`typing` **attributes** (e.g., those returned by the
    :func:`beartype._util.hint.pep.get_hint_pep_typing_attr` function). The
    :func:`die_unless_hint_pep_typing_attr_supported` function should be called
    instead. Why? Because the :mod:`typing` module implicitly parametrizes
    these attributes by one or more type variables. Since this decorator
    currently fails to support type variables, this function unconditionally
    raises an exception when passed these attributes.

    **This validator only shallowly validates this object.** If this object is
    a subscripted PEP-compliant type hint (e.g., ``Union[str, List[int]]``),
    this validator ignores all subscripted arguments (e.g., ``List[int]``) on
    this hint and may thus return false positives for hints that are directly
    supported but whose subscripted arguments are not. To deeply validate this
    object, iteratively call this validator during a recursive traversal (such
    as a breadth-first search) over each subscripted argument of this object.

    Parameters
    ----------
    hint : object
        Object to be validated.
    hint_label : Optional[str]
        Human-readable label prefixing this object's representation in the
        exception message raised by this function. Defaults to ``"Annotated"``.

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
    assert hint_label.__class__ is str, '{!r} not string.'.format(hint_label)

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with is_hint_pep_supported() below.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # If this hint is *NOT* PEP-compliant, raise an exception.
    die_unless_hint_pep(hint=hint, hint_label=hint_label)
    # Else, this hint is PEP-compliant.

    #FIXME: Remove *AFTER* implementing support for type variables.
    # Else if this hint is a generic, raise an exception. Generics require
    # non-trivial decorator support that has yet to be implemented.
    if is_hint_pep_generic_user(hint):
        raise BeartypeDecorHintPepUnsupportedException(
            '{} generic PEP hint {!r} {}'.format(
                hint_label, hint, _EXCEPTION_MESSAGE_UNSUPPORTED_SUFFIX))
    #FIXME: Remove *AFTER* implementing support for type variables.
    # Else if this hint is typevared, raise an exception. Type variables
    # require non-trivial decorator support that has yet to be implemented.
    elif is_hint_pep_typevared(hint):
        raise BeartypeDecorHintPepUnsupportedException(
            '{} "TypeVar"-parametrized PEP hint {!r} {}'.format(
                hint_label, hint, _EXCEPTION_MESSAGE_UNSUPPORTED_SUFFIX))

    # Else, this hint is neither generic nor typevared. In this case, raise a
    # general-purpose exception.
    #
    # Note that, by definition, the argumentless "typing" argument uniquely
    # identifying this hint *SHOULD* be in the "TYPING_ATTRS_SUPPORTED" set.
    # Regardless of whether it is or isn't, we raise a similar exception. Ergo,
    # there's no benefit to validating this expectation here.
    raise BeartypeDecorHintPepUnsupportedException(
        '{} PEP hint {!r} {}'.format(
            hint_label, hint, _EXCEPTION_MESSAGE_UNSUPPORTED_SUFFIX))


def die_unless_hint_pep_typing_attr_supported(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Argumentless "typing" attribute',
) -> None:
    '''
    Raise an exception unless the passed object is a **PEP-compliant supported
    argumentless typing attribute** (i.e., public attribute of the
    :mod:`typing` module without arguments uniquely identifying a category of
    PEP-compliant type hints currently supported by the
    :func:`beartype.beartype` decorator).

    This validator is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

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

    # If this hint is *NOT* a supported argumentless "typing" attribute, raise
    # an exception.
    if not is_hint_pep_typing_attr_supported(hint):
        assert isinstance(hint_label, str), (
            '{!r} not string.'.format(hint_label))
        raise BeartypeDecorHintPepUnsupportedException(
            '{} {!r} {}'.format(
                hint_label, hint, _EXCEPTION_MESSAGE_UNSUPPORTED_SUFFIX))

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

    # Either the passed object if this object is a class *OR* the class of this
    # object otherwise (i.e., if this object is *NOT* a class).
    hint_type = get_object_type(hint)

    # Return true only if either...
    return (
        # This hint's type is directly defined by the "typing" module and thus
        # PEP-compliant by definition *OR*...
        is_hint_pep_typing(hint_type) or
        # This hint is a PEP-compliant generic. Although a small subset of
        # generics are directly defined by the "typing" module (e.g.,
        # "typing.IO"), most generics are user-defined subclasses defined by
        # user-defined modules residing elsewhere.
        is_hint_pep_generic_user(hint)
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
        # PEP-compliant but a generic...
        #
        # Generics require non-trivial decorator support.
        is_hint_pep_generic_user(hint) or

        #FIXME: Remove *AFTER* implementing support for type variables.
        # PEP-compliant but typevared...
        #
        # Type variables require non-trivial decorator support.
        is_hint_pep_typevared(hint)
    # Return false.
    ):
        return False
    # Else, this hint is PEP-compliant, *NOT* a generic, and *NOT* typevared.

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilhintpepget import (
        get_hint_pep_typing_attr)

    # Argumentless "typing" attribute uniquely identifying this hint.
    hint_typing_attr = get_hint_pep_typing_attr(hint)

    # Return true only if this attribute is supported.
    return is_hint_pep_typing_attr_supported(hint_typing_attr)

# ....................{ TESTERS ~ typing                  }....................
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
    # Note that this implementation could probably be reduced to the trailing
    # portion of the body of the get_hint_pep_typing_attr() function testing
    # this object's representation. While certainly more compact and convenient
    # than the current approach, that refactored approach would also be
    # considerably more fragile, failure-prone, and subject to whimsical
    # "improvements" in the already overly hostile "typing" API. Why? Because
    # the get_hint_pep_typing_attr() function:
    #
    # * Parses the machine-readable string returned by the __repr__() dunder
    #   method of "typing" types. Since that string is *NOT* standardized by
    #   PEP 484 or any other PEP, "typing" authors remain free to violate this
    #   pseudo-standard in any manner and at any time of their choosing.
    # * Suffers common edge cases for "typing" types whose __repr__() dunder
    #   methods fail to comply with the non-standard implemented by their
    #   sibling types. This includes the common "TypeVar" type.
    # * Calls this tester function to decide whether the passed object is a
    #   PEP-compliant type hint or not before subjecting that object to further
    #   introspection, which would clearly complicate implementing this tester
    #   function in terms of that getter function.
    #
    # In contrast, the current approach only tests the standardized "__name__"
    # and "__module__" dunder attributes and is thus significantly more robust
    # against whimsical destruction by "typing" authors.
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


def is_hint_pep_typing_attr_supported(hint) -> bool:
    '''
    ``True`` only if the passed object is a **PEP-compliant supported
    argumentless typing attribute** (i.e., public attribute of the
    :mod:`typing` module without arguments uniquely identifying a category of
    PEP-compliant type hints currently supported by the
    :func:`beartype.beartype` decorator).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be tested.

    Returns
    ----------
    bool
        ``True`` only if this object is a PEP-compliant supported argumentless
        typing attribute.

    Raises
    ----------
    TypeError
        If this object is **unhashable** (i.e., *not* hashable by the builtin
        :func:`hash` function and thus unusable in hash-based containers like
        dictionaries and sets). All supported type hints are hashable.
    '''

    # Return true only if this hint is a supported argumentless "typing"
    # attribute.
    return hint in TYPING_ATTRS_SUPPORTED

# ....................{ TESTERS ~ generic                 }....................
# If the active Python interpreter targets Python >= 3.7.0, define the
# is_hint_pep_generic_user() tester for Python >= 3.7.0. Sadly, Python
# 3.7.0 broke backward compatibility with the public API of the "typing" module
# by removing the prior "typing.GenericMeta" metaclass previously referenced by
# this tester under Python < 3.7.0, necessitating fundamentally different
# implementations for this tester between Python < 3.7.0 and >= 3.7.0.
if IS_PYTHON_AT_LEAST_3_7:
    def is_hint_pep_generic_user(hint: object) -> bool:

        # Return true only if this hint is a subclass of the "typing.Generic"
        # abstract base class (ABC) *not* defined by the "typing" module, in
        # which case this hint is a user-defined generic.
        #
        # Note that this test is robust against edge case, as the "typing"
        # module guarantees all user-defined classes subclassing one or more
        # "typing" pseudo-superclasses to subclass the "typing.Generic"
        # abstract base class (ABC) regardless of whether those classes
        # originally did so explicitly. How? By type erasure, of course, the
        # malicious gift that keeps on giving:
        #     >>> import typing as t
        #     >>> class MuhList(t.List): pass
        #     >>> MuhList.__orig_bases__
        #     (typing.List)
        #     >>> MuhList.__mro__
        #     (__main__.MuhList, list, typing.Generic, object)
        #
        # Note that this issubclass() call implicitly performs a surprisingly
        # inefficient search over the method resolution order (MRO) of all
        # superclasses of this hint. In theory, the cost of this search might
        # be circumventable by observing that this ABC is expected to reside at
        # the second-to-last index of the tuple exposing this MRO far all
        # generics by virtue of fragile implementation details violating
        # privacy encapsulation. In practice, this codebase is fragile enough.
        #
        # Note lastly that the following logic superficially appears to
        # implement the same test *WITHOUT* the onerous cost of a search:
        #     return len(get_hint_pep_generic_bases(hint)) > 0
        #
        # Why didn't we opt for that, then? Because this tester is routinely
        # passed objects that *CANNOT* be guaranteed to be PEP-compliant.
        # Indeed, the high-level is_hint_pep() tester establishing the
        # PEP-compliance of arbitrary objects internally calls this lower-level
        # tester to do so. Since the get_hint_pep_generic_bases() getter
        # internally reduces to returning the tuple of the general-purpose
        # "__orig_bases__" dunder attribute formalized by PEP 560, testing
        # whether that tuple is non-empty or not in no way guarantees this
        # object to be a PEP-compliant generic.
        return (
            isinstance(hint, type) and
            issubclass(hint, Generic) and
            not is_hint_pep_typing(hint)
        )
# Else if the active Python interpreter targets Python < 3.7.0, define the
# is_hint_pep_generic_user() tester for Python < 3.7.0.
else:
    # Import the Python < 3.7.0-specific metaclass required by this tester.
    from typing import GenericMeta

    def is_hint_pep_generic_user(hint: object) -> bool:

        # Return true only if this hint is a subclass *not* defined by the
        # "typing" module whose class is the "typing.GenericMeta" metaclass, in
        # which case this hint is a user-defined generic.
        #
        # Note the Python >= 3.7.0-specific implementation of this tester does
        # *NOT* apply to Python < 3.7.0, as this metaclass unconditionally
        # raises exceptions when user-defined "typing" subclasses internally
        # requiring this metaclass are passed to the issubclass() builtin.
        return isinstance(hint, GenericMeta) and not is_hint_pep_typing(hint)


# Docstring for this function regardless of implementation details.
is_hint_pep_generic_user.__doc__ = '''
    ``True`` only if the passed object is a **user-defined generic** (i.e.,
    PEP-compliant type hint subclassing one or more public :mod:`typing`
    pseudo-superclasses but *not* itself defined by the :mod:`typing` module).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Design
    ----------
    This tester intentionally avoids returning ``True`` for *all* generics
    (including both those internally defined by the :mod:`typing` module and
    those externally defined by third-party callers). Why? Because generics
    internally defined by the :mod:`typing` module are effectively *not*
    generics and only implemented as such under Python < 3.7.0 for presumably
    indefensible low-level reasons -- including:

    * *All* callable types (e.g., :attr:`typing.Awaitable`,
      :attr:`typing.Callable`, :attr:`typing.Coroutine`,
      :attr:`typing.Generator`).
    * *Most* container and iterable types (e.g., :attr:`typing.Dict`,
      :attr:`typing.List`, :attr:`typing.Mapping`, :attr:`typing.Tuple`).

    If this tester returned ``True`` for *all* generics, then downstream
    callers would effectively have no means of distinguishing genuine
    user-defined generics from disingenuous :mod:`typing` pseudo-generics.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a generic.

    See Also
    ----------
    :func:`is_hint_pep_typevared`
        Commentary on the relation between generics and typevared hints.

    Examples
    ----------
        >>> import typing
        >>> from beartype._util.hint.pep.utilhintpepget import (
        ...     is_hint_pep_generic_user)
        >>> T = typing.TypeVar('T')
        >>> class Genericized(typing.Generic[T]) pass
        >>> class Containment(typing.Iterable[T], typing.Container[T]): pass
        >>> is_hint_pep_generic_user(Genericized)
        True
        >>> is_hint_pep_generic_user(Containment)
        True
        >>> is_hint_pep_generic_user(typing.Generic[T])
        False
        >>> is_hint_pep_generic_user(typing.Iterable[T])
        False
    '''

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

    # Return true only if the type of this hint is that of all type variables.
    #
    # Note that the "typing.TypeVar" class prohibits subclassing: e.g.,
    #     >>> import typing as t
    #     >>> class MutTypeVar(t.TypeVar): pass
    #     TypeError: Cannot subclass special typing classes
    #
    # Ergo, the object identity test performed here both suffices and is more
    # efficient than the equivalent general-purpose test, which requires an
    # implicit breadth- or depth-first search over the method resolution order
    # (MRO) of all superclasses of this object: e.g.,
    #     # This is potentially *MUCH* slower. It's the little things in life.
    #     return isinstance(hint, TypeVar)
    return hint.__class__ is TypeVar


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

    Semantics
    ----------
    **Generics** (i.e., PEP-compliant type hints whose classes subclass one or
    more public :mod:`typing` pseudo-superclasses) are often but *not* always
    typevared. For example, consider the untypevared generic:

        >>> from typing import List
        >>> class UntypevaredGeneric(List[int]): pass
        >>> UntypevaredGeneric.__mro__
        (__main__.UntypevaredGeneric, list, typing.Generic, object)
        >>> UntypevaredGeneric.__parameters__
        ()

    Likewise, typevared hints are often but *not* always generic. For example,
    consider the typevared non-generic:

        >>> from typing import List, TypeVar
        >>> TypevaredNongeneric = List[TypeVar('T')]
        >>> type(TypevaredNongeneric).__mro__
        (typing._GenericAlias, typing._Final, object)
        >>> TypevaredNongeneric.__parameters__
        (~T,)

    Parameters
    ----------
    hint : object
        Object to be inspected.

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
    # alias (e.g., "typing._GenericAlias" subtype) *OR* the empty tuple
    # otherwise is non-empty.
    return len(get_hint_pep_typevars(hint)) > 0
