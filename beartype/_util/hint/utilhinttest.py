#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-agnostic type hint tester utilities** (i.e., callables
validating arbitrary objects to be PEP-agnostic type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import (
    BeartypeDecorHintTypeException,
    BeartypeDecorHintForwardRefException,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cls.utilclstest import (
    die_unless_type, is_type_isinstanceable)
from beartype._util.hint.nonpep.utilhintnonpeptest import (
    die_unless_hint_nonpep,
    is_hint_nonpep,
)
from beartype._util.hint.pep.utilhintpeptest import (
    die_if_hint_pep_unsupported,
    is_hint_pep,
    is_hint_pep_supported,
)
from beartype._util.hint.data.utilhintdata import (
    HINT_BASES_FORWARDREF,
    HINTS_IGNORABLE_SHALLOW,
)
from typing import Type

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ VALIDATORS                        }....................
def die_unless_hint(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Annotated',
) -> None:
    '''
    Raise an exception unless the passed object is a **supported type hint**
    (i.e., object supported by the :func:`beartype.beartype` decorator as a
    valid type hint annotating callable parameters and return values).

    Specifically, this function raises an exception if this object is neither:

    * A **supported PEP-compliant type hint** (i.e., :mod:`beartype`-agnostic
      annotation compliant with annotation-centric PEPs currently supported
      by the :func:`beartype.beartype` decorator).
    * A **PEP-noncompliant type hint** (i.e., :mod:`beartype`-specific
      annotation intentionally *not* compliant with annotation-centric PEPs).

    Efficiency
    ----------
    This validator is effectively (but technically *not*) memoized. Since the
    passed ``hint_label`` parameter is typically unique to each call to this
    validator, memoizing this validator would uselessly consume excess space
    *without* improving time efficiency. Instead, this validator first calls
    the memoized :func:`is_hint_pep` tester. If that tester returns ``True``,
    this validator immediately returns ``True`` and is thus effectively
    memoized; else, this validator inefficiently raises a human-readable
    exception without memoization. Since efficiency is largely irrelevant in
    exception handling, this validator thus remains effectively memoized.

    Parameters
    ----------
    hint : object
        Object to be validated.
    hint_label : Optional[str]
        Human-readable label prefixing this object's representation in the
        exception message raised by this function. Defaults to ``"Annotated"``.

    Raises
    ----------
    BeartypeDecorHintPepUnsupportedException
        If this object is a PEP-compliant type hint currently unsupported by
        the :func:`beartype.beartype` decorator.
    BeartypeDecorHintNonPepException
        If this object is neither:

        * A PEP-noncompliant type hint.
        * A supported PEP-compliant type hint.
    '''

    # If this object is a supported type hint, reduce to a noop.
    if is_hint(hint):
        return
    # Else, this object is *NOT* a supported type hint. In this case,
    # subsequent logic raises an exception specific to the passed parameters.

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with is_hint() below.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # If this hint is PEP-compliant, raise an exception only if this hint is
    # currently unsupported by @beartype.
    if is_hint_pep(hint):
        die_if_hint_pep_unsupported(hint=hint, hint_label=hint_label)

    # Else, this hint is *NOT* PEP-compliant. In this case, raise an exception
    # only if this hint is also *NOT* PEP-noncompliant. By definition, all
    # PEP-noncompliant type hints are supported by @beartype.
    die_unless_hint_nonpep(hint=hint, hint_label=hint_label)

# ....................{ VALIDATORS ~ class                }....................
#FIXME: Unit test us up, please.
def die_unless_hint_type_isinstanceable(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Annotated',
    exception_cls: Type[Exception] = BeartypeDecorHintTypeException,
) -> None:
    '''
    Raise an exception unless the passed object is an **isinstanceable class**
    (i.e., class whose metaclass does *not* define an ``__instancecheck__()``
    dunder method that raises an exception).

    Classes that are *not* isinstanceable include most PEP-compliant type
    hints, notably:

    * **Generic aliases** (i.e., subscriptable classes overriding the
      ``__class_getitem__()`` class dunder method standardized by `PEP 560`_
      subscripted by an arbitrary object) under Python >= 3.9, whose
      metaclasses define an ``__instancecheck__()`` dunder method to
      unconditionally raise an exception. Generic aliases include:

      * `PEP 484`_-compliant **subscripted generics.**
      * `PEP 585`_-compliant type hints.

    * User-defined classes whose metaclasses define an ``__instancecheck__()``
      dunder method to unconditionally raise an exception, including:

      * `PEP 544`_-compliant protocols *not* decorated by the
        :func:`typing.runtime_checkable` decorator.

    Motivation
    ----------
    When a class whose metaclass defines an ``__instancecheck__()`` dunder
    method is passed as the second parameter to the :func:`isinstance` builtin,
    that builtin defers to that method rather than testing whether the first
    parameter passed to that builtin is an instance of that class. If that
    method raises an exception, that builtin raises the same exception,
    preventing callers from deciding whether arbitrary objects are instances
    of that class. For brevity, we refer to that class as "non-isinstanceable."

    Most classes are isinstanceable, because deciding whether arbitrary objects
    are instances of those classes is a core prerequisite for object-oriented
    programming. Most classes that are also PEP-compliant type hints, however,
    are *not* isinstanceable, because they're *never* intended to be
    instantiated into objects (and typically prohibit instantiation in various
    ways); they're only intended to be referenced as type hints annotating
    callables, an arguably crude form of callable markup.

    :mod:`beartype`-decorated callables typically check the types of arbitrary
    objects at runtime by passing those objects and types as the first and
    second parameters to the :func:`isinstance` builtin. If those types are
    non-isinstanceable, those type-checks will typically raise
    non-human-readable exceptions (e.g., ``"TypeError: isinstance() argument 2
    cannot be a parameterized generic"`` for `PEP 585`_-compliant type hints).
    This is non-ideal both because those exceptions are non-human-readable
    *and* because those exceptions are raised at call rather than decoration
    time, where users expect the :mod:`beartype.beartype` decorator to raise
    exceptions for erroneous type hints.

    Thus the existence of this function, which the :mod:`beartype.beartype`
    decorator calls to validate the usability of type hints that are classes
    *before* checking objects against those classes at call time.

    Parameters
    ----------
    hint : object
        Object to be validated.
    hint_label : str
        Human-readable label prefixing this hint's representation in the
        exception message raised by this function. Defaults to ``"Annotated"``.
    exception_cls : Type[Exception]
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintTypeException`.

    Raises
    ----------
    BeartypeDecorHintTypeException
        If this hint is *not* an isinstanceable class.

    .. _PEP 544:
        https://www.python.org/dev/peps/pep-0544
    .. _PEP 585:
        https://www.python.org/dev/peps/pep-0585
    '''

    # # Avoid circular import dependencies.
    # from beartype._util.hint.pep.proposal.utilhintpep544 import (
    #     is_hint_pep544_protocol)

    # If this hint is *NOT* a class, raise an exception.
    die_unless_type(cls=hint, exception_cls=exception_cls)
    # Else, this hint is a class.

    # If this class is *NOT* isinstanceable, raise an exception. For
    # efficiency, this test is split into two passes (in order of decreasing
    # efficiency):
    #
    # 1. Test whether this class is isinstanceable with the memoized
    #    is_type_isinstanceable() tester. This is crucial, as this test can
    #    *ONLY* be implemented via inefficient EAFP-style exception handling.
    # 2. If that tester reports this class to be non-isinstanceable, raise a
    #    human-readable exception chained onto the non-human-readable exception
    #    raised by explicitly passing that class as the second parameter to the
    #    isinstance() builtin.
    if not is_type_isinstanceable(hint):
        assert isinstance(exception_cls, type), (
            'f{repr(exception_cls)} not exception class.')

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize with the is_type_isinstanceable() tester.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        try:
            isinstance(None, hint)  # type: ignore[arg-type]
        except Exception as exception:
            #FIXME: Uncomment after we uncover why doing so triggers an
            #infinite circular exception chain when "hint" is a "GenericAlias".
            # # Human-readable exception message to be raised as either...
            # exception_message = (
            #     # If this class is a PEP 544-compliant protocol, a message
            #     # documenting this exact issue and how to resolve it;
            #     (
            #         f'{hint_label} PEP 544 protocol {hint} '
            #         f'uncheckable at runtime (i.e., '
            #         f'not decorated by @typing.runtime_checkable).'
            #     )
            #     if is_hint_pep544_protocol(hint) else
            #     # Else, a fallback message documenting this general issue.
            #     (
            #         f'{hint_label} type {hint} uncheckable at runtime (i.e., '
            #         f'not passable as second parameter to isinstance() '
            #         f'due to raising "{exception}" from metaclass '
            #         f'__instancecheck__() method).'
            #     )
            # )

            # Human-readable exception message to be raised.
            exception_message = (
                f'{hint_label} type {hint} uncheckable at runtime (i.e., '
                f'not passable as second parameter to isinstance() '
                f'due to raising "{exception}" from metaclass '
                f'__instancecheck__() method).'
            )

            # Raise this high-level exception with this human-readable message
            # chained onto this low-level exception with a typically
            # non-human-readable message.
            raise exception_cls(exception_message) from exception

# ....................{ VALIDATORS ~ forwardref           }....................
def die_unless_hint_forwardref(hint: object) -> None:
    '''
    Raise an exception unless the passed object is a **forward reference type
    hint** (i.e., object indirectly referring to a user-defined class that
    typically has yet to be defined).

    Parameters
    ----------
    hint : object
        Object to be validated.

    Raises
    ----------
    BeartypeDecorHintForwardRefException
        If this object is *not* a forward reference type hint.
    '''

    # If this is *NOT* a forward reference type hint, raise an exception.
    if not is_hint_forwardref(hint):
        raise BeartypeDecorHintForwardRefException(
            f'Type hint {repr(hint)} not forward reference.')

# ....................{ TESTERS                           }....................
@callable_cached
def is_hint(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a **supported type hint** (i.e.,
    object supported by the :func:`beartype.beartype` decorator as a valid type
    hint annotating callable parameters and return values).

    This tester function is memoized for efficiency.

    Parameters
    ----------
    hint : object
        Object to be validated.

    Returns
    ----------
    bool
        ``True`` only if this object is either:

        * A **PEP-compliant type hint** (i.e., :mod:`beartype`-agnostic
          annotation compliant with annotation-centric PEPs).
        * A **PEP-noncompliant type hint** (i.e., :mod:`beartype`-specific
          annotation intentionally *not* compliant with annotation-centric
          PEPs).

    Raises
    ----------
    TypeError
        If this object is **unhashable** (i.e., *not* hashable by the builtin
        :func:`hash` function and thus unusable in hash-based containers like
        dictionaries and sets). All supported type hints are hashable.
    '''

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with die_unless_hint() above.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Return true only if...
    return (
        # This is a PEP-compliant type hint supported by @beartype *OR*...
        is_hint_pep_supported(hint) if is_hint_pep(hint) else
        # This is a PEP-noncompliant type hint, which by definition is
        # necessarily supported by @beartype.
        is_hint_nonpep(hint)
    )

# ....................{ TESTERS ~ ignorable               }....................
@callable_cached
def is_hint_ignorable(hint: object) -> bool:
    '''
    ``True`` only if the passed object is an **ignorable type hint.**

    This tester function is memoized for efficiency.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is an ignorable type hint.

    Raises
    ----------
    TypeError
        If this object is **unhashable** (i.e., *not* hashable by the builtin
        :func:`hash` function and thus unusable in hash-based containers like
        dictionaries and sets). All supported type hints are hashable.
    '''

    # Attempt to...
    try:
        # If this hint is shallowly ignorable, return true.
        if hint in HINTS_IGNORABLE_SHALLOW:
            return True
        # Else, this hint is *NOT* shallowly ignorable.
    # If this hint is unhashable, hint is *NOT* shallowly ignorable.
    except TypeError:
        pass

    # If this hint is PEP-compliant...
    if is_hint_pep(hint):
        # Avoid circular import dependencies.
        from beartype._util.hint.pep.utilhintpeptest import (
            is_hint_pep_ignorable)

        # Defer to the function testing whether this hint is an ignorable
        # PEP-compliant type hint.
        return is_hint_pep_ignorable(hint)

    # Else, this hint is PEP-noncompliant and thus *NOT* deeply ignorable.
    # Since this hint is also *NOT* shallowly ignorable, this hint is
    # unignorable. In this case, return false.
    return False

# ....................{ TESTERS ~ forwardref              }....................
def is_hint_forwardref(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a **forward reference type hint**
    (i.e., object indirectly referring to a user-defined class that typically
    has yet to be defined).

    Specifically, this tester returns ``True`` only if this object is either:

    * A string whose value is the syntactically valid name of a class.
    * An instance of the :class:`typing.ForwardRef` class. The :mod:`typing`
      module implicitly replaces all strings subscripting :mod:`typing` objects
      (e.g., the ``MuhType`` in ``List['MuhType']``) with
      :class:`typing.ForwardRef` instances containing those strings as instance
      variables, for nebulous reasons that make little justifiable sense but
      what you gonna do 'cause this is 2020. *Fight me.*

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
        ``True`` only if this object is a forward reference type hint.
    '''

    # Return true only if this hint is an instance of a PEP-compliant forward
    # reference superclass.
    return isinstance(hint, HINT_BASES_FORWARDREF)
