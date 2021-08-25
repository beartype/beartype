#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`3119`-compliant **class tester** (i.e., callable testing
various properties of arbitrary classes first standardized by :pep:`3119`)
utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep3119Exception
from typing import Type

# ....................{ VALIDATORS                        }....................
def die_unless_type_isinstanceable(
    # Mandatory parameters.
    cls: type,

    # Optional parameters.
    cls_label: str = 'Type hint',
    exception_cls: Type[Exception] = BeartypeDecorHintPep3119Exception,
) -> None:
    '''
    Raise an exception of the passed type unless the passed object is an
    **isinstanceable class** (i.e., class whose metaclass does *not* define an
    ``__instancecheck__()`` dunder method that raises an exception).

    Classes that are *not* isinstanceable include most PEP-compliant type
    hints, notably:

    * **Generic aliases** (i.e., subscriptable classes overriding the
      ``__class_getitem__()`` class dunder method standardized by :pep:`560`
      subscripted by an arbitrary object) under Python >= 3.9, whose
      metaclasses define an ``__instancecheck__()`` dunder method to
      unconditionally raise an exception. Generic aliases include:

      * :pep:`484`-compliant **subscripted generics.**
      * :pep:`585`-compliant type hints.

    * User-defined classes whose metaclasses define an ``__instancecheck__()``
      dunder method to unconditionally raise an exception, including:

      * :pep:`544`-compliant protocols *not* decorated by the
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
    cannot be a parameterized generic"`` for :pep:`585`-compliant type hints).
    This is non-ideal both because those exceptions are non-human-readable
    *and* because those exceptions are raised at call rather than decoration
    time, where users expect the :mod:`beartype.beartype` decorator to raise
    exceptions for erroneous type hints.

    Thus the existence of this function, which the :mod:`beartype.beartype`
    decorator calls to validate the usability of type hints that are classes
    *before* checking objects against those classes at call time.

    Parameters
    ----------
    cls : type
        Class to be validated.
    cls_label : str
        Human-readable label prefixing the representation of this class in the
        exception message raised by this function. Defaults to ``"Type hint"``.
    exception_cls : Type[Exception]
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep3119Exception`.

    Raises
    ----------
    BeartypeDecorHintPep3119Exception
        If this class is *not* isinstanceable.
    '''

    # Avoid circular import dependencies.
    from beartype._util.cls.utilclstest import die_unless_type

    # If this hint is *NOT* a class, raise an exception.
    die_unless_type(cls=cls, exception_cls=exception_cls)
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
    if not is_type_isinstanceable(cls):
        assert isinstance(cls_label, str), f'{repr(cls_label)} not string.'
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not exception class.')

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize with the is_type_isinstanceable() tester.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        try:
            isinstance(None, cls)  # type: ignore[arg-type]
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
                f'{cls_label} {repr(cls)} uncheckable at runtime (i.e., '
                f'not passable as second parameter to isinstance() '
                f'due to raising "{exception}" from metaclass '
                f'__instancecheck__() method).'
            )

            # Raise this high-level exception with this human-readable message
            # chained onto this low-level exception with a typically
            # non-human-readable message.
            raise exception_cls(exception_message) from exception


def die_unless_type_issubclassable(
    # Mandatory parameters.
    cls: type,

    # Optional parameters.
    cls_label: str = 'Type hint',
    exception_cls: Type[Exception] = BeartypeDecorHintPep3119Exception,
) -> None:
    '''
    Raise an exception of the passed type unless the passed object is an
    **issubclassable class** (i.e., class whose metaclass does *not* define a
    ``__subclasscheck__()`` dunder method that raises an exception).

    Classes that are *not* issubclassable include most PEP-compliant type
    hints, notably:

    * **Generic aliases** (i.e., subscriptable classes overriding the
      ``__class_getitem__()`` class dunder method standardized by :pep:`560`
      subscripted by an arbitrary object) under Python >= 3.9, whose
      metaclasses define an ``__subclasscheck__()`` dunder method to
      unconditionally raise an exception. Generic aliases include:

      * :pep:`484`-compliant **subscripted generics.**
      * :pep:`585`-compliant type hints.

    * User-defined classes whose metaclasses define a ``__subclasscheck__()``
      dunder method to unconditionally raise an exception, including:

      * :pep:`544`-compliant protocols *not* decorated by the
        :func:`typing.runtime_checkable` decorator.

    Motivation
    ----------
    When a class whose metaclass defines a ``__subclasscheck__()`` dunder
    method is passed as the second parameter to the :func:`issubclass` builtin,
    that builtin defers to that method rather than testing whether the first
    parameter passed to that builtin is an subclass of that class. If that
    method raises an exception, that builtin raises the same exception,
    preventing callers from deciding whether arbitrary objects are subclasses
    of that class. For brevity, we refer to that class as "non-issubclassable."

    Most classes are issubclassable, because deciding whether arbitrary classes
    are subclasses of those classes is a core prerequisite for object-oriented
    programming. Most classes that are also PEP-compliant type hints, however,
    are *not* issubclassable, because they're *never* intended to be
    instantiated into objects (and typically prohibit instantiation in various
    ways); they're only intended to be referenced as type hints annotating
    callables, an arguably crude form of callable markup.

    :mod:`beartype`-decorated callables typically check the superclasses of
    arbitrary classes at runtime by passing those classes and superclasses as
    the first and second parameters to the :func:`issubclass` builtin. If those
    types are non-issubclassable, those type-checks will typically raise
    non-human-readable exceptions (e.g., ``"TypeError: issubclass() argument 2
    cannot be a parameterized generic"`` for :pep:`585`-compliant type hints).
    This is non-ideal both because those exceptions are non-human-readable
    *and* because those exceptions are raised at call rather than decoration
    time, where users expect the :mod:`beartype.beartype` decorator to raise
    exceptions for erroneous type hints.

    Thus the existence of this function, which the :mod:`beartype.beartype`
    decorator calls to validate the usability of type hints that are classes
    *before* checking objects against those classes at call time.

    Parameters
    ----------
    cls : type
        Class to be validated.
    cls_label : str
        Human-readable label prefixing the representation of this class in the
        exception message raised by this function. Defaults to ``"Type hint"``.
    exception_cls : Type[Exception]
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep3119Exception`.

    Raises
    ----------
    BeartypeDecorHintPep3119Exception
        If this class is *not* issubclassable.
    '''

    # Avoid circular import dependencies.
    from beartype._util.cls.utilclstest import die_unless_type

    # If this hint is *NOT* a class, raise an exception.
    die_unless_type(cls=cls, exception_cls=exception_cls)
    # Else, this hint is a class.

    # If this class is *NOT* issubclassable, raise an exception. For
    # efficiency, this test is split into two passes (in order of decreasing
    # efficiency):
    #
    # 1. Test whether this class is issubclassable with the memoized
    #    is_type_issubclassable() tester. This is crucial, as this test can
    #    *ONLY* be implemented via inefficient EAFP-style exception handling.
    # 2. If that tester reports this class to be non-issubclassable, raise a
    #    human-readable exception chained onto the non-human-readable exception
    #    raised by explicitly passing that class as the second parameter to the
    #    issubclass() builtin.
    if not is_type_issubclassable(cls):
        assert isinstance(cls_label, str), f'{repr(cls_label)} not string.'
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not exception class.')

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize with the is_type_issubclassable() tester.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        try:
            issubclass(type, cls)  # type: ignore[arg-type]
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
            #         f'not passable as second parameter to issubclass() '
            #         f'due to raising "{exception}" from metaclass '
            #         f'__subclasscheck__() method).'
            #     )
            # )

            # Human-readable exception message to be raised.
            exception_message = (
                f'{cls_label} {repr(cls)} uncheckable at runtime (i.e., '
                f'not passable as second parameter to issubclass() '
                f'due to raising "{exception}" from metaclass '
                f'__subclasscheck__() method).'
            )

            # Raise this high-level exception with this human-readable message
            # chained onto this low-level exception with a typically
            # non-human-readable message.
            raise exception_cls(exception_message) from exception

# ....................{ TESTERS                           }....................
def is_type_isinstanceable(cls: object) -> bool:
    '''
    ``True`` only if the passed type is **isinstanceable** (i.e., class whose
    metaclass does *not* define an ``__instancecheck__()`` dunder method that
    raises an exception).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator). Although the implementation does *not*
    trivially reduce to an efficient one-liner, the inefficient branch of this
    implementation *only* applies to erroneous edge cases resulting in raised
    exceptions and is thus largely ignorable.

    Caveats
    ----------
    **This tester may return false positives in unlikely edge cases.**
    Internally, this tester tests whether this class is isinstanceable by
    detecting whether passing the ``None`` singleton and this class to the
    :func:`isinstance` builtin raises an exception. If that call raises *no*
    exception, this class is probably but *not* necessarily isinstanceable.
    Since the metaclass of this class could define an ``__instancecheck__()``
    dunder method to conditionally raise exceptions except when passed the
    ``None`` singleton, there exists *no* means of ascertaining whether a class
    is fully isinstanceable in the general case. Since most classes that are
    *not* isinstanceable are unconditionally isinstanceable (i.e., the
    metaclasses of those classes define an ``__instancecheck__()`` dunder
    method to unconditionally raise exceptions), this distinction is generally
    meaningless in the real world. This test thus generally suffices.

    Parameters
    ----------
    cls : object
        Object to be tested.

    Returns
    ----------
    bool
        ``True`` only if this object is an isinstanceable class.

    See Also
    ----------
    :func:`die_unless_type_isinstanceable`
        Further details.
    '''

    # If this object is *NOT* a class, return false.
    if not isinstance(cls, type):
        return False

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize with die_unless_type_isinstanceable().
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Attempt to pass this class as the second parameter to the isinstance()
    # builtin to decide whether or not this class is safely usable as a
    # standard class or not.
    #
    # Note that this leverages an EAFP (i.e., "It is easier to ask forgiveness
    # than permission") approach and thus imposes a minor performance penalty,
    # but that there exists *NO* faster alternative applicable to arbitrary
    # user-defined classes, whose metaclasses may define an __instancecheck__()
    # dunder method to raise exceptions and thus prohibit being passed as the
    # second parameter to the isinstance() builtin, the primary means employed
    # by @beartype wrapper functions to check arbitrary types.
    try:
        isinstance(None, cls)  # type: ignore[arg-type]

        # If the prior function call raised *NO* exception, this class is
        # probably but *NOT* necessarily isinstanceable.
        return True
    # If the prior function call raised an exception, this class is *NOT*
    # isinstanceable. In this case, return false.
    except:
        return False


def is_type_issubclassable(cls: object) -> bool:
    '''
    ``True`` only if the passed type is **issubclassable** (i.e., class whose
    metaclass does *not* define a ``__subclasscheck__()`` dunder method that
    raises an exception).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator). Although the implementation does *not*
    trivially reduce to an efficient one-liner, the inefficient branch of this
    implementation *only* applies to erroneous edge cases resulting in raised
    exceptions and is thus largely ignorable.

    Caveats
    ----------
    **This tester may return false positives in unlikely edge cases.**
    Internally, this tester tests whether this class is issubclassable by
    detecting whether passing the :class:`type` superclass and this class to
    the :func:`issubclass` builtin raises an exception. If that call raises
    *no* exception, this class is probably but *not* necessarily
    issubclassable. Since the metaclass of this class could define a
    ``__subclasscheck__()`` dunder method to conditionally raise exceptions
    except when passed the :class:`type` superclass, there exists *no* means of
    ascertaining whether a class is fully issubclassable in the general case.
    Since most classes that are *not* issubclassable are unconditionally
    issubclassable (i.e., the metaclasses of those classes define an
    ``__subclasscheck__()`` dunder method to unconditionally raise exceptions),
    this distinction is generally meaningless in the real world. This test thus
    generally suffices.

    Parameters
    ----------
    cls : object
        Object to be tested.

    Returns
    ----------
    bool
        ``True`` only if this object is an issubclassable class.

    See Also
    ----------
    :func:`die_unless_type_issubclassable`
        Further details.
    '''

    # If this object is *NOT* a class, return false.
    if not isinstance(cls, type):
        return False

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize with die_unless_type_issubclassable().
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Attempt to pass this class as the second parameter to the issubclass()
    # builtin to decide whether or not this class is safely usable as a
    # standard class or not.
    #
    # Note that this leverages an EAFP (i.e., "It is easier to ask forgiveness
    # than permission") approach and thus imposes a minor performance penalty,
    # but that there exists *NO* faster alternative applicable to arbitrary
    # user-defined classes, whose metaclasses may define a __subclasscheck__()
    # dunder method to raise exceptions and thus prohibit being passed as the
    # second parameter to the issubclass() builtin, the primary means employed
    # by @beartype wrapper functions to check arbitrary types.
    try:
        issubclass(type, cls)  # type: ignore[arg-type]

        # If the prior function call raised *NO* exception, this class is
        # probably but *NOT* necessarily issubclassable.
        return True
    # If the prior function call raised an exception, this class is *NOT*
    # issubclassable. In this case, return false.
    except:
        return False
