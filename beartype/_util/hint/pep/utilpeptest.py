#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **EP-compliant type hint tester utilities** (i.e., callables
validating arbitrary objects to be PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import (
    BeartypeDecorHintPepException,
    BeartypeDecorHintPepDeprecatedWarning,
    BeartypeDecorHintPepUnsupportedException,
    BeartypeDecorHintPep484Exception,
)
from beartype._cave._cavefast import HintGenericSubscriptedType
from beartype._util.cache.utilcachecall import callable_cached
from beartype._data.hint.pep.datapeprepr import (
    HINTS_PEP484_REPR_PREFIX_DEPRECATED,
    HINTS_REPR_PREFIX_DEPRECATED,
)
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignTypeVar,
)
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_SUPPORTED,
    HINT_SIGNS_TYPE_MIMIC,
)
from beartype._data.mod.datamod import (
    TYPING_MODULE_NAMES,
    TYPING_MODULE_NAMES_DOTTED,
)
from beartype._util.hint.pep.proposal.utilpep484 import (
    HINT_PEP484_TUPLE_EMPTY,
    is_hint_pep484_generic,
    is_hint_pep484_ignorable_or_none,
)
from beartype._util.hint.pep.proposal.utilpep544 import (
    is_hint_pep544_ignorable_or_none)
from beartype._util.hint.pep.proposal.utilpep585 import (
    HINT_PEP585_TUPLE_EMPTY,
    is_hint_pep585_builtin,
    is_hint_pep585_generic,
)
from beartype._util.hint.pep.proposal.utilpep593 import (
    is_hint_pep593_ignorable_or_none)
from beartype._util.mod.utilmodule import (
    get_object_module_name,
    get_object_module_name_or_none,
)
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_7
from beartype._util.utilobject import get_object_type_unless_type
from typing import NoReturn, Type, TypeVar
from warnings import warn

# See the "beartype.cave" submodule for further commentary.
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
        hint: object, hint_sign: HintSign) -> Optional[bool]:
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
    hint_label: str = 'Type hint',
    exception_cls: Type[Exception] = BeartypeDecorHintPepException,
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
        ``"Type hint"``.
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
            f'{hint_label} {repr(hint)} is PEP-compliant '
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
        exception message raised by this function. Defaults to ``"Type hint"``.

    Raises
    ----------
    BeartypeDecorHintPepException
        If this object is *not* a PEP-compliant type hint.
    '''

    # If this hint is *NOT* PEP-compliant, raise an exception.
    if not is_hint_pep(hint):
        assert isinstance(hint_label, str), f'{repr(hint_label)} not string.'
        raise BeartypeDecorHintPepException(
            f'{hint_label} {repr(hint)} not PEP-compliant.')

# ....................{ EXCEPTIONS ~ supported            }....................
#FIXME: *DANGER.* This and the die_if_hint_pep_sign_unsupported() function make
#beartype more fragile. Instead, refactor all or most calls to this and the
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
    BeartypeDecorHintPep484Exception
        If this object is the PEP-compliant :attr:`typing.NoReturn` type hint,
        which is contextually valid in only a single use case and thus
        supported externally by the :mod:`beartype._decor._code.codemain`
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
    assert isinstance(hint_label, str), f'{repr(hint_label)} not string.'

    # If this hint is *NOT* PEP-compliant, raise an exception.
    die_unless_hint_pep(hint=hint, hint_label=hint_label)

    # Else, this hint is PEP-compliant.
    #
    # If this is the PEP 484-compliant "typing.NoReturn" type hint permitted
    # *ONLY* as a return annotation, raise an exception specific to this hint.
    if hint is NoReturn:
        raise BeartypeDecorHintPep484Exception(
            f'{hint_label} {repr(hint)} invalid (i.e., "typing.NoReturn" '
            f'valid only as non-nested return annotation).'
        )
    # Else, this is any PEP-compliant type hint other than "typing.NoReturn".
    # In this case, raise a general-purpose exception.
    #
    # Note that, by definition, the sign uniquely identifying this hint
    # *SHOULD* be in the "HINT_SIGNS_SUPPORTED" set. Regardless of whether
    # it is or isn't, we raise a similar exception. Ergo, there's no benefit to
    # validating that expectation here.
    else:
        raise BeartypeDecorHintPepUnsupportedException(
            f'{hint_label} {repr(hint)} currently unsupported by @beartype.')


def die_if_hint_pep_sign_unsupported(
    # Mandatory parameters.
    hint_sign: HintSign,

    # Optional parameters.
    hint_label: str = 'Annotation sign',
) -> None:
    '''
    Raise an exception unless the passed object is a **supported PEP-compliant
    sign** (i.e., arbitrary object uniquely identifying PEP-compliant type
    hints currently supported by the :func:`beartype.beartype` decorator).

    This validator is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : HintSign
        Sign to be validated.
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

    # If this hint is *NOT* a supported sign, raise an exception.
    if hint_sign not in HINT_SIGNS_SUPPORTED:
        assert isinstance(hint_label, str), f'{repr(hint_label)} not string.'
        raise BeartypeDecorHintPepUnsupportedException(
            f'{hint_label} sign {repr(hint_sign)} '
            f'currently unsupported by @beartype.'
        )

# ....................{ WARNINGS                          }....................
#FIXME: Resurrect support for the passed "hint_label" parameter. We've
#currently disabled this parameter as it's typically just a non-human-readable
#placeholder substring *NOT* intended to be exposed to end users (e.g.,
#"$%ROOT_PITH_LABEL/~"). For exceptions, we simply catch raised exceptions and
#replace such substrings with human-readable equivalents. Can we perform a
#similar replacement for warnings?

def warn_if_hint_pep_deprecated(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Annotated',
) -> None:
    '''
    Emit a non-fatal warning if the passed PEP-compliant type hint is
    **deprecated** (i.e., obsoleted by an equivalent type hint or set of type
    hints standardized under one or more recent PEPs).

    This validator is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        PEP-compliant type hint to be inspected.
    hint_label : Optional[str]
        Human-readable label prefixing this object's representation in the
        warning message emitted by this function. Defaults to ``"Annotated"``.

    Warns
    ----------
    BeartypeDecorHintPepDeprecatedWarning
        If this hint is deprecated.
    '''

    # Substring of the machine-readable representation of this hint preceding
    # the first "[" delimiter if this representation contains that delimiter
    # *OR* this representation as is otherwise.
    #
    # Note that the str.partition() method has been profiled to be the
    # optimally efficient means of parsing trivial prefixes.
    hint_bare_repr, _, _ = repr(hint).partition('[')

    # If this representation is deprecated...
    if hint_bare_repr in HINTS_REPR_PREFIX_DEPRECATED:
        #FIXME: Uncomment *AFTER* resolving the "FIXME:" above.
        #FIXME: Unit test that this string contains *NO* non-human-readable
        #placeholder substrings. Note that the existing
        #"beartype_test.a00_unit.decor.code.test_codemain" submodule contains
        #relevant logic currently disabled for reasons that hopefully no longer
        #apply. *Urgh!*

        # assert isinstance(hint_label, str), f'{repr(hint_label)} not string.'
        #
        # # Warning message to be emitted.
        # warning_message = f'{hint_label} PEP type hint {repr(hint)} deprecated'

        # Warning message to be emitted.
        warning_message = f'Type hint {repr(hint)} deprecated'

        # If this sign uniquely identifies PEP 484-compliant type hints
        # originating from origin types (e.g., "typing.List[int]"), this sign
        # has been deprecated by the equivalent PEP 585-compliant sign (e.g.,
        # "list[int]"). In this case, suffix this warning message with
        # pragmatic suggestions for resolving this deprecation.
        if hint_bare_repr in HINTS_PEP484_REPR_PREFIX_DEPRECATED:
            warning_message += (
                ' by PEP 585. To resolve this, globally replace this hint by '
                'the equivalent PEP 585 type hint '
                '(e.g., "typing.List[int]" by "list[int]"). See also:\n'
                '    https://www.python.org/dev/peps/pep-0585'
            )
        # Else, this sign is of unknown deprecation. In this case, simply
        # terminate this unterminated sentence fragment as is.
        else:
            warning_message += '.'

        # Emit this warning.
        # print(f'Emitting {hint_label} hint {repr(hint)} deprecation warning...')
        warn(warning_message, BeartypeDecorHintPepDeprecatedWarning)
    # Else, this sign is *NOT* deprecated. In this case, reduce to a noop.


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
def is_hint_pep(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a **PEP-compliant type hint** (i.e.,
    object either directly defined by the :mod:`typing` module *or* whose type
    subclasses one or more classes directly defined by the :mod:`typing`
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
    ----------
    bool
        ``True`` only if this object is a PEP-compliant type hint.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_sign_or_none)

    # Return true only if this object is uniquely identified by a sign and thus
    # a PEP-compliant type hint.
    return get_hint_pep_sign_or_none(hint) is not None


#FIXME: Unit test us up.
def is_hint_pep_uncached(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a **PEP-compliant non-self-cached
    type hint** (i.e., PEP-compliant type hint that does *not* externally cache
    itself somewhere).

    Since most PEP-compliant type hints are self-caching, this function
    returns:

    * ``True`` for only:

      * :pep:`484`-compliant subscripted generics under Python >= 3.9 (e.g.,
        ``from typing import List; class MuhPep484List(List): pass;
        MuhPep484List[int]``). See below for further commentary.
      * :pep:`585`-compliant type hints, including both:

        * Builtin :pep:`585`-compliant type hints (e.g., ``list[int]``).
        * User-defined :pep:`585`-compliant generics (e.g.,
          ``class MuhPep585List(list): pass; MuhPep585List[int]``).

    * ``False`` for *all* other PEP-compliant type hints.

    Caveats
    ----------
    This function *cannot* be meaningfully memoized, since the passed type hint
    is *not* guaranteed to be cached somewhere. Only functions passed cached
    type hints can be meaningfully memoized. Since this high-level function
    internally defers to unmemoized low-level functions that are ``O(n)`` in
    ``n`` the size of the inheritance hierarchy of this hint, this function
    should be called sparingly. See the :mod:`beartype._decor._cache.cachehint`
    submodule for further details.

    This tester intentionally returns a false negative for :pep:`484`-compliant
    generics subscripted by type variables under Python < 3.9. Although those
    hints are technically non-self-cached, this tester falsely reports those
    hints to be self-cached by returning ``False``. Why? Because correctly
    detecting those hints as non-self-cached would require an unmemoized
    ``O(n)`` search across the inheritance hierarchy of *all* passed objects
    and thus all type hints annotating callables decorated by
    :func:`beartype.beartype`. Since this failure only affects obsolete Python
    versions *and* since the only harms induced by this failure are a slight
    increase in space and time consumption for edge-case type hints unlikely to
    actually be used in real-world code, this tradeoff is more than acceptable.
    We're not the bad guy here. Right?

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a PEP-compliant type hint.
    '''

    # Return true only if this hint is either:
    # * A PEP 585-compliant type hint.
    # * A PEP 484-compliant subscripted generic masquerading as a PEP
    #   585-compliant type hint. *shrug*
    return is_hint_pep585_builtin(hint)

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
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign
    # print(f'Testing PEP hint {repr(hint)} deep ignorability...')

    # Sign uniquely identifying this hint.
    hint_sign = get_hint_pep_sign(hint)

    #FIXME: Remove this *AFTER* properly supporting type variables. For
    #now, ignoring type variables is required ta at least shallowly support
    #generics parametrized by one or more type variables.

    # If this hint is a type variable, return true. Type variables require
    # non-trivial and currently unimplemented decorator support.
    if hint_sign is HintSignTypeVar:
        return True
    # Else, this hint is *NOT* a type variable.

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
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign

    # Sign uniquely identifying this hint.
    hint_sign = get_hint_pep_sign(hint)

    # Return true only if this sign is supported.
    return hint_sign in HINT_SIGNS_SUPPORTED

# ....................{ TESTERS ~ typing                  }....................
#FIXME: Replace all hardcoded "'typing" strings throughout the codebase with
#access of "TYPING_MODULE_NAMES" instead. We only see two remaining in:
#* beartype/_util/hint/pep/proposal/utilpep544.py
#* beartype/_util/hint/pep/proposal/utilpep484.py
#Thankfully, nobody really cares about generalizing these two edge cases to
#"testing_extensions", so they're mostly fine for various definitions of fine.
@callable_cached
def is_hint_pep_typing(hint: object) -> bool:
    '''
    ``True`` only if the passed object is an attribute of a **typing module**
    (i.e., module officially declaring attributes usable for creating
    PEP-compliant type hints accepted by both static and runtime type
    checkers).

    This tester is memoized for efficiency.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is an attribute of a typing module.
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


# If the active Python interpreter targets at least Python 3.7 and is thus
# sane enough to support the normal implementation of this tester, do so.
if IS_PYTHON_AT_LEAST_3_7:
    def is_hint_pep_type_typing(hint: object) -> bool:

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
    def is_hint_pep_type_typing(hint: object) -> bool:

        # This hint if this hint is a class *OR* this hint's class otherwise.
        hint_type = get_object_type_unless_type(hint)
        # print(f'pep_type_typing({repr(hint)}): {repr(hint_type)} {repr(get_object_module_name(hint_type))}')

        # Return true only if...
        return (
            # This type pretends to be defined by a typing module *AND*...
            get_object_module_name(hint_type) in TYPING_MODULE_NAMES and
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


is_hint_pep_type_typing.__doc__ = '''
    ``True`` only if either the passed object is defined by a **typing module**
    (i.e., module officially declaring attributes usable for creating
    PEP-compliant type hints accepted by both static and runtime type checkers)
    if this object is a class *or* the class of this object is defined by a
    typing module otherwise (i.e., if this object is *not* a class).

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

        * If this object is a class, this class is defined by a typing module.
        * Else, the class of this object is defined by a typing module.
    '''

# ....................{ TESTERS ~ subscript               }....................
def is_hint_pep_subscripted(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a **subscripted PEP-compliant type
    hint** (i.e., PEP-compliant type hint indexed by one or more objects).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
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
    ----------
    bool
        ``True`` only if this object is a subscripted PEP-compliant type hint.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_args,
        get_hint_pep_typevars,
    )

    # Return true only if this hint is either...
    return (
        # A PEP-compliant subscripted generic under Python >= 3.9, including:
        # * A PEP 484- or 585-compliant subscripted generic.
        # * A PEP 585-compliant builtin type hint.
        #
        # Surprisingly, this test is *NOT* simply an optimization. Although
        # most subscripted generics do preserve their subscripted objects as
        # one or more arguments and/or type variables, PEP 585-compliant empty
        # tuple type hints (i.e., "tuple[()]") do *NOT*. Thankfully, this
        # simple and efficient test conveniently handles all edge cases
        # associated with PEP 585.
        isinstance(hint, HintGenericSubscriptedType) or
        # Any other PEP-compliant type hint subscripted by one or more
        # arguments and/or type variables. Note that this test is *NOT*
        # reducible to merely:
        #     bool(get_hint_pep_args(hint) or get_hint_pep_typevars(hint))
        # Frankly, we have no idea why. We suspect we'd probably have to
        # change the "or" operator in the above expression to the "+" operator,
        # at which point the resulting operation is likely to be substantially
        # slower than the simple series of tests performed here.
        bool(get_hint_pep_args(hint)) or
        bool(get_hint_pep_typevars(hint))
    )

# ....................{ TESTERS ~ subscript : typevar     }....................
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
        >>> from beartype._util.hint.pep.utilpeptest import (
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
    from beartype._util.hint.pep.utilpepget import get_hint_pep_typevars

    # Return true only if this hint is parametrized by one or more type
    # variables, trivially detected by testing whether the tuple of all type
    # variables parametrizing this hint is non-empty.
    return bool(get_hint_pep_typevars(hint))

# ....................{ TESTERS ~ kind : generic          }....................
@callable_cached
def is_hint_pep_generic(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a **generic** (i.e., class
    superficially subclassing at least one PEP-compliant type hint that is
    possibly *not* an actual class).

    Specifically, this tester returns ``True`` only if this object is a class
    that is either:

    * A :pep:`585`-compliant generic as tested by the lower-level
      :func:`is_hint_pep585_generic` function.
    * A :pep:`484`-compliant generic as tested by the lower-level
      :func:`is_hint_pep484_generic` function.

    This tester is memoized for efficiency. Although the implementation
    trivially reduces to a one-liner, constant factors associated with that
    one-liner are non-negligible. Moreover, this tester is called frequently
    enough to warrant its reduction to an efficient lookup.

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
        Commentary on the relation between generics and parametrized hints.
    '''

    # Return true only if this hint is...
    return (
        # A PEP 484-compliant generic. Note this test trivially reduces to
        # an O(1) operation and is thus tested first.
        is_hint_pep484_generic(hint) or
        # A PEP 585-compliant generic. Note this test is O(n) in n the
        # number of pseudo-superclasses originally subclassed by this
        # generic and is thus tested last.
        is_hint_pep585_generic(hint)
    )

# ....................{ TESTERS ~ kind : tuple            }....................
def is_hint_pep_tuple_empty(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a PEP-compliant **empty fixed-length
    tuple hint** (i.e., PEP-compliant type hint constraining piths to be the
    empty tuple).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as this tester is only called under
    fairly uncommon edge cases.

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
    '''

    # Return true only if this hint resembles either the PEP 484- or
    # 585-compliant fixed-length empty tuple type hint. Since there only exist
    # two such hints *AND* comparison against these hints is mostly fast, this
    # test is efficient in the general case.
    #
    # Note that this test may also be inefficiently performed by explicitly
    # obtaining this hint's sign and then subjecting this hint to specific
    # tests conditionally depending on which sign and thus PEP this hint
    # complies with: e.g.,
    #     # Return true only if this hint is either...
    #     return true (
    #         # A PEP 585-compliant "tuple"-based hint subscripted by no
    #         # child hints *OR*...
    #         (
    #             hint.__origin__ is tuple and
    #             hint_childs_len == 0
    #         ) or
    #         # A PEP 484-compliant "typing.Tuple"-based hint subscripted
    #         # by exactly one child hint *AND* this child hint is the
    #         # empty tuple,..
    #         (
    #             hint.__origin__ is Tuple and
    #             hint_childs_len == 1 and
    #             hint_childs[0] == ()
    #         )
    #     )
    return (
        hint == HINT_PEP585_TUPLE_EMPTY or
        hint == HINT_PEP484_TUPLE_EMPTY
    )
