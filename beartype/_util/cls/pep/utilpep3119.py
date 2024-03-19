#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`3119`-compliant **class detectors** (i.e., callables
validating and testing various properties of arbitrary classes standardized by
:pep:`3119`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep3119Exception
from beartype.typing import Callable
from beartype._data.hint.datahinttyping import (
    TypeException,
    TypeOrTupleTypes,
)

# ....................{ RAISERS ~ instance                 }....................
def die_unless_object_isinstanceable(
    # Mandatory parameters.
    obj: TypeOrTupleTypes,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep3119Exception,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception of the passed type unless the passed object is
    **isinstanceable** (i.e., valid as the second parameter to the
    :func:`isinstance` builtin).

    Specifically, this function raises an exception unless this object is
    either:

    * An **isinstanceable class** (i.e., class whose metaclass does *not* define
      an ``__instancecheck__()`` dunder method that raises a :exc:`TypeError`
      exception).
    * Tuple of one or more isinstanceable classes.
    * A :pep:`604`-compliant **new union** (i.e., objects created by expressions
      of the form ``{type1} | {type2} | ... | {typeN}``) under Python >= 3.10.
      By definition, *all* new unions are isinstanceable.

    Parameters
    ----------
    obj : object
        Object to be validated.
    exception_cls : TypeException, optional
        Type of exception to be raised. Defaults to
        :exc:`.BeartypeDecorHintPep3119Exception`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ------
    BeartypeDecorHintPep3119Exception
        If this object is neither:

        * An isinstanceable class.
        * A tuple containing only isinstanceable classes.
        * A :pep:`604`-compliant new union.
    '''

    # Defer to this lower-level general-purpose raiser.
    _die_if_object_uncheckable(
        obj=obj,
        obj_pith=None,
        obj_raiser=die_unless_type_isinstanceable,
        obj_tester=isinstance,  # type: ignore[arg-type]
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )


def die_unless_type_isinstanceable(
    # Mandatory parameters.
    cls: type,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep3119Exception,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception of the passed type unless the passed object is an
    **isinstanceable class** (i.e., class whose metaclass does *not* define an
    ``__instancecheck__()`` dunder method that raises a :exc:`TypeError`
    exception).

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
    This is non-ideal both because those exceptions are non-human-readable *and*
    because those exceptions are raised at call rather than decoration time,
    where users expect the :func:`beartype.beartype` decorator to raise
    exceptions for erroneous type hints.

    Thus the existence of this function, which the :func:`beartype.beartype`
    decorator calls to validate the usability of type hints that are classes
    *before* checking objects against those classes at call time.

    Caveats
    -------
    **This function considers all classes whose metaclasses define
    ``__instancecheck__()`` dunder methods that raise exceptions other than**
    :exc:`TypeError` **to be isinstanceable.** This function *only* considers
    classes whose metaclasses define ``__instancecheck__()`` dunder methods that
    raise :exc:`TypeError` exceptions to be non-isinstanceable; all other
    classes are isinstanceable.

    Ideally, this function would consider any class whose metaclass defines an
    ``__instancecheck__()`` dunder method that raises any exception (rather than
    merely a :exc:`TypeError` exception) to be non-isinstanceable.
    Pragmatically, doing so would raise false positives in common edge cases --
    and previously did so, in fact, which is why we no longer do so.

    In particular, the metaclass of the passed class may *not* necessarily be
    fully initialized at the early time that this function is called (typically,
    at :func:`beartype.beartype` decoration time). If this is the case, then
    eagerly passing that class to :func:`isinstance` is likely to raise an
    exception. For example, doing so raises an :exc:`AttributeError` when the
    ``__instancecheck__()`` dunder method defined by that metaclass references
    an external attribute that has yet to be defined:

    .. code-block:: python

       from beartype import beartype

       class MetaFoo(type):
           def __instancecheck__(cls, other):
               return g()

       class Foo(metaclass=MetaFoo):
           pass

       # @beartype transitively calls this function to validate that "Foo" is
       # isinstanceable. However, since g() has yet to be defined at this time,
       # doing so raises an "AttributeError" exception despite this logic
       # otherwise being sound.
       @beartype
       def f(x: Foo):
           pass

       def g():
           return True

    This function thus constrains itself to merely the :exc:`TypeError`
    exception, which all non-isinstanceable classes defined by the standard
    :mod:`typing` module unconditionally raise. This suggests that there is
    currently an unambiguous one-to-one mapping between non-isinstanceable
    classes and classes whose metaclass ``__instancecheck__()`` dunder methods
    raise :exc:`TypeError` exceptions. May this mapping hold true forever!

    Parameters
    ----------
    cls : object
        Object to be validated.
    exception_cls : TypeException, optional
        Type of exception to be raised. Defaults to
        :exc:`.BeartypeDecorHintPep3119Exception`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ------
    BeartypeDecorHintPep3119Exception
        If this object is *not* an isinstanceable class.

    See Also
    --------
    :func:`.die_unless_type_isinstanceable`
        Further details.
    '''

    # Avoid circular import dependencies.
    from beartype._util.cls.utilclstest import die_unless_type

    # If this object is *NOT* a class, raise an exception.
    die_unless_type(
        cls=cls,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # Else, this object is a class.

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize with the is_type_isinstanceable() tester.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Attempt to pass this class as the second parameter to isinstance().
    try:
        isinstance(None, cls)  # type: ignore[arg-type]
    # If doing so raised a "TypeError" exception, this class is *NOT*
    # isinstanceable. In this case, raise a human-readable exception.
    #
    # See the docstring for further discussion.
    except TypeError as exception:
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not exception class.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        #FIXME: Uncomment after we uncover why doing so triggers an
        #infinite circular exception chain when "hint" is a "GenericAlias".
        #It's clearly the is_hint_pep544_protocol() call, but why? In any
        #case, the simplest workaround would just be to inline the logic of
        #is_hint_pep544_protocol() here directly. Yes, we know. *shrug*

        # # Human-readable exception message to be raised as either...
        # exception_message = (
        #     # If this class is a PEP 544-compliant protocol, a message
        #     # documenting this exact issue and how to resolve it;
        #     (
        #         f'{exception_prefix}PEP 544 protocol {hint} '
        #         f'uncheckable at runtime (i.e., '
        #         f'not decorated by @typing.runtime_checkable).'
        #     )
        #     if is_hint_pep544_protocol(hint) else
        #     # Else, a fallback message documenting this general issue.
        #     (
        #         f'{exception_prefix}type {hint} uncheckable at runtime (i.e., '
        #         f'not passable as second parameter to isinstance() '
        #         f'due to raising "{exception}" from metaclass '
        #         f'__instancecheck__() method).'
        #     )
        # )

        # Exception message to be raised.
        exception_message = (
            f'{exception_prefix}{repr(cls)} uncheckable at runtime '
            f'(i.e., not passable as second parameter to isinstance(), '
            f'due to raising "{exception.__class__.__name__}: {exception}" '
            f'from metaclass __instancecheck__() method).'
        )

        # Raise this exception chained onto this lower-level exception.
        raise exception_cls(exception_message) from exception
    # If doing so raised any exception *OTHER* than a "TypeError" exception,
    # this class may or may not be isinstanceable. Since we have no means of
    # differentiating the two, we err on the side of caution. Avoid returning a
    # false negative by quietly ignoring this exception.
    except Exception:
        pass

# ....................{ RAISERS ~ subclass                 }....................
def die_unless_object_issubclassable(
    # Mandatory parameters.
    obj: TypeOrTupleTypes,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep3119Exception,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception of the passed type unless the passed object is
    **issubclassable** (i.e., valid as the second parameter to the
    :func:`issubclass` builtin).

    Specifically, this function raises an exception unless this object is
    either:

    * An **issubclassable class** (i.e., class whose metaclass does *not* define
      an ``__subclasscheck__()`` dunder method that raises a :exc:`TypeError`
      exception).
    * Tuple of one or more issubclassable classes.
    * A :pep:`604`-compliant **new union** (i.e., objects created by expressions
      of the form ``{type1} | {type2} | ... | {typeN}``) under Python >= 3.10.
      By definition, *all* new unions are issubclassable.

    Parameters
    ----------
    obj : object
        Object to be validated.
    exception_cls : TypeException, optional
        Type of exception to be raised. Defaults to
        :exc:`.BeartypeDecorHintPep3119Exception`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ------
    BeartypeDecorHintPep3119Exception
        If this object is neither:

        * An issubclassable class.
        * A tuple containing only issubclassable classes.
        * A :pep:`604`-compliant new union.
    '''

    # Defer to this lower-level general-purpose raiser.
    _die_if_object_uncheckable(
        obj=obj,
        obj_pith=type,
        obj_raiser=die_unless_type_issubclassable,
        obj_tester=issubclass,  # type: ignore[arg-type]
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )


def die_unless_type_issubclassable(
    # Mandatory parameters.
    cls: type,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep3119Exception,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception of the passed type unless the passed object is an
    **issubclassable class** (i.e., class whose metaclass does *not* define a
    ``__subclasscheck__()`` dunder method that raise a :exc:`TypeError`
    exception).

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
    See also the "Motivation" and "Caveats" sections of the
    :func:`die_unless_type_isinstanceable` docstring for further discussion,
    substituting:

    * ``__instancecheck__()`` for ``__subclasscheck__()``.
    * :func:`isinstance` for :func:`issubclass`.

    Parameters
    ----------
    cls : object
        Object to be validated.
    exception_cls : TypeException, optional
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep3119Exception`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ------
    BeartypeDecorHintPep3119Exception
        If this object is *not* an issubclassable class.
    '''

    # Avoid circular import dependencies.
    from beartype._util.cls.utilclstest import die_unless_type

    # If this hint is *NOT* a class, raise an exception.
    die_unless_type(
        cls=cls,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # Else, this hint is a class.

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize with the is_type_issubclassable() tester.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Attempt to pass this class as the second parameter to issubclass().
    try:
        issubclass(type, cls)  # type: ignore[arg-type]
    # If doing so raised a "TypeError" exception, this class is *NOT*
    # issubclassable. In this case, raise a human-readable exception.
    #
    # See the die_unless_type_isinstanceable() docstring for details.
    except TypeError as exception:
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not exception class.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Exception message to be raised.
        exception_message = (
            f'{exception_prefix}{repr(cls)} uncheckable at runtime '
            f'(i.e., not passable as second parameter to issubclass(), '
            f'due to raising "{exception.__class__.__name__}: {exception}" '
            f'from metaclass __subclasscheck__() method).'
        )

        # Raise this exception chained onto this lower-level exception.
        raise exception_cls(exception_message) from exception
    # If doing so raised any exception *OTHER* than a "TypeError" exception,
    # this class may or may not be issubclassable. Since we have no means of
    # differentiating the two, we err on the side of caution. Avoid returning a
    # false negative by quietly ignoring this exception.
    except Exception:
        pass

# ....................{ TESTERS                            }....................
def is_type_isinstanceable(cls: object) -> bool:
    '''
    :data:`True` only if the passed object is an **isinstanceable class** (i.e.,
    class whose metaclass does *not* define an ``__instancecheck__()`` dunder
    method that raises a :exc:`TypeError` exception).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator). Although the implementation does *not*
    trivially reduce to an efficient one-liner, the inefficient branch of this
    implementation *only* applies to erroneous edge cases resulting in raised
    exceptions and is thus largely ignorable.

    Caveats
    -------
    **This tester may return false positives in unlikely edge cases.**
    Internally, this tester tests whether this class is isinstanceable by
    detecting whether passing the :data:`None` singleton and this class to the
    :func:`isinstance` builtin raises a :exc:`TypeError` exception. If that call
    raises *no* exception, this class is probably but *not* necessarily
    isinstanceable. Since the metaclass of this class could define an
    ``__instancecheck__()`` dunder method to conditionally raise exceptions
    *except* when passed the :data:`None` singleton, there exists *no* perfect
    means of deciding whether an arbitrary class is fully isinstanceable in the
    general sense. Since most classes that are *not* isinstanceable are
    unconditionally isinstanceable (i.e., the metaclasses of those classes
    define an ``__instancecheck__()`` dunder method to unconditionally raise
    exceptions), this distinction is generally meaningless in the real world.
    This test thus generally suffices.

    Parameters
    ----------
    cls : object
        Object to be tested.

    Returns
    -------
    bool
        :data:`True` only if this object is an isinstanceable class.

    See Also
    --------
    :func:`.die_unless_type_isinstanceable`
        Further details.
    '''

    # If this object is *NOT* a class, immediately return false.
    if not isinstance(cls, type):
        return False
    # Else, this object is a class.

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize with die_unless_type_isinstanceable().
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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
        # probably but *NOT* necessarily isinstanceable. Return true.
    # If the prior function call raised a "TypeError" exception, this class is
    # *NOT* isinstanceable. In this case, return false.
    except TypeError:
        return False
    # If the prior function call raised any exception *OTHER* than a "TypeError"
    # exception, this class may or may not be isinstanceable. Since we have no
    # means of differentiating the two, we err on the side of caution. Avoid
    # returning a false negative by safely returning true.
    except Exception:
        return True

    # Look. Just do it. *sigh*
    return True


def is_type_issubclassable(cls: object) -> bool:
    '''
    :data:`True` only if the passed object is either an **issubclassable class**
    (i.e., class whose metaclass does *not* define a ``__subclasscheck__()``
    dunder method that raises a :exc:`TypeError` exception) *or* tuple
    containing only issubclassable classes.

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator). Although the implementation does *not*
    trivially reduce to an efficient one-liner, the inefficient branch of this
    implementation *only* applies to erroneous edge cases resulting in raised
    exceptions and is thus largely ignorable.

    Caveats
    -------
    See also the "Caveats" sections of the
    :func:`.is_type_isinstanceable` docstring for further discussion,
    substituting:

    * ``__instancecheck__()`` for ``__subclasscheck__()``.
    * :func:`isinstance` for :func:`issubclass`.

    Parameters
    ----------
    cls : object
        Object to be tested.

    Returns
    -------
    bool
        :data:`True` only if this object is either:

        * An issubclassable class.
        * A tuple containing only issubclassable classes.

    See Also
    --------
    :func:`.die_unless_type_issubclassable`
        Further details.
    '''

    # If this object is *NOT* a class, immediately return false.
    if not isinstance(cls, type):
        return False
    # Else, this object is a class.

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
        # probably but *NOT* necessarily issubclassable. Return true.
    # If the prior function call raised a "TypeError" exception, this class is
    # *NOT* issubclassable. In this case, return false.
    except TypeError:
        return False
    # If the prior function call raised any exception *OTHER* than a "TypeError"
    # exception, this class may or may not be issubclassable. Since we have no
    # means of differentiating the two, we err on the side of caution. Avoid
    # returning a false negative by safely returning true.
    except Exception:
        pass

    # Look. Just do it. *sigh*
    return True

# ....................{ PRIVATE ~ raisers                  }....................
def _die_if_object_uncheckable(
    obj: TypeOrTupleTypes,
    obj_pith: object,
    obj_raiser: Callable,
    obj_tester: Callable[[object, TypeOrTupleTypes], bool],
    exception_cls: TypeException,
    exception_prefix: str,
) -> None:
    '''
    Raise an exception of the passed type unless the passed object is
    **runtime-checkable** (i.e., valid as the second parameter to either the
    :func:`isinstance` or :func:`issubclass` builtins) according to the passed
    object tester and raiser.

    Parameters
    ----------
    obj : object
        Object to be validated.
    obj_pith : object
        Object guaranteed to satisfy the ``obj_tester`` callable when ``obj`` is
        runtime-typecheckable (i.e., when ``obj_tester`` is called as
        ``obj_tester(obj_pith, obj)``).
    obj_raiser : Callable
        Callable raising an exception unless this object is runtime-checkable
        according to this predicate, which should be either:

        * :func:`.die_unless_type_isinstanceable`.
        * :func:`.die_unless_type_issubclassable`.
    obj_tester : Callable[[object, TypeOrTupleTypes], bool]
        Callable returning :data:`True` only if this object is runtime-checkable
        according to this predicate, which should be either:

        * :func:`isinstance`.
        * :func:`issubclass`.
    exception_cls : TypeException
        Type of exception to be raised.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message.

    Raises
    ------
    BeartypeDecorHintPep3119Exception
        If this object is *not* runtime-checkable according to the passed
        object tester and raiser.
    '''
    assert callable(obj_raiser), f'{repr(obj_raiser)} uncallable.'
    assert callable(obj_tester), f'{repr(obj_tester)} uncallable.'

    # Avoid circular import dependencies.
    from beartype._util.cls.utilclstest import die_unless_type_or_types
    from beartype._util.hint.pep.proposal.utilpep604 import is_hint_pep604
    from beartype._util.hint.pep.utilpepget import get_hint_pep_args

    # If this object is *NOT* a PEP 604-compliant new union...
    if not is_hint_pep604(obj):
        # If this object is neither a class nor tuple of classes, raise an
        # exception.
        die_unless_type_or_types(
            type_or_types=obj,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )
        # Else, this object is either a class or tuple of classes.
    # Else, this object is a PEP 604-compliant new union. In either case, this
    # object now *COULD* be runtime-checkable. To decide whether this object is
    # actually instanceable, further introspection is needed.

    # If this object is a class...
    if isinstance(obj, type):
        # If this class is *NOT* runtime-checkable, raise an exception.
        obj_raiser(
            cls=obj,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )
        # Else, this class is runtime-checkable.
    # Else, this object *MUST* (by process of elimination and validation
    # above) be either a tuple of classes *OR* new union. In either case...
    else:
        # Attempt to pass this object as the second parameter to isinstance().
        try:
            obj_tester(obj_pith, obj)  # type: ignore[arg-type]
        # If doing so raises a "TypeError" exception, this object is *NOT*
        # runtime-checkable. In this case, raise a human-readable exception.
        #
        # See the die_unless_type_runtime-checkable() docstring for details.
        except TypeError as exception:
            assert isinstance(exception_cls, type), (
                f'{repr(exception_cls)} not exception class.')
            assert isinstance(exception_prefix, str), (
                f'{repr(exception_prefix)} not string.')

            # Tuple of all items of this iterable object.
            obj_items: tuple = None  # type: ignore[assignment]

            # Human-readable label describing this object in this exception
            # message.
            obj_label: str = None  # type: ignore[assignment]

            # Human-readable label describing the first non-runtime-checkable
            # item of this object in this exception message.
            obj_item_label: str = None  # type: ignore[assignment]

            # If this object is a tuple, define these locals accordingly.
            if isinstance(obj, tuple):
                obj_items = obj
                obj_label = 'tuple union'
                obj_item_label = 'tuple union item'
            # Else, this object is a new union. Define these locals accordingly.
            else:
                obj_items = get_hint_pep_args(obj)
                obj_label = 'PEP 604 new union'
                obj_item_label = 'new union child type'

            # Exception message to be raised.
            exception_message = (
                f'{exception_prefix} {obj_label} {repr(obj)} '
                f'uncheckable at runtime'
            )

            # For the 0-based index of each tuple class and that class...
            for cls_index, cls in enumerate(obj_items):
                # If this class is *NOT* runtime-checkable, raise an exception.
                obj_raiser(
                    cls=cls,
                    exception_cls=exception_cls,
                    exception_prefix=(
                        f'{exception_message}, as '
                        f'{obj_item_label} {cls_index} '
                    ),
                )
                # Else, this class is runtime-checkable. Continue to the next.

            # Raise this exception chained onto this lower-level exception.
            # Although this should *NEVER* happen (as we should have already
            # raised an exception above), we nonetheless do so for safety.
            raise exception_cls(f'{exception_message}.') from exception
        # If doing so raised any exception *OTHER* than a "TypeError" exception,
        # this class may or may not be runtime-checkable. Since we have no means
        # of differentiating the two, we err on the side of caution. Avoid
        # returning a false negative by quietly ignoring this exception.
        except Exception:
            pass
