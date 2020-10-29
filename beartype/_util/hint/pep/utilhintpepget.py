#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint getter utilities** (i.e., callables querying
arbitrary objects for attributes specific to PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
import typing
from beartype.roar import BeartypeDecorHintPepException
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.data.pep.utilhintdatapep import (
    HINT_PEP_SIGNS_TYPE_ORIGIN)
from typing import Generic, TypeVar

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS ~ tuple                   }....................
def get_hint_pep_args(hint: object) -> tuple:
    '''
    Tuple of all **typing arguments** (i.e., subscripted objects of the passed
    PEP-compliant type hint listed by the caller at hint declaration time)
    if any *or* the empty tuple otherwise.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This function should always be called in lieu of attempting to directly
    access the low-level** ``__args__`` **dunder attribute.** Various
    singleton objects defined by the :mod:`typing` module (e.g.,
    :attr:`typing.Any`, :attr:`typing.NoReturn`) fail to define this attribute,
    guaranteeing :class:`AttributeError` exceptions from all general-purpose
    logic attempting to directly access this attribute. Thus this function,
    which "fills in the gaps" by implementing this oversight.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    tuple
        Either:

        * If this object defines an ``__args__`` dunder attribute, the value of
          that attribute.
        * Else, the empty tuple.

    Examples
    ----------
        >>> import typing
        >>> from beartype._util.hint.pep.utilhintpepget import (
        ...     get_hint_pep_args)
        >>> get_hint_pep_args(typing.Any)
        ()
        >>> get_hint_pep_args(typing.List[int, str, typing.Dict[str, str])
        (int, str, typing.Dict[str, str])
    '''

    # Return the value of the "__args__" dunder attribute on this object if
    # this object defines this attribute *OR* the empty tuple otherwise. Note:
    #
    # * The trailing "or ()" test is required to handle edge cases under the
    #   Python < 3.7.0 implementation of the "typing" module. Notably, under
    #   Python 3.6.11:
    #       >>> import typing as t
    #       >>> t.Tuple.__args__   # yes, this is total bullocks
    #       None
    return getattr(hint, '__args__', ()) or ()


def get_hint_pep_typevars(hint: object) -> tuple:
    '''
    Tuple of all **unique type variables** (i.e., subscripted :class:`TypeVar`
    instances of the passed PEP-compliant type hint listed by the caller at
    hint declaration time ignoring duplicates) if any *or* the empty tuple
    otherwise.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This function should always be called in lieu of attempting to directly
    access the low-level** ``__parameters__`` **dunder attribute.** Various
    singleton objects defined by the :mod:`typing` module (e.g.,
    :attr:`typing.Any`, :attr:`typing.NoReturn`) fail to define this attribute,
    guaranteeing :class:`AttributeError` exceptions from all general-purpose
    logic attempting to directly access this attribute. Thus this function,
    which "fills in the gaps" by implementing this oversight.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    tuple
        Either:

        * If this object defines a ``__parameters__`` dunder attribute, the
          value of that attribute.
        * Else, the empty tuple.

    Examples
    ----------
        >>> import typing
        >>> from beartype._util.hint.pep.utilhintpepget import (
        ...     get_hint_pep_typevars)
        >>> S = typing.TypeVar('S')
        >>> T = typing.TypeVar('T')
        >>> get_hint_pep_typevars(typing.Any)
        ()
        >>> get_hint_pep_typevars(typing.List[T, int, S, str, T)
        (T, S)
    '''

    #FIXME: After dropping Python 3.6, drop the trailing "or ()". See below.

    # Value of the "__parameters__" dunder attribute on this object if this
    # object defines this attribute *OR* the empty tuple otherwise. Note that:
    # * The "typing._GenericAlias.__parameters__" dunder attribute tested here
    #   is defined by the typing._collect_type_vars() function at subscription
    #   time. Yes, this is insane. Yes, this is PEP 484.
    # * This trivial test implicitly handles superclass parametrizations.
    #   Thankfully, the "typing" module percolates the "__parameters__" dunder
    #   attribute from "typing" pseudo-superclasses to user-defined subclasses
    #   during PEP 560-style type erasure. Finally: they did something right.
    # * The trailing "or ()" test is required to handle edge cases under the
    #   Python < 3.7.0 implementation of the "typing" module. Notably, under
    #   Python 3.6.11:
    #       >>> import typing as t
    #       >>> t.Union.__parameters__   # yes, this is total bullocks
    #       None
    return getattr(hint, '__parameters__', ()) or ()

# ....................{ GETTERS ~ sign                    }....................
#FIXME: Revise docstring to account for refactorings imposed by PEP 585.

@callable_cached
def get_hint_pep_sign(hint: object) -> dict:
    '''
    **Sign** (i.e., arbitrary object) uniquely identifying the passed
    PEP-compliant type hint if this hint is PEP-compliant *or* raise an
    exception otherwise (i.e., if this hint is *not* PEP-compliant).

    This getter function associates the passed hint with a public attribute of
    the :mod:`typing` module effectively acting as a superclass of this hint
    and thus uniquely identifying the "type" of this hint in the broadest sense
    of the term "type". These attributes are typically *not* actual types, as
    most actual :mod:`typing` types are private, fragile, and prone to extreme
    violation (or even removal) between major Python versions. Nonetheless,
    these attributes are sufficiently unique to enable callers to distinguish
    between numerous broad categories of :mod:`typing` behaviour and logic.

    Specifically, this function returns either:

    * If this hint is a **generic** (i.e., instance of the
      :class:`typing.Generic` abstract base class (ABC)),
      :class:`typing.Generic`.
    * Else if this hint is a **type variable** (i.e., instance of the concrete
      :class:`typing.TypeVar` class), :class:`typing.TypeVar`.
    * Else if this hint is **optional** (i.e., subscription of the
      :attr:`typing.Optional` attribute), :attr:`typing.Union`. The
      :mod:`typing` module implicitly reduces *all* subscriptions of the
      :attr:`typing.Optional` singleton by the corresponding
      :attr:`typing.Union` singleton subscripted by both that argument and
      ``type(None)``. Ergo, there effectively exists *no*
      :attr:`typing.Optional` attribute with respect to categorization.
    * Else, the unsubscripted :mod:`typing` attribute dynamically retrieved by
      inspecting this hint's **object representation** (i.e., the
      non-human-readable string returned by the :func:`repr` builtin).

    This getter function is memoized for efficiency.

    Motivation
    ----------
    Both `PEP 484`_ and the :mod:`typing` module implementing `PEP 484`_ are
    functionally deficient with respect to their public APIs. Neither provide
    external callers any means of deciding the categories of arbitrary
    PEP-compliant type hints. For example, there exists no general-purpose
    means of identifying a parametrized subtype (e.g., ``typing.List[int]``) as
    a parametrization of its unparameterized base type (e.g., ``type.List``).
    Thus this function, which "fills in the gaps" by implementing this
    oversight.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    dict
        Sign uniquely identifying this hint.

    Raises
    ----------
    AttributeError
        If this object's representation is prefixed by the substring
        ``"typing."``, but the remainder of that representation up to but *not*
        including the first "[" character in that representation (e.g.,
        ``"Dict"`` for the object ``typing.Dict[str, Tuple[int, ...]]``) is
        *not* an attribute of the :mod:`typing` module.
    BeartypeDecorHintPepException
        If this object is *not* a PEP-compliant type hint.

    Examples
    ----------
        >>> import typing
        >>> from beartype._util.hint.pep.utilhintpepget import (
        ...     get_hint_pep_sign)
        >>> get_hint_pep_sign(typing.Any)
        typing.Any
        >>> get_hint_pep_sign(typing.Union[str, typing.Sequence[int]])
        typing.Union
        >>> T = typing.TypeVar('T')
        >>> get_hint_pep_sign(T)
        typing.TypeVar
        >>> class Genericity(typing.Generic[T]): pass
        >>> get_hint_pep_sign(Genericity)
        typing.Generic
        >>> class Duplicity(typing.Iterable[T], typing.Container[T]): pass
        >>> get_hint_pep_sign(Duplicity)
        typing.Iterable

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Avoid circular import dependencies.
    from beartype.cave import HintPep585Type
    from beartype._util.hint.pep.utilhintpeptest import (
        die_unless_hint_pep,
        is_hint_pep_typevar,
    )
    from beartype._util.hint.pep.proposal.utilhintpep484 import (
        is_hint_pep484_generic,
    )
    from beartype._util.hint.pep.proposal.utilhintpep585 import is_hint_pep585

    # If this hint is *NOT* PEP-compliant, raise an exception.
    #
    # Note that we intentionally avoid calling the
    # die_unless_hint_pep_supported() function here, which calls the
    # is_hint_pep_supported() function, which calls this function.
    die_unless_hint_pep(hint)
    # Else, this hint is PEP-compliant.

    # If this hint is a PEP 484-compliant generic (i.e., class subclassing one
    # or more "typing" pseudo-superclasses), return the "typing.Generic" ABC
    # generically (...get it?) identifying multiple-inherited generics.
    #
    # Note that the "typing" module guarantees *ALL* generics to subclass
    # this ABC regardless of whether those generics originally did so
    # explicitly. How? By type erasure, the gift that keeps on giving:
    #     >>> import typing as t
    #     >>> class MuhList(t.List): pass
    #     >>> MuhList.__orig_bases__
    #     (typing.List)
    #     >>> MuhList.__mro__
    #     (__main__.MuhList, list, typing.Generic, object)
    #
    # Ergo, this ABC uniquely identifies *ALL* generics and thus serves as
    # a sufficient and complete unsubscripted "typing" attribute.
    #
    # Note that generics *CANNOT* be detected by the general-purpose logic
    # performed below, as this ABC does *NOT* define a __repr__() dunder method
    # returning a string prefixed by the "typing." substring.
    if is_hint_pep484_generic(hint):
        return Generic
    # Else, this hint is PEP-compliant but *NOT* a generic.
    #
    # If this hint is PEP 585-compliant type hint, return the C-based ABC
    # generically identifying *ALL* such hints.
    elif is_hint_pep585(hint):
        return HintPep585Type
    # If this hint is a type variable, return a dictionary constant mapping
    # from the common type of all such variables.
    #
    # Note that type variables *CANNOT* be detected by the general-purpose
    # logic performed below, as the TypeVar.__repr__() dunder method insanely
    # returns a string prefixed by the non-human-readable character "~" rather
    # than the module name "typing." -- unlike most "typing" objects:
    #      >>> import typing as t
    #      >>> repr(t.TypeVar('T'))
    #      ~T
    #
    # Of course, that brazenly violates Pythonic standards. __repr__() is
    # generally assumed to return an evaluatable Python expression that, when
    # evaluated, instantiates an object equal to the original object. Instead,
    # this API was designed by incorrigible monkeys who profoundly hate the
    # Python language. This is why we can't have sane things.
    #
    # Ergo, type variables require special-purpose handling and *CANNOT* be
    # handled by the general-purpose detection implemented below.
    elif is_hint_pep_typevar(hint):
        return TypeVar
    # Else, this hint is PEP-compliant but neither a generic nor type variable.

    #FIXME: Consider shifting this PEP 484-specific logic as well as the above
    #"if is_hint_pep484_generic(hint):" branch into a new
    #utilhintpep484.get_hint_pep484_sign() function for maintainability.

    # Machine-readable string representation of this hint also serving as the
    # fully-qualified name of the public "typing" attribute uniquely associated
    # with this hint (e.g., "typing.Tuple[str, ...]").
    #
    # Although the "typing" module provides *NO* sane public API, it does
    # reliably implement the __repr__() dunder method across most objects and
    # types to return a string prefixed "typing." regardless of Python version.
    # Ergo, this string is effectively the *ONLY* sane means of deciding which
    # broad category of behaviour an arbitrary PEP 484 type hint conforms to.
    sign_name = repr(hint)

    # If this representation is *NOT* prefixed by "typing.", this hint does
    # *NOT* originate from the "typing" module and is thus *NOT* PEP-compliant.
    # But by the validation above, this hint is PEP-compliant. Since this
    # invokes a world-shattering paradox, raise an exception.
    if not sign_name.startswith('typing.'):
        raise BeartypeDecorHintPepException(
            f'PEP 484-compliant type hint {repr(hint)} '
            f'representation "{sign_name}" not prefixed by "typing.".'
        )

    # Strip the now-harmful "typing." prefix from this representation.
    # Preserving this prefix would raise an "AttributeError" exception from
    # the subsequent call to the getattr() builtin.
    sign_name = sign_name[7:]  # hardcode us up the bomb

    # 0-based index of the first "[" delimiter in this representation if
    # any *OR* -1 otherwise.
    sign_name_bracket_index = sign_name.find('[')

    # If this representation contains such a delimiter, this is a subscripted
    # type hint. In this case, reduce this representation to its unsubscripted
    # form by truncating the suffixing parametrization from this representation
    # (e.g., from "typing.Union[str, typing.Sequence[int]]" to merely
    # "typing.Union").
    #
    # Note that this is the common case and thus explicitly tested first.
    if sign_name_bracket_index > 0:
        sign_name = sign_name[:sign_name_bracket_index]
    # Else, this representation contains no such delimiter and is thus already
    # unsubscripted. In this case, preserve this representation as is.

    # Return the "typing" attribute with this name if any *OR* implicitly raise
    # an "AttributeError" exception. This is an unlikely edge case that will
    # probably only occur with intentionally malicious callers whose objects
    # override their __repr__() dunder methods to return strings prefixed by
    # "typing.". Ergo, we avoid performing any deeper validation here.
    # print(f'sign_name: {sign_name}')
    return getattr(typing, sign_name)

# ....................{ GETTERS ~ type                    }....................
def get_hint_pep_type_origin(hint: object) -> type:
    '''
    **Origin type** (i.e., non-:mod:`typing` class such that *all* objects
    satisfying the passed PEP-compliant type hint are instances of this class)
    originating this hint if this hint originates from a non-:mod:`typing`
    class *or* raise an exception otherwise (i.e., if this hint does *not*
    originate from a non-:mod:`typing` class).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    tuple
        Origin type originating this hint.

    See Also
    ----------
    :func:`get_hint_pep_type_origin_or_none`
    '''

    # Origin type originating this object if any *OR* "None" otherwise.
    hint_type_origin = get_hint_pep_type_origin_or_none(hint)

    # If this type exists, return this type.
    if hint_type_origin is not None:
        return hint_type_origin

    # Else, no such type exists. In this case, raise an exception.
    raise BeartypeDecorHintPepException(
        f'PEP type hint {repr(hint)} originates from no non-"typing" type.')


def get_hint_pep_type_origin_or_none(hint: object) -> 'NoneTypeOr[type]':
    '''
    **Origin type** (i.e., non-:mod:`typing` class such that *all* objects
    satisfying the passed PEP-compliant type hint are instances of this class)
    originating this hint if this hint originates from a non-:mod:`typing`
    class *or* ``None`` otherwise (i.e., if this hint does *not* originate from
    a non-:mod:`typing` class).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This function should always be called in lieu of attempting to directly
    access the low-level** ``__origin__`` **dunder attribute.** This attribute
    is defined non-orthogonally by various singleton objects in the
    :mod:`typing` module, including:

    * Objects failing to define this attribute (e.g., :attr:`typing.Any`,
      :attr:`typing.NoReturn`).
    * Objects defining this attribute to be their unsubscripted :mod:`typing`
      object (e.g., :attr:`typing.Optional`, :attr:`typing.Union`).
    * Objects defining this attribute to be their origin type.

    Since the :mod:`typing` module neither guarantees the existence of this
    attribute nor imposes a uniform semantic on this attribute when defined,
    this attribute is *not* safely directly accessible. Thus this function,
    which "fills in the gaps" by implementing this oversight.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    tuple
        Either:

        * If this object originates from a non-:mod:`typing` class, that class.
        * Else, ``None``.

    Examples
    ----------
        >>> import typing
        >>> from beartype._util.hint.pep.utilhintpepget import (
        ...     get_hint_pep_type_origin_or_none)
        # This is sane.
        >>> get_hint_pep_type_origin_or_none(typing.List[int])
        list
        >>> get_hint_pep_type_origin_or_none(typing.Union[int, str])
        None
        # This is reasonable.
        >>> typing.List.__origin__
        list
        >>> typing.List[int].__origin__
        list
        # This is crazy.
        >>> typing.Union.__origin__
        AttributeError: '_SpecialForm' object has no attribute '__origin__'
        # This is balls crazy.
        >>> typing.Union[int].__origin__
        AttributeError: type object 'int' has no attribute '__origin__'
        # This is balls cray-cray -- the ultimate evolution of crazy.
        >>> typing.Union[int, str].__origin__
        typing.Union
    '''

    # Sign uniquely identifying this hint.
    hint_sign = get_hint_pep_sign(hint)

    # Return either...
    return (
        # If this sign originates from an origin type, that type.
        hint_sign.__origin__
        if hint_sign in HINT_PEP_SIGNS_TYPE_ORIGIN else
        # Else, "None".
        None
    )
