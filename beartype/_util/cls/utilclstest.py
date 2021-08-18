#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **unmemoized class tester** (i.e., unmemoized and thus efficient
callable testing various properties of arbitrary classes) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import (
    BeartypeDecorHintPep3119Exception,
    _BeartypeUtilTypeException,
)
from beartype._data.cls.datacls import TYPES_BUILTIN_FAKE
from beartype._data.mod.datamod import BUILTINS_MODULE_NAME
from typing import Type

# ....................{ VALIDATORS                        }....................
def die_unless_type(
    # Mandatory parameters.
    cls: object,

    # Optional parameters.
    exception_cls: Type[Exception] = _BeartypeUtilTypeException,
) -> None:
    '''
    Raise an exception unless the passed object is a class.

    Parameters
    ----------
    cls : object
        Object to be validated.
    exception_cls : Type[Exception]
        Type of exception to be raised. Defaults to
        :exc:`_BeartypeUtilTypeException`.

    Raises
    ----------
    exception_cls
        If this object is *not* a class.
    '''

    # If this object is *NOT* a class, raise an exception.
    if not isinstance(cls, type):
        assert isinstance(exception_cls, type), (
            'f{repr(exception_cls)} not exception class.')
        raise exception_cls(f'{repr(cls)} not class.')

# ....................{ VALIDATORS ~ class                }....................
#FIXME: Unit test us up, please.
def die_unless_type_isinstanceable(
    # Mandatory parameters.
    cls: type,

    # Optional parameters.
    cls_label: str = 'Annotated',
    exception_cls: Type[Exception] = BeartypeDecorHintPep3119Exception,
) -> None:
    '''
    Raise an exception unless the passed object is an **isinstanceable class**
    (i.e., class whose metaclass does *not* define an ``__instancecheck__()``
    dunder method that raises an exception).

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
    cls : type
        Class to be validated.
    cls_label : str
        Human-readable label prefixing the representation of this class in the
        exception message raised by this function. Defaults to ``"Annotated"``.
    exception_cls : Type[Exception]
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep3119Exception`.

    Raises
    ----------
    BeartypeDecorHintPep3119Exception
        If this hint is *not* an isinstanceable class.
    '''

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
        assert isinstance(exception_cls, type), (
            'f{repr(exception_cls)} not exception class.')

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

# ....................{ TESTERS ~ builtin                 }....................
def is_type_builtin(cls: type) -> bool:
    '''
    ``True`` only if the passed class is **builtin** (i.e., globally accessible
    C-based type requiring *no* explicit importation).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    cls : type
        Class to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this class is builtin.

    Raises
    ----------
    _BeartypeUtilTypeException
        If this object is *not* a class.
    '''

    # Avoid circular import dependencies.
    from beartype._util.mod.utilmodule import (
        get_object_type_module_name_or_none)

    # If this object is *NOT* a type, raise an exception.
    die_unless_type(cls)
    # Else, this object is a type.

    # If this type is a fake builtin (i.e., type that is *NOT* builtin but
    # erroneously masquerading as being builtin), this type is *NOT* a builtin.
    # In this case, silently reject this type.
    if cls in TYPES_BUILTIN_FAKE:
        return False
    # Else, this type is *NOT* a fake builtin.

    # Fully-qualified name of the module defining this type if this type is
    # defined by a module *OR* "None" otherwise (i.e., if this type is
    # dynamically defined in-memory).
    cls_module_name = get_object_type_module_name_or_none(cls)

    # This return true only if this name is that of the "builtins" module
    # declaring all builtin types.
    return cls_module_name == BUILTINS_MODULE_NAME

# ....................{ TESTERS ~ isinstanceable          }....................
def is_type_isinstanceable(cls: object) -> bool:
    '''
    ``True`` only if the passed type cls is an **isinstanceable class** (i.e.,
    class whose metaclass does *not* define an ``__instancecheck__()`` dunder
    method that raises an exception).

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
        isinstance(None, cls)

        # If the prior function call raised *NO* exception, this class is
        # probably but *NOT* necessarily isinstanceable.
        return True
    # If the prior function call raised an exception, this class is *NOT*
    # isinstanceable. In this case, return false.
    except:
        return False
