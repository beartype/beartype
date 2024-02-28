#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-compliant type hint tester** (i.e., callable validating an
arbitrary object to be a PEP-compliant type hint) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeDecorHintPepException,
    BeartypeDecorHintPepUnsupportedException,
    BeartypeDecorHintPep484Exception,
)
from beartype.typing import (
    Dict,
    NoReturn,
)
from beartype._data.hint.datahinttyping import TypeException
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignAnnotated,
    HintSignGeneric,
    HintSignOptional,
    HintSignNewType,
    HintSignPep695TypeAlias,
    HintSignProtocol,
    HintSignTypeVar,
    HintSignUnion,
)
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_SUPPORTED,
    HINT_SIGNS_TYPE_MIMIC,
)
from beartype._data.module.datamodtyping import TYPING_MODULE_NAMES
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.pep.proposal.pep484.utilpep484 import (
    is_hint_pep484_typevar_ignorable,
    is_hint_pep484585_generic_ignorable,
    is_hint_pep484604_union_ignorable,
)
from beartype._util.hint.pep.proposal.pep484.utilpep484newtype import (
    is_hint_pep484_newtype_ignorable)
from beartype._util.hint.pep.proposal.utilpep544 import is_hint_pep544_ignorable
from beartype._util.hint.pep.proposal.utilpep593 import is_hint_pep593_ignorable
from beartype._util.hint.pep.proposal.utilpep695 import is_hint_pep695_ignorable
from beartype._util.module.utilmodget import get_object_module_name_or_none
from beartype._util.utilobject import get_object_type_unless_type
from collections.abc import Callable

# ....................{ EXCEPTIONS                         }....................
def die_if_hint_pep(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPepException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception of the passed type if the passed object is a
    **PEP-compliant type hint** (i.e., :mod:`beartype`-agnostic annotation
    compliant with annotation-centric PEPs).

    This validator is effectively (but technically *not*) memoized. See the
    :func:`beartype._util.hint.utilhinttest.die_unless_hint` validator.

    Parameters
    ----------
    hint : object
        Object to be validated.
    exception_cls : Type[Exception], optional
        Type of the exception to be raised by this function. Defaults to
        :exc:`.BeartypeDecorHintPepException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ------
    exception_cls
        If this object is a PEP-compliant type hint.
    '''

    # If this hint is PEP-compliant...
    if is_hint_pep(hint):
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not type.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Raise an exception of this class.
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} is PEP-compliant '
            f'(e.g., rather than isinstanceable class).'
        )


def die_unless_hint_pep(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPepException,
    exception_prefix: str = '',
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
    exception_cls : Type[Exception], optional
        Type of the exception to be raised by this function. Defaults to
        :class:`.BeartypeDecorHintPepException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ------
    exception_cls
        If this object is *not* a PEP-compliant type hint.
    '''

    # If this hint is *NOT* PEP-compliant, raise an exception.
    if not is_hint_pep(hint):
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not type.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} not PEP-compliant.')

# ....................{ EXCEPTIONS ~ supported             }....................
#FIXME: *DANGER.* This function makes beartype more fragile. Instead, refactor
#all or most calls to this function into calls to the
#warn_if_hint_pep_unsupported() function; then, consider excising this as well
#as exception classes (e.g., "BeartypeDecorHintPepUnsupportedException").
def die_if_hint_pep_unsupported(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception if the passed object is a **PEP-compliant unsupported
    type hint** (i.e., :mod:`beartype`-agnostic annotation compliant with
    annotation-centric PEPs currently *not* supported by the
    :func:`beartype.beartype` decorator).

    This validator is effectively (but technically *not*) memoized. See the
    :func:`beartype._util.hint.utilhinttest.die_unless_hint` validator.

    Caveats
    -------
    **This validator only shallowly validates this object.** If this object is a
    subscripted PEP-compliant type hint (e.g., ``Union[str, List[int]]``), this
    validator ignores all subscripted arguments (e.g., ``List[int]``) on this
    hint and may thus return false positives for hints that are directly
    supported but whose subscripted arguments are not. To deeply validate this
    object, iteratively call this validator during a recursive traversal (such
    as a breadth-first search) over each subscripted argument of this object.

    Parameters
    ----------
    hint : object
        Object to be validated.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ------
    BeartypeDecorHintPepException
        If this object is *not* a PEP-compliant type hint.
    BeartypeDecorHintPepUnsupportedException
        If this object is a PEP-compliant type hint but is currently
        unsupported by the :func:`beartype.beartype` decorator.
    BeartypeDecorHintPep484Exception
        If this object is the PEP-compliant :attr:`typing.NoReturn` type hint,
        which is contextually valid in only a single use case and thus
        supported externally by the :mod:`beartype._decor.wrap.wrapmain`
        submodule rather than with general-purpose automation.
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

    # If this hint is *NOT* PEP-compliant, raise an exception.
    die_unless_hint_pep(hint=hint, exception_prefix=exception_prefix)
    assert isinstance(exception_prefix, str), (
        f'{repr(exception_prefix)} not string.')

    # Else, this hint is PEP-compliant.
    #
    # If this is the PEP 484-compliant "typing.NoReturn" type hint permitted
    # *ONLY* as a return annotation, raise an exception specific to this hint.
    if hint is NoReturn:
        raise BeartypeDecorHintPep484Exception(
            f'{exception_prefix}PEP 484 type hint "{repr(hint)}" '
            f'invalid in this type hint context (i.e., '
            f'"{repr(hint)}" valid only as non-nested return annotation).'
        )
    # Else, this is any PEP-compliant type hint other than "typing.NoReturn".

    # In this case, raise a general-purpose exception.
    #
    # Note that, by definition, the sign uniquely identifying this hint *SHOULD*
    # be in the "HINT_SIGNS_SUPPORTED" set. Regardless of whether it is or not,
    # we raise a similar exception in either case. Ergo, there is *NO* practical
    # benefit to validating that expectation here.
    raise BeartypeDecorHintPepUnsupportedException(
        f'{exception_prefix}type hint {repr(hint)} '
        f'currently unsupported by @beartype.'
    )

# ....................{ WARNINGS                           }....................
#FIXME: Unit test us up.
#FIXME: Actually use us in place of die_if_hint_pep_unsupported().
#FIXME: Actually, it's unclear whether we still require or desire this. See
#"_pephint" commentary for further details.
# def warn_if_hint_pep_unsupported(
#     # Mandatory parameters.
#     hint: object,
#
#     # Optional parameters.
#     exception_prefix: str = 'Annotated',
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
#     exception_prefix : Optional[str]
#         Human-readable label prefixing this object's representation in the
#         warning message emitted by this function. Defaults to the empty string.
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
#         assert isinstance(exception_prefix, str), f'{repr(exception_prefix)} not string.'
#
#         # If this hint is *NOT* PEP-compliant, raise an exception.
#         die_unless_hint_pep(hint=hint, exception_prefix=exception_prefix)
#
#         # Else, this hint is PEP-compliant. In this case, emit a warning.
#         warn(
#             (
#                 f'{exception_prefix}PEP type hint {repr(hint)} '
#                 f'currently unsupported by @beartype.'
#             ),
#             BeartypeDecorHintPepUnsupportedWarning
#         )
#
#     # Return true only if this object is a supported PEP-compliant type hint.
#     return is_hint_pep_supported_test

# ....................{ TESTERS                            }....................
def is_hint_pep(hint: object) -> bool:
    '''
    :data:`True` only if the passed object is a **PEP-compliant type hint**
    (i.e., object either directly defined by the :mod:`typing` module *or* whose
    type subclasses one or more classes directly defined by the :mod:`typing`
    module).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Motivation
    ----------
    Standard Python types allow callers to test for compliance with protocols,
    interfaces, and abstract base classes by calling either the
    :func:`isinstance` or :func:`issubclass` builtins. This is the
    well-established Pythonic standard for deciding conformance to an API.

    Insanely, :pep:`484` *and* the :mod:`typing` module implementing :pep:`484`
    reject community standards by explicitly preventing callers from calling
    either the :func:`isinstance` or :func:`issubclass` builtins on most but
    *not* all :pep:`484` objects and types. Moreover, neither :pep:`484` nor
    :mod:`typing` implement public APIs for testing whether arbitrary objects
    comply with :pep:`484` or :mod:`typing`.

    Thus this function, which "fills in the gaps" by implementing this
    laughably critical oversight.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a PEP-compliant type hint.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_sign_or_none)

    # Sign uniquely identifying this hint if this hint is PEP-compliant *OR*
    # "None" otherwise (i.e., if this hint is *NOT* PEP-compliant).
    hint_sign = get_hint_pep_sign_or_none(hint)
    # print(f'hint: {repr(hint)}; sign: {repr(hint_sign)}')

    # Return true *ONLY* if this hint is uniquely identified by a sign and thus
    # PEP-compliant.
    return hint_sign is not None


#FIXME: Currently unused but preserved for posterity. *shrug*
# def is_hint_pep_deprecated(hint: object) -> bool:
#     '''
#     :data:`True` only if the passed PEP-compliant type hint is **deprecated**
#     (i.e., obsoleted by an equivalent PEP-compliant type hint standardized by a
#     more recently released PEP).
#
#     This tester is intentionally *not* memoized (e.g., by the
#     ``callable_cached`` decorator), as this tester is currently *only* called at
#     test time from our test suite.
#
#     Parameters
#     ----------
#     hint : object
#         PEP-compliant type hint to be inspected.
#
#     Returns
#     -------
#     bool
#         :data:`True` only if this PEP-compliant type hint is deprecated.
#     '''
#
#     # Avoid circular import dependencies.
#     from beartype._util.hint.pep.utilpepget import get_hint_pep_sign
#
#     # Sign uniquely identifying this hint.
#     hint_sign = get_hint_pep_sign(hint)
#
#     # Return true only if either...
#     return (
#         # This sign is that of an unconditionally deprecated type hint *OR*...
#         hint_sign in HINT_SIGNS_DEPRECATED or
#         # This is a PEP 484-compliant type hint (e.g., "typing.List[str]")
#         # conditionally deprecated by an equivalent PEP 585-compliant type hint
#         # (e.g., "list[str]") under Python >= 3.9.
#         #
#         # Note that, in this case, the sign of this hint does *NOT* convey
#         # enough metadata to ascertain whether this hint is deprecated. Ergo, a
#         # non-trivial tester dedicated to this discernment is required: e.g.,
#         # * "list[str]" has the sign "HintSignList" but is *NOT* deprecated.
#         # * "typing.List[str]" has the sign "HintSignList" but is deprecated.
#         is_hint_pep484_deprecated(hint)
#     )


def is_hint_pep_ignorable(hint: object) -> bool:
    '''
    :data:`True` only if the passed PEP-compliant type hint is **deeply
    ignorable** (i.e., shown to be ignorable only after recursively inspecting
    the contents of this hint).

    This tester is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as this tester is only safely callable by
    the memoized parent
    :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester.

    Parameters
    ----------
    hint : object
        PEP-compliant type hint to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this PEP-compliant type hint is deeply ignorable.

    Warns
    -----
    BeartypeDecorHintPepIgnorableDeepWarning
        If this object is a deeply ignorable PEP-compliant type hint. Why?
        Because deeply ignorable PEP-compliant type hints convey *no*
        meaningful semantics but superficially appear to do so. Consider
        ``Union[str, List[int], NewType('MetaType', Annotated[object, 53])]``,
        for example; this PEP-compliant type hint effectively reduces to
        :obj:`typing.Any` and thus conveys *no* meaningful semantics despite
        superficially appearing to do so.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign
    # print(f'Testing PEP hint {repr(hint)} deep ignorability...')

    # Sign uniquely identifying this hint.
    hint_sign = get_hint_pep_sign(hint)

    # Ignorer (i.e., callable testing whether this hint is ignorable) if an
    # ignorer for hints of this sign was registered *OR* "None" otherwise (i.e.,
    # if *NO* ignorer was registered, in which case this hint is unignorable).
    is_hint_ignorable = _HINT_SIGN_TO_IS_HINT_IGNORABLE.get(hint_sign)

    # Return either...
    return (
        # If an ignorer for hints of this sign was registered, the boolean
        # returned when passing this ignorer this hint);
        is_hint_ignorable(hint)
        if is_hint_ignorable else
        # Else, *NO* ignorer for hints of this sign was registered, implying
        # this hint to be unignorable. Return false.
        False
    )


@callable_cached
def is_hint_pep_supported(hint: object) -> bool:
    '''
    :data:`True` only if the passed object is a **PEP-compliant supported type
    hint** (i.e., :mod:`beartype`-agnostic annotation compliant with
    annotation-centric PEPs currently supported by the
    :func:`beartype.beartype` decorator).

    This tester is memoized for efficiency.

    Caveats
    -------
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
    -------
    bool
        :data:`True` only if this object is a supported PEP-compliant type hint.
    '''

    # If this hint is *NOT* PEP-compliant, immediately return false.
    if not is_hint_pep(hint):
        return False
    # Else, this hint is PEP-compliant.

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign

    # Sign uniquely identifying this hint.
    hint_sign = get_hint_pep_sign(hint)

    # Return true only if this sign is supported.
    return hint_sign in HINT_SIGNS_SUPPORTED

# ....................{ TESTERS ~ typing                   }....................
#FIXME: Replace all hardcoded "'typing" strings throughout the codebase with
#access of "TYPING_MODULE_NAMES" instead. We only see one remaining in:
#* beartype._util.hint.pep.proposal.pep484.utilpep484.py
#Thankfully, nobody really cares about generalizing this one edge case to
#"testing_extensions", so it's mostly fine for various definitions of fine.
@callable_cached
def is_hint_pep_typing(hint: object) -> bool:
    '''
    :data:`True` only if the passed object is an attribute of a **typing
    module** (i.e., module officially declaring attributes usable for creating
    PEP-compliant type hints accepted by both static and runtime type checkers).

    This tester is memoized for efficiency.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is an attribute of a typing module.
    '''
    # print(f'is_hint_pep_typing({repr(hint)}')

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_sign_or_none)

    # Return true only if this hint is either...
    return (
        # Any PEP-compliant type hint defined by a typing module (except those
        # maliciously masquerading as another type entirely) *OR*...
        get_object_module_name_or_none(hint) in TYPING_MODULE_NAMES or
        # Any PEP-compliant type hint defined by a typing module maliciously
        # masquerading as another type entirely.
        get_hint_pep_sign_or_none(hint) in HINT_SIGNS_TYPE_MIMIC
    )


def is_hint_pep_type_typing(hint: object) -> bool:
    '''
    :data:`True` only if either the passed object is defined by a **typing
    module** (i.e., module officially declaring attributes usable for creating
    PEP-compliant type hints accepted by both static and runtime type checkers)
    if this object is a class *or* the class of this object is defined by a
    typing module otherwise (i.e., if this object is *not* a class).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`.callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if either:

        * If this object is a class, this class is defined by a typing module.
        * Else, the class of this object is defined by a typing module.
    '''

    # This hint if this hint is a class *OR* this hint's class otherwise.
    hint_type = get_object_type_unless_type(hint)
    # print(f'pep_type_typing({repr(hint)}): {get_object_module_name(hint_type)}')

    # Return true only if this type is defined by a typing module.
    #
    # Note that this implementation could probably be reduced to the
    # leading portion of the body of the get_hint_pep_sign_or_none()
    # function testing this object's representation. While certainly more
    # compact and convenient than the current approach, that refactored
    # approach would also be considerably more fragile, failure-prone, and
    # subject to whimsical "improvements" in the already overly hostile
    # "typing" API. Why? Because the get_hint_pep_sign_or_none() function:
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
    # In contrast, the current approach only tests the standard
    # "__module__" dunder attribute and is thus significantly more robust
    # against whimsical destruction by "typing" authors. Note that there
    # might exist an alternate means of deciding this boolean, documented
    # here merely for completeness:
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
    # * Requires catching exceptions in the common case and is thus *MUCH*
    #   less efficient than the preferable approach implemented here.
    # * Assumes that *ALL* "typing" types prohibit such calls. Sadly, only
    #   a proper subset of these types prohibit such calls.
    # * Assumes that those "typing" types that do prohibit such calls raise
    #   exceptions with reliable messages across *ALL* Python versions.
    #
    # In short, there is no general-purpose clever solution. *sigh*
    return hint_type.__module__ in TYPING_MODULE_NAMES

# ....................{ TESTERS ~ args                     }....................
#FIXME: Overkill. Replace directly with a simple test, please.
#
#Note that the corresponding unit test should be preserved, as that test is
#essential to ensuring sanity across type hints and Python versions.
def is_hint_pep_args(hint: object) -> bool:
    '''
    :data:`True` only if the passed object is a **subscripted PEP-compliant type
    hint** (i.e., PEP-compliant type hint directly indexed by one or more
    objects).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`.callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    -------
    **Callers should not assume that the objects originally subscripting this
    hint are still accessible.** Although *most* hints preserve their
    subscripted objects over their lifetimes, a small subset of edge-case hints
    erase those objects at subscription time. This includes:

    * :pep:`585`-compliant empty tuple type hints (i.e., ``tuple[()]``), which
      despite being explicitly subscripted erroneously erase that subscription
      at subscription time. This does *not* extend to :pep:`484`-compliant
      empty tuple type hints (i.e., ``typing.Tuple[()]``), which correctly
      preserve that subscripted empty tuple.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a subscripted PEP-compliant type
        hint.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_args

    # Return true only if this hint is subscripted by one or more arguments.
    return bool(get_hint_pep_args(hint))

# ....................{ TESTERS ~ typevars                 }....................
#FIXME: Overkill. Replace directly with a simple test, please.
#
#Note that the corresponding unit test should be preserved, as that test is
#essential to ensuring sanity across type hints and Python versions.
def is_hint_pep_typevars(hint: object) -> bool:
    '''
    :data:`True` only if the passed object is a PEP-compliant type hint
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
    ---------
    **Generics** (i.e., PEP-compliant type hints whose classes subclass one or
    more public :mod:`typing` pseudo-superclasses) are often but *not* always
    typevared. For example, consider the untypevared generic:

    .. code-block:: pycon

       >>> from typing import List
       >>> class UntypevaredGeneric(List[int]): pass
       >>> UntypevaredGeneric.__mro__
       (__main__.UntypevaredGeneric, list, typing.Generic, object)
       >>> UntypevaredGeneric.__parameters__
       ()

    Likewise, typevared hints are often but *not* always generic. For example,
    consider the typevared non-generic:

    .. code-block:: pycon

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
    -------
    bool
        :data:`True` only if this object is a PEP-compliant type hint
        parametrized by one or more type variables.

    Examples
    --------
    .. code-block:: pycon

       >>> import typing
       >>> from beartype._util.hint.pep.utilpeptest import (
       ...     is_hint_pep_typevars)
       >>> T = typing.TypeVar('T')
       >>> class UserList(typing.List[T]): pass
       # Unparametrized type hint.
       >>> is_hint_pep_typevars(typing.List[int])
       False
       # Directly parametrized type hint.
       >>> is_hint_pep_typevars(typing.List[T])
       True
       # Superclass-parametrized type hint.
       >>> is_hint_pep_typevars(UserList)
       True
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_typevars

    # Return true only if this hint is parametrized by one or more type
    # variables, trivially detected by testing whether the tuple of all type
    # variables parametrizing this hint is non-empty.
    return bool(get_hint_pep_typevars(hint))

# ....................{ PRIVATE ~ dicts                    }....................
# Note that this type hints would ideally be defined with the mypy-specific
# "callback protocol" pseudostandard, documented here:
#     https://mypy.readthedocs.io/en/stable/protocols.html#callback-protocols
#
# Doing so would enable static type-checkers to type-check that the values of
# this dictionary are valid ignorer functions. Sadly, that pseudostandard is
# absurdly strict to the point of practical uselessness. Attempting to conform
# to that pseudostandard would require refactoring *ALL* ignorer functions to
# explicitly define the same signature. However, we have intentionally *NOT*
# done that. Why? Doing so would substantially increase the fragility of this
# API by preventing us from readily adding and removing infrequently required
# parameters (e.g., "cls_stack", "pith_name"). Callback protocols suck, frankly.
_HINT_SIGN_TO_IS_HINT_IGNORABLE: Dict[HintSign, Callable] = {
    # ..................{ PEP 484                            }..................
    # Ignore *ALL* PEP 484-compliant "NewType"-style type aliases aliasing
    # ignorable type hints.
    HintSignNewType: is_hint_pep484_newtype_ignorable,

    # Ignore *ALL* PEP 484-compliant type variables.
    HintSignTypeVar: is_hint_pep484_typevar_ignorable,

    # ..................{ PEP (484|585)                      }..................
    # Ignore *ALL* PEP 484- and 585-compliant "Generic[...]" subscriptions.
    HintSignGeneric: is_hint_pep484585_generic_ignorable,

    # ..................{ PEP (484|604)                      }..................
    # Ignore *ALL* PEP 484- and 604-compliant unions subscripted by one or more
    # ignorable type hints.
    HintSignOptional: is_hint_pep484604_union_ignorable,
    HintSignUnion:    is_hint_pep484604_union_ignorable,

    # ..................{ PEP 544                            }..................
    # Ignore *ALL* PEP 544-compliant "typing.Protocol[...]" subscriptions.
    HintSignProtocol: is_hint_pep544_ignorable,

    # ..................{ PEP 593                            }..................
    # Ignore *ALL* PEP 593-compliant "typing.Annotated[...]" type hints except
    # those indexed by one or more beartype validators.
    HintSignAnnotated: is_hint_pep593_ignorable,

    # ..................{ PEP 695                            }..................
    # Ignore *ALL* PEP 695-compliant type aliases aliasing ignorable type hints.
    HintSignPep695TypeAlias: is_hint_pep695_ignorable,
}
'''
Dictionary mapping from each sign uniquely identifying PEP-compliant type hints
to that sign's **ignorer** (i.e., low-level function testing whether the passed
type hint identified by that sign is deeply ignorable).

Each value of this dictionary is expected to have a signature resembling:

.. code-block:: python

   def is_hint_pep{pep_number}_ignorable(hint: object) -> bool: ...

Note that:

* Ignorers do *not* need to validate the passed type hint as being of the
  expected sign. By design, an ignorer is only ever passed a type hint of the
  expected sign.
* Ignorers should *not* be memoized (e.g., by the
  `callable_cached`` decorator). Since the higher-level
  :func:`.is_hint_pep_ignorable` function that is the sole entry point to
  calling all lower-level ignorers is itself effectively memoized, ignorers
  themselves neither require nor benefit from memoization.
'''
