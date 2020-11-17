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
#FIXME: Refactor is_hint_pep_supported() and die_unless_hint_pep_supported() to
#explicitly reject (with a human-readable exception in the latter case) PEP
#544-compatible protocols *NOT* decorated by @typing.runtime_checkable, as such
#PEP-compliant type hints are unusable at runtime.
#
#Alternately, we could always try something *REAL* sneaky and clever:
#basically, rather than accept "typing" nonsense verbatim, we could instead:
#* Detect PEP 544-compatible protocol type hints *NOT* decorated by
#  @typing.runtime_checkable.
#* Emit a non-fatal warning advising the end user to resolve this on their end.
#* Meanwhile, beartype can simply:
#  * Dynamically fabricate a new PEP 544-compatible protocol decorated by
#    @typing.runtime_checkable using the body of the undecorated user-defined
#    protocol as its base. Indeed, simply subclassing a new subclass decorated
#    by @typing.runtime_checkable from the undecorated user-defined protocol as
#    its base with a noop body of "pass" should suffice.
#  * Replacing all instances of the undecorated user-defined protocol with that
#    decorated beartype-defined protocol in annotations. Note this would
#    strongly benefit from some form of memoization or caching. Since this edge
#    case should be fairly rare, even a dictionary would probably be overkill.
#    Just implementing something resembling the following memoized getter
#    in the "utilhintpep544" submodule would probably suffice:
#        @callable_cached
#        def get_pep544_protocol_checkable_from_protocol_uncheckable(
#            protocol_uncheckable: object) -> Protocol:
#            ...
#
#Checkmate, "typing". Checkmate.

# ....................{ IMPORTS                           }....................
from beartype.roar import (
    BeartypeDecorHintPepException,
    BeartypeDecorHintPepUnsupportedException,
    # BeartypeDecorHintPepIgnorableDeepWarning,
    # BeartypeDecorHintPepUnsupportedWarning,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.data.pep.utilhintdatapep import (
    HINT_PEP_SIGNS_SUPPORTED,
)
from beartype._util.hint.pep.proposal.utilhintpep484 import (
    is_hint_pep484_generic,
    is_hint_pep484_ignorable_or_none,
    is_hint_pep484_newtype,
)
from beartype._util.hint.pep.proposal.utilhintpep544 import (
    is_hint_pep544_ignorable_or_none)
from beartype._util.hint.pep.proposal.utilhintpep585 import (
    is_hint_pep585)
from beartype._util.hint.pep.proposal.utilhintpep593 import (
    is_hint_pep593_ignorable_or_none)
from beartype._util.utilobject import get_object_class_unless_class
from beartype._util.py.utilpymodule import (
    get_object_module_name, get_object_class_module_name_or_none)
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_7
from typing import TypeVar
# from warnings import warn

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
_IS_HINT_PEP_IGNORABLE_TESTERS = (
    is_hint_pep484_ignorable_or_none,
    is_hint_pep544_ignorable_or_none,
    is_hint_pep593_ignorable_or_none,
)
'''
Tuple of all PEP-specific functions testing whether the passed object is an
ignorable type hint fully compliant with a specific PEP.

Each such function is expected to have a signature resembling:

.. code-block:: python

    def is_hint_pep{PEP_NUMBER}_ignorable_or_none(
        hint: object, hint_sign: object) -> Optional[bool]:
        ...

Each such function is expected to return either:

* If the passed object is fully compliant with that PEP:

    * If this object is a ignorable, ``True``.
    * Else, ``False``.

* If this object is *not* fully compliant with that PEP, ``None``.
'''

# ....................{ EXCEPTIONS                        }....................
def die_if_hint_pep(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: 'Optional[str]' = 'Type hint',
    exception_cls: 'Optional[type]' = BeartypeDecorHintPepException,
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
        exception message raised by this function. Defaults to
        ``"Annotation"``.
    exception_cls : Optional[type]
        Type of the exception to be raised by this function. Defaults to
        :class:`BeartypeDecorHintPepException`.

    Raises
    ----------
    exception_cls
        If this object is a PEP-compliant type hint.
    '''

    # If this hint is PEP-compliant...
    if is_hint_pep(hint):
        assert isinstance(hint_label, str), f'{repr(hint_label)} not string.'
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not type.')

        # Raise an exception of this class.
        raise exception_cls(
            f'{hint_label} {repr(hint)} PEP-compliant '
            f'(e.g., rather than non-"typing" type).'
        )


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

# ....................{ EXCEPTIONS ~ supported            }....................
#FIXME: Refactor all or most calls to this and the
#die_if_hint_pep_sign_unsupported() functions into calls to the
#warn_if_hint_pep_unsupported() function; then, consider excising these as well
#as exception classes (e.g., "BeartypeDecorHintPepUnsupportedException").
def die_if_hint_pep_unsupported(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Annotated',
) -> None:
    '''
    Raise an exception if the passed object is a **PEP-compliant unsupported
    type hint** (i.e., :mod:`beartype`-agnostic annotation compliant with
    annotation-centric PEPs currently *not* supported by the
    :func:`beartype.beartype` decorator).

    This validator is effectively (but technically *not*) memoized. See the
    :func:`beartype._util.hint.utilhinttest.die_unless_hint` validator.

    Caveats
    ----------
    **This function should never be called to validate either signs or
    unsubscripted** :mod:`typing` **objects** (e.g., those returned by the
    :func:`beartype._util.hint.pep.get_hint_pep_sign` function). The
    :func:`die_if_hint_pep_sign_unsupported` function should be called
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
    assert isinstance(hint_label, str), f'{repr(hint_label)} not string.'

    # If this hint is *NOT* PEP-compliant, raise an exception.
    die_unless_hint_pep(hint=hint, hint_label=hint_label)

    # Else, this hint is PEP-compliant. In this case, raise an exception.
    #
    # Note that, by definition, the unsubscripted "typing" argument uniquely
    # identifying this hint *SHOULD* be in the "HINT_PEP_SIGNS_SUPPORTED" set.
    # Regardless of whether it is or isn't, we raise a similar exception. Ergo,
    # there's no benefit to validating that expectation here.
    raise BeartypeDecorHintPepUnsupportedException(
        f'{hint_label} PEP type hint {repr(hint)} '
        f'currently unsupported by @beartype.'
    )


def die_if_hint_pep_sign_unsupported(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Unsubscripted "typing" attribute',
) -> None:
    '''
    Raise an exception unless the passed object is a **PEP-compliant supported
    unsubscripted typing attribute** (i.e., public attribute of the
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

    # If this hint is *NOT* a supported unsubscripted "typing" attribute, raise
    # an exception.
    if not is_hint_pep_sign_supported(hint):
        assert isinstance(hint_label, str), f'{repr(hint_label)} not string.'
        raise BeartypeDecorHintPepUnsupportedException(
            f'{hint_label} PEP sign {repr(hint)} '
            f'currently unsupported by @beartype.'
        )

# ....................{ WARNINGS                          }....................
#FIXME: Unit test us up.
#FIXME: Actually use us in place of die_if_hint_pep_unsupported().
#FIXME: Actually, it's unclear whether we still require or desire this. See
#"_pephint" commentary for further details.
# def warn_if_hint_pep_unsupported(
#     # Mandatory parameters.
#     hint: object,
#
#     # Optional parameters.
#     hint_label: str = 'Annotated',
# ) -> bool:
#     '''
#     Return ``True`` and emit a non-fatal warning only if the passed object is a
#     **PEP-compliant unsupported type hint** (i.e., :mod:`beartype`-agnostic
#     annotation compliant with annotation-centric PEPs currently *not* supported
#     by the :func:`beartype.beartype` decorator).
#
#     This validator is effectively (but technically *not*) memoized. See the
#     :func:`beartype._util.hint.utilhinttest.die_unless_hint` validator.
#
#     Parameters
#     ----------
#     hint : object
#         Object to be validated.
#     hint_label : Optional[str]
#         Human-readable label prefixing this object's representation in the
#         warning message emitted by this function. Defaults to ``"Annotated"``.
#
#     Returns
#     ----------
#     bool
#         ``True`` only if this PEP-compliant type hint is currently supported by
#         that decorator.
#
#     Raises
#     ----------
#     BeartypeDecorHintPepException
#         If this object is *not* a PEP-compliant type hint.
#
#     Warnings
#     ----------
#     BeartypeDecorHintPepUnsupportedWarning
#         If this object is a PEP-compliant type hint currently unsupported by
#         that decorator.
#     '''
#
#     # True only if this object is a supported PEP-compliant type hint.
#     #
#     # Note that this memoized call is intentionally passed positional rather
#     # than keyword parameters to maximize efficiency.
#     is_hint_pep_supported_test = is_hint_pep_supported(hint)
#
#     # If this object is an unsupported PEP-compliant type hint...
#     if not is_hint_pep_supported_test:
#         assert isinstance(hint_label, str), f'{repr(hint_label)} not string.'
#
#         # If this hint is *NOT* PEP-compliant, raise an exception.
#         die_unless_hint_pep(hint=hint, hint_label=hint_label)
#
#         # Else, this hint is PEP-compliant. In this case, emit a warning.
#         warn(
#             (
#                 f'{hint_label} PEP type hint {repr(hint)} '
#                 f'currently unsupported by @beartype.'
#             ),
#             BeartypeDecorHintPepUnsupportedWarning
#         )
#
#     # Return true only if this object is a supported PEP-compliant type hint.
#     return is_hint_pep_supported_test

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

    # Avoid circular import dependencies.
    from beartype._util.hint.utilhinttest import is_hint_forwardref

    # Either the passed object if this object is a class *OR* the class of this
    # object otherwise (i.e., if this object is *NOT* a class).
    hint_type = get_object_class_unless_class(hint)

    # Return true only if either...
    #
    # Note that these tests are intentionally ordered in descending likelihood
    # of a match with the least common type hints tested last and the most
    # common type hints tested first.
    return (
        # This hint's type is directly declared by the "typing" module and thus
        # PEP-compliant by definition *OR*...
        is_hint_pep_class_typing(hint_type) or
        # This hint is a PEP 585-compliant type hint.
        is_hint_pep585(hint) or
        # This hint is a PEP 484-compliant generic. Although a small subset of
        # generics are directly defined by the "typing" module (e.g.,
        # "typing.IO"), most generics are user-defined subclasses defined by
        # user-defined modules residing elsewhere.
        is_hint_pep484_generic(hint) or
        # This hint is a forward reference type hint.
        #
        # Note this unconditionally matches *ALL* forward references, including
        # absolute forward references (i.e., fully-qualified classnames)
        # technically non-compliant with PEP 484 but seemingly compliant with
        # PEP 585. Since the distinction between PEP-compliant and
        # -noncompliant forward references is murky at best and since
        # unconditionally matching *ALL* forward references as PEP-compliant
        # substantially simplifies logic throughout the codebase, we do so.
        is_hint_forwardref(hint) or
        # This hint is a PEP 484-compliant new type hint.
        is_hint_pep484_newtype(hint)
    )

# ....................{ TESTERS ~ ignorable               }....................
def is_hint_pep_ignorable(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a **deeply ignorable PEP-compliant
    type hint** (i.e., PEP-compliant type hint shown to be ignorable only after
    recursively inspecting the contents of this hint).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as this tester is only safely callable
    by the memoized parent
    :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a deeply ignorable PEP-compliant type
        hint.

    Warnings
    ----------
    BeartypeDecorHintPepIgnorableDeepWarning
        If this object is a deeply ignorable PEP-compliant type hint. Why?
        Because deeply ignorable PEP-compliant type hints convey *no*
        meaningful semantics but superficially appear to do so. Consider
        ``Union[str, List[int], NewType('MetaType', Annotated[object, 53])]``,
        for example; this PEP-compliant type hint effectively reduces to
        ``typing.Any`` and thus conveys *no* meaningful semantics despite
        superficially appearing to do so.
    '''


    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilhintpepget import get_hint_pep_sign

    #FIXME: Remove this *AFTER* properly supporting type variables. For
    #now, ignoring type variables is required ta at least shallowly support
    #generics parametrized by one or more type variables.

    # If this hint is a type variable, return true. Type variables require
    # non-trivial and currently unimplemented decorator support.
    if is_hint_pep_typevar(hint):
        return True

    # Sign uniquely identifying this hint.
    hint_sign = get_hint_pep_sign(hint)

    # For each PEP-specific function testing whether this hint is an ignorable
    # type hint fully compliant with that PEP...
    for is_hint_pep_ignorable_tester in _IS_HINT_PEP_IGNORABLE_TESTERS:
        # True only if this hint is a ignorable under this PEP, False only if
        # this hint is unignorable under this PEP, and None if this hint is
        # *NOT* compliant with this PEP.
        is_hint_pep_ignorable_or_none = is_hint_pep_ignorable_tester(
            hint, hint_sign)

        # If this hint is compliant with this PEP...
        # print(f'{is_hint_pep_ignorable_or_none} = {is_hint_pep_ignorable_tester}({hint}, {hint_sign})')
        if is_hint_pep_ignorable_or_none is not None:
            #FIXME: Uncomment *AFTER* we properly support type variables. Since
            #we currently ignore type variables, uncommenting this now would
            #raise spurious warnings for otherwise unignorable and absolutely
            #unsuspicious generics and protocols parametrized by type
            #variables, which would be worse than the existing situation.

            # # If this hint is ignorable under this PEP, warn the user this hint
            # # is deeply ignorable. (See the docstring for justification.)
            # if is_hint_pep_ignorable_or_none:
            #     warn(
            #         (
            #             f'Ignorable PEP type hint {repr(hint)} '
            #             f'typically not intended to be ignored.'
            #         ),
            #         BeartypeDecorHintPepIgnorableDeepWarning,
            #     )

            # Return this boolean.
            return is_hint_pep_ignorable_or_none
        # Else, this hint is *NOT* compliant with this PEP. In this case,
        # silently continue to the next such tester.

    # Else, this hint is *NOT* deeply ignorable. In this case, return false.
    return False

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

    # If this hint is *NOT* PEP-compliant, immediately return false.
    if not is_hint_pep(hint):
        return False
    # Else, this hint is PEP-compliant.

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilhintpepget import (
        get_hint_pep_sign)

    # Unsubscripted "typing" attribute uniquely identifying this hint.
    hint_pep_sign = get_hint_pep_sign(hint)

    # Return true only if this attribute is supported.
    return is_hint_pep_sign_supported(hint_pep_sign)


def is_hint_pep_sign_supported(hint) -> bool:
    '''
    ``True`` only if the passed object is a **PEP-compliant supported
    unsubscripted typing attribute** (i.e., public attribute of the
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
        ``True`` only if this object is a PEP-compliant supported unsubscripted
        typing attribute.

    Raises
    ----------
    TypeError
        If this object is **unhashable** (i.e., *not* hashable by the builtin
        :func:`hash` function and thus unusable in hash-based containers like
        dictionaries and sets). All supported type hints are hashable.
    '''
    # from beartype._util.hint.data.pep.utilhintdatapep import (
    #     HINT_PEP_SIGNS_SUPPORTED_DEEP)
    # print(f'HINT_PEP_SIGNS_SUPPORTED_DEEP: {HINT_PEP_SIGNS_SUPPORTED_DEEP}')

    # Return true only if this hint is a supported unsubscripted "typing"
    # attribute.
    return hint in HINT_PEP_SIGNS_SUPPORTED

# ....................{ TESTERS ~ typing                  }....................
def is_hint_pep_typing(hint: object) -> bool:
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

    return repr(hint).startswith('typing.')


# If the active Python interpreter targets at least Python 3.7 and is thus
# sane enough to support the normal implementation of this tester, do so.
if IS_PYTHON_AT_LEAST_3_7:
    def is_hint_pep_class_typing(hint: object) -> bool:
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
        return get_object_module_name(get_object_class_unless_class(hint)) == (
            'typing')
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
    def is_hint_pep_class_typing(hint: object) -> bool:
        # Return true only if...
        return (
            # This type pretends to be defined by the "typing" module *AND*...
            get_object_module_name(get_object_class_unless_class(hint)) == (
                'typing') and
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
is_hint_pep_class_typing.__doc__ = '''
    ``True`` only if either the passed object is defined by the :mod:`typing`
    module if this object is a class *or* the class of this object is defined
    by the :mod:`typing` module otherwise (i.e., if this object is *not* a
    class).

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
        ``True`` only if either:

        * If this object is a class, this class is defined by the :mod:`typing`
          module.
        * Else, the class of this object is defined by the :mod:`typing`
          module.
    '''

# ....................{ TESTERS ~ subtype : typevar       }....................
def is_hint_pep_typevar(hint: object) -> bool:
    '''
    ``True`` only if the passed object either is a PEP-compliant **type
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
