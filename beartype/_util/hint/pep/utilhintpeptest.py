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
from beartype._util.hint.pep.proposal.utilhintpep484 import (
    is_hint_pep484_generic,
    is_hint_pep484_generic_multiple,
)
from beartype._util.hint.data.pep.utilhintdatapep import HINT_PEP_SIGNS_SUPPORTED
from beartype._util.utilobject import (
    get_object_module_name_or_none,
    get_object_type,
)
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_7
from typing import TypeVar

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
        assert isinstance(hint_label, str), f'{repr(hint_label)} not string.'
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not type.')

        raise exception_cls(
            f'{hint_label} {repr(hint)} PEP-compliant '
            f'(e.g., rather than non-"typing" type).')


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
        assert isinstance(hint_label, str), f'{repr(hint_label)} not string.'

        raise BeartypeDecorHintPepException(
            f'{hint_label} {repr(hint)} not PEP-compliant '
            f'(e.g., not "typing" type).')

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
    :func:`beartype._util.hint.pep.get_hint_pep_sign` function). The
    :func:`die_unless_hint_pep_pep_sign_supported` function should be called
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
    assert hint_label.__class__ is str, f'{repr(hint_label)} not string.'

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with is_hint_pep_supported() below.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # If this hint is *NOT* PEP-compliant, raise an exception.
    die_unless_hint_pep(hint=hint, hint_label=hint_label)
    # Else, this hint is PEP-compliant.

    #FIXME: Remove *AFTER* adding support for multiple-inherited generics.
    # If this hint is a multiple-inherited generic, raise an exception. These
    # hints require non-trivial decorator support yet to be implemented.
    if is_hint_pep484_generic_multiple(hint):
        raise BeartypeDecorHintPepUnsupportedException(
            f'{hint_label} multiple-inherited generic PEP hint {repr(hint)} '
            f'{_EXCEPTION_MESSAGE_UNSUPPORTED_SUFFIX}')
    #FIXME: Remove *AFTER* adding support for type variables.
    # Else if this hint is typevared, raise an exception. Type variables
    # require non-trivial decorator support yet to be implemented.
    elif is_hint_pep_typevared(hint):
        raise BeartypeDecorHintPepUnsupportedException(
            f'{hint_label} "TypeVar"-parametrized PEP hint {repr(hint)} '
            f'{_EXCEPTION_MESSAGE_UNSUPPORTED_SUFFIX}')

    # Else, this hint is neither generic nor typevared. In this case, raise a
    # general-purpose exception.
    #
    # Note that, by definition, the argumentless "typing" argument uniquely
    # identifying this hint *SHOULD* be in the "HINT_PEP_SIGNS_SUPPORTED" set.
    # Regardless of whether it is or isn't, we raise a similar exception. Ergo,
    # there's no benefit to validating that expectation here.
    raise BeartypeDecorHintPepUnsupportedException(
        f'{hint_label} PEP hint {repr(hint)} '
        f'{_EXCEPTION_MESSAGE_UNSUPPORTED_SUFFIX}')


def die_unless_hint_pep_pep_sign_supported(
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
    if not is_hint_pep_pep_sign_supported(hint):
        assert isinstance(hint_label, str), f'{repr(hint_label)} not string.'
        raise BeartypeDecorHintPepUnsupportedException(
            f'{hint_label} {repr(hint)} '
            f'{_EXCEPTION_MESSAGE_UNSUPPORTED_SUFFIX}')

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
        is_hint_pep484_generic(hint)
    )

# ....................{ TESTERS ~ supported               }....................
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
        # Is PEP-complaint and is either...

        #FIXME: Remove *AFTER* implementing support for multiple-inherited
        #generics.
        # A multiple-inherited generic...
        #
        # Multiple-inherited generics require non-trivial decorator support.
        is_hint_pep484_generic_multiple(hint) or

        #FIXME: Remove *AFTER* implementing support for type variables.
        # Typevared...
        #
        # Type variables require non-trivial decorator support.
        is_hint_pep_typevared(hint)
    # Return false.
    ):
        return False
    # Else, this hint is PEP-compliant, *NOT* a generic, and *NOT* typevared.

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilhintpepget import (
        get_hint_pep_sign)

    # Argumentless "typing" attribute uniquely identifying this hint.
    hint_pep_sign = get_hint_pep_sign(hint)

    # Return true only if this attribute is supported.
    return is_hint_pep_pep_sign_supported(hint_pep_sign)


def is_hint_pep_pep_sign_supported(hint) -> bool:
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
    # from beartype._util.hint.data.pep.utilhintdatapep import (
    #     HINT_PEP_SIGNS_DEEP_SUPPORTED)
    # print(f'HINT_PEP_SIGNS_DEEP_SUPPORTED: {HINT_PEP_SIGNS_DEEP_SUPPORTED}')

    # Return true only if this hint is a supported argumentless "typing"
    # attribute.
    return hint in HINT_PEP_SIGNS_SUPPORTED

# ....................{ TESTERS ~ typing                  }....................
# If the active Python interpreter targets at least Python 3.7 and is thus
# sane enough to support the normal implementation of this tester, do so.
if IS_PYTHON_AT_LEAST_3_7:
    def is_hint_pep_typing(hint: object) -> bool:
        # Return true only if this type is defined by the "typing" module.
        #
        # Note that this implementation could probably be reduced to the
        # trailing portion of the body of the get_hint_pep_sign()
        # function testing this object's representation. While certainly more
        # compact and convenient than the current approach, that refactored
        # approach would also be considerably more fragile, failure-prone, and
        # subject to whimsical "improvements" in the already overly hostile
        # "typing" API. Why? Because the get_hint_pep_sign() function:
        #
        # * Parses the machine-readable string returned by the __repr__()
        #   dunder method of "typing" types. Since that string is *NOT*
        #   standardized by PEP 484 or any other PEP, "typing" authors remain
        #   free to violate this pseudo-standard in any manner and at any time
        #   of their choosing.
        # * Suffers common edge cases for "typing" types whose __repr__()
        #   dunder methods fail to comply with the non-standard implemented by
        #   their sibling types. This includes the common "TypeVar" type.
        # * Calls this tester function to decide whether the passed object is a
        #   PEP-compliant type hint or not before subjecting that object to
        #   further introspection, which would clearly complicate implementing
        #   this tester function in terms of that getter function.
        #
        # In contrast, the current approach only tests the standardized
        # "__name__" and "__module__" dunder attributes and is thus
        # significantly more robust against whimsical destruction by "typing"
        # authors. Note that there might exist an alternate means of deciding
        # this boolean, documented here merely for completeness:
        #
        #     try:
        #         isinstance(obj, object)
        #         return False
        #     except TypeError as type_error:
        #         return str(type_error).endswith(
        #             'cannot be used with isinstance()')
        #
        # The above effectively implements an Aikido throw by using the fact
        # that "typing" types prohibit isinstance() calls against those types.
        # While clever (and deliciously obnoxious), the above logic:
        #
        # * Requires catching exceptions in the common case and is thus *MUCH*
        #   less efficient than the preferable approach implemented here.
        # * Assumes that *ALL* "typing" types prohibit such calls. Sadly, only
        #   a proper subset of such types prohibit such calls.
        # * Assumes that those "typing" types that do prohibit such calls raise
        #   exceptions with reliable messages across *ALL* Python versions.
        #
        # In short, there is no general-purpose clever solution. *sigh*
        return get_object_module_name_or_none(hint) == 'typing'
# Else, the active Python interpreter targets exactly Python 3.6. In this case,
# define this tester to circumvent Python 3.6-specific issues. Notably, the
# implementation of the "typing" module under this major version harmfully
# modifies the fully-qualified module names advertised by some but *NOT* all
# "collections.abc" superclasses to be "typing" rather than "collections.abc".
# This absolute insanity appears to have something inexplicable to do with
# internal misuse of the private "collections.abc" caches by this
# implementation of the "typing" module. Although the exact cause is unclear,
# the resolution is simply to explicitly test for and reject "collections.abc"
# superclasses passed to this Python 3.6-specific tester implementation.
else:
    def is_hint_pep_typing(hint: object) -> bool:
        # Return true only if...
        return (
            # This type pretends to be defined by the "typing" module *AND*...
            get_object_module_name_or_none(hint) == 'typing' and
            # This type is *NOT* actually a superclass defined by the
            # "collections.abc" submodule. Ideally, we would simply uncomment
            # the following test:
            #     not (
            #         isinstance(hint, type) and
            #         getattr(collections_abc, hint.__name__, None) is hint
            #     )
            #
            # Insanely, that seemingly sane test returns false positives for
            # both "typing.Hashable" and "typing.Sized", which appear to be
            # literally replacing "collections.abc.Hashable" and
            # "collections.abc.Sized" with themselves... somehow.
            #
            # Equally insanely, "typing.Generator" retains a sane
            # representation when accessed as "typing.Generator" but *NOT* when
            # accessed as "collections.abc.Generator" -- the latter of which
            # returns this insane representation. Ergo, we explicitly detect
            # and reject the latter. We have no idea what's happening here and
            # can only wish for the hasty death of Python 3.6. So much rage.
            repr(hint) != "<class 'typing.Generator'>"
        )

# Docstring for this function regardless of implementation details.
is_hint_pep_typing.__doc__ = '''
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

# ....................{ TESTERS ~ typevar                 }....................
def is_hint_pep_typevar(hint: object) -> bool:
    '''
    ``True`` only if the passed object either is a `PEP 484`_-compliant **type
    variable** (i.e., instance of the :class:`TypeVar` class).

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
