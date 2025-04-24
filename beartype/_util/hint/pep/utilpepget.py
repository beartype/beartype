#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-compliant type hint getters** (i.e., low-level callables
introspecting PEP-compliant type hints for associated metadata).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPepException
from beartype.roar._roarexc import _BeartypeUtilTypeException
from beartype.typing import (
    Any,
    Optional,
)
from beartype._data.hint.datahintpep import (
    Hint,
    HintOrNone,
)
from beartype._data.hint.datahinttyping import (
    TypeException,
)
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_ORIGIN_ISINSTANCEABLE,
)
from beartype._util.hint.pep.proposal.pep585 import (
    get_hint_pep585_generic_typevars,
    is_hint_pep585_generic_unsubbed,
)
from beartype._data.hint.datahinttyping import TupleTypeVars

# ....................{ GETTERS ~ args                     }....................
def get_hint_pep_args(hint: object) -> tuple:
    '''
    Tuple of the zero or more **child type hints** subscripting (indexing) the
    passed PEP-compliant type hint if this hint was subscripted *or* the empty
    tuple otherwise (i.e., if this hint is unsubscripted and is thus either an
    unsubscriptable type hint *or* a subscriptable type hint factory that is
    unsubscripted).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    -------
    **This getter should always be called in lieu of attempting to directly
    access the low-level** ``__args__`` **dunder attribute.** Various
    singleton objects defined by the :mod:`typing` module (e.g.,
    :attr:`typing.Any`, :attr:`typing.NoReturn`) fail to define this attribute,
    guaranteeing :class:`AttributeError` exceptions from all general-purpose
    logic attempting to directly access this attribute. Thus this function,
    which "fills in the gaps" by implementing this oversight.

    **This getter lies rarely due to subscription erasure** (i.e., the malicious
    destruction of child type hints by parent type hint factories at
    subscription time). Callers should *not* assume that the objects originally
    subscripting this hint are still accessible. Although *most* hints preserve
    their subscripted objects over their lifetimes, a small subset of edge-case
    hints erase those objects at subscription time. This includes:

    * :pep:`585`-compliant empty tuple type hints (i.e., ``tuple[()]``), which
      despite being explicitly subscripted erroneously erase that subscription
      at subscription time. This does *not* extend to :pep:`484`-compliant
      empty tuple type hints (i.e., ``typing.Tuple[()]``), which correctly
      preserve that subscripted empty tuple.

    **This getter lies less than the comparable**
    :func:`.get_hint_pep_typevars` **getter.** Whereas
    :func:`.get_hint_pep_typevars` synthetically propagates type variables from
    child to parent type hints (rather than preserving the literal type
    variables subscripting this type hint), this getter preserves the literal
    arguments subscripting this type hint if any. Notable cases where the two
    differ include:

    * Generic classes subclassing pseudo-superclasses subscripted by one or
      more type variables (e.g., ``class MuhGeneric(Generic[S, T])``).
    * Unions subscripted by one or more child type hints subscripted by one or
      more type variables (e.g., ``Union[str, Iterable[Tuple[S, T]]]``).

    Parameters
    ----------
    hint : object
        PEP-compliant type hint to be inspected.

    Returns
    -------
    tuple
        Either:

        * If this hint defines an ``__args__`` dunder attribute, the value of
          that attribute.
        * Else, the empty tuple.

    Examples
    --------
    .. code-block:: pycon

       >>> import typing
       >>> from beartype._util.hint.pep.utilpepget import (
       ...     get_hint_pep_args)
       >>> get_hint_pep_args(typing.Any)
       ()
       >>> get_hint_pep_args(typing.List[int, str, typing.Dict[str, str]])
       (int, str, typing.Dict[str, str])
    '''

    # Tuple of the zero or more child type hints subscripting this hint if
    # this hint defines of the "__args__" dunder attribute *OR* "None"
    # otherwise (i.e., if this hint fails to define this attribute).
    hint_args = getattr(hint, '__args__', None)

    # If this hint does *NOT* define this attribute, return the empty tuple.
    if hint_args is None:
        return ()
    # Else, this hint defines this attribute.
    #
    # If this hint is subscripted by zero child type hints, this hint only
    # superficially appears to be unsubscripted but was actually subscripted
    # by the empty tuple (e.g., "tuple[()]", "typing.Tuple[()]"). Why?
    # Because:
    # * Python 3.11 made the unfortunate decision of ambiguously conflating
    #   unsubscripted type hints (e.g., "tuple", "typing.Tuple") with type
    #   hints subscripted by the empty tuple, preventing downstream
    #   consumers from reliably distinguishing these two orthogonal cases.
    # * Python 3.9 made a similar decision but constrained to only PEP
    #   585-compliant empty tuple type hints (i.e., "tuple[()]"). PEP
    #   484-compliant empty tuple type hints (i.e., "typing.Tuple[()]")
    #   continued to correctly declare an "__args__" dunder attribute of
    #   "((),)" until Python 3.11.
    #
    # Disambiguate these two cases on behalf of callers by returning a
    # 1-tuple containing only the empty tuple (i.e., "((),)") rather than
    # returning the empty tuple (i.e., "()").
    elif not hint_args:
        return _HINT_ARGS_EMPTY_TUPLE
    # Else, this hint is either subscripted *OR* is unsubscripted but not
    # PEP 585-compliant.

    # In this case, return this tuple as is.
    return hint_args


# ....................{ GETTERS ~ typevars                 }....................
def get_hint_pep_typevars(hint: Hint) -> TupleTypeVars:
    '''
    Tuple of all **unique type variables** (i.e., subscripted :class:`TypeVar`
    instances of the passed PEP-compliant type hint listed by the caller at
    hint declaration time ignoring duplicates) if any *or* the empty tuple
    otherwise.

    This getter correctly handles both:

    * **Direct parametrizations** (i.e., cases in which this object itself is
      directly parametrized by type variables).
    * **Superclass parametrizations** (i.e., cases in which this object is
      indirectly parametrized by one or more superclasses of its class being
      directly parametrized by type variables).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    -------
    **This function should always be called in lieu of attempting to directly
    access the low-level** ``__parameters__`` **dunder attribute.** Various
    singleton objects defined by the :mod:`typing` module (e.g.,
    :attr:`typing.Any`, :attr:`typing.NoReturn`) fail to define this attribute,
    guaranteeing :class:`AttributeError` exceptions from all general-purpose
    logic attempting to directly access this attribute. Thus this function,
    which "fills in the gaps" by implementing this oversight.

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
    hint : Hint
        Object to be inspected.

    Returns
    -------
    Tuple[TypeVar, ...]
        Either:

        * If this object defines a ``__parameters__`` dunder attribute, the
          value of that attribute.
        * Else, the empty tuple.

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
       >>> from beartype._util.hint.pep.utilpepget import (
       ...     get_hint_pep_typevars)

       >>> S = typing.TypeVar('S')
       >>> T = typing.TypeVar('T')
       >>> class UserList(typing.List[T]): pass

       >>> get_hint_pep_typevars(typing.Any)
       ()
       >>> get_hint_pep_typevars(typing.List[int])
       ()
       >>> get_hint_pep_typevars(typing.List[T])
       (T)
       >>> get_hint_pep_typevars(UserList)
       (T)
       >>> get_hint_pep_typevars(typing.List[T, int, S, str, T])
       (T, S)
    '''

    # Value of the "__parameters__" dunder attribute on this object if this
    # object defines this attribute (e.g., is *NOT* a PEP 585-compliant
    # unsubscripted generic) *OR* "None" otherwise (e.g., is such a generic).
    hint_pep_typevars = getattr(hint, '__parameters__', None)

    # If this object defines *NO* such attribute, synthetically reconstruct
    # this attribute for PEP 585-compliant unsubscripted generics. Notably...
    if hint_pep_typevars is None:
        # Reconstruct this attribute as either...
        hint_pep_typevars = (
            # If this hint is a PEP 585-compliant unsubscripted generic, the
            # tuple of all type variables parametrizing all pseudo-superclasses
            # of this generic;
            get_hint_pep585_generic_typevars(hint)
            if is_hint_pep585_generic_unsubbed(hint) else
            # Else, this hint is *NOT* a PEP 585-compliant unsubscripted
            # generic. In this case, the empty tuple.
            ()
        )
    # Else, this object defines this attribute.

    # Return this attribute.
    return hint_pep_typevars

# ....................{ GETTERS ~ origin                   }....................
def get_hint_pep_origin(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    #FIXME: This should probably be a new "BeartypeDecorHintPepOriginException"
    #type, instead. But it's unclear whether users will even ever see this
    #exception. So, for now, laziness prevails. Huzzah! *sigh*
    exception_cls: TypeException = _BeartypeUtilTypeException,
    exception_prefix: str = '',
) -> Hint:
    '''
    **Unsafe origin object** (i.e., arbitrary object originating the passed
    PEP-compliant type hint but *not* necessarily an isinstanceable class such
    that all objects satisfying this hint are instances of this class)
    originating this hint if this hint originates from an origin *or*
    raise an exception otherwise (i.e., if this hint originates from *no*
    origin).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`.callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : Hint
        Object to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`._BeartypeUtilTypeException`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    -------
    Hint
        Arbitrary object this hint originates from.

    Raises
    ------
    exception_cls
        If this hint originates from *no* object.
    '''

    # Origin originating this hint if any *OR* "None" otherwise.
    hint_origin = get_hint_pep_origin_or_none(hint)

    # If this hint does *NOT* originate from anything, raise an exception.
    if hint_origin is None:
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} '
            f'originates from no other object.'
        )
    # Else, this hint originates from something.

    # Return that something.
    return hint_origin


def get_hint_pep_origin_or_none(hint: Hint) -> HintOrNone:
    '''
    **Unsafe origin object** (i.e., arbitrary object originating the passed
    PEP-compliant type hint but *not* necessarily an isinstanceable class such
    that all objects satisfying this hint are instances of this class)
    originating this hint if this hint originates from an origin *or*
    :data:`None` otherwise (i.e., if this hint originates from *no* origin).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    -------
    **The high-level** :func:`get_hint_pep_origin_type_isinstanceable` getter
    should always be called in lieu of this low-level function.** Whereas the
    former is guaranteed to return either an isinstanceable class or
    :data:`None`, this getter enjoys no such guarantees and instead returns an
    arbitrary object that may or may not actually be an instanceable class.

    If this getter *must* be called, **this getter should always be called in
    lieu of attempting to directly access the low-level** ``__origin__``
    **dunder attribute.** Various :mod:`typing` objects either fail to define
    this attribute or define this attribute non-orthogonally, including objects:

    * Failing to define this attribute altogether (e.g., :attr:`typing.Any`,
      :attr:`typing.NoReturn`).
    * Defining this attribute to be their unsubscripted :mod:`typing` type hint
      factories (e.g., :attr:`typing.Optional`, :attr:`typing.Union`).
    * Defining this attribute to be their actual origin types.

    Since the :mod:`typing` module neither guarantees the existence of this
    attribute nor imposes a uniform semantic on this attribute when defined,
    that attribute is *not* safely directly accessible. Thus this getter, which
    "fills in the gaps" by implementing this oversight.

    Parameters
    ----------
    hint : Hint
        Object to be inspected.

    Returns
    -------
    Optional[Hint]
        Either:

        * If this hint originates from an arbitrary object, that object.
        * Else, :data:`None`.

    Examples
    --------
    .. code-block:: pycon

       >>> import typing
       >>> from beartype._util.hint.pep.utilpepget import (
       ...     get_hint_pep_origin_or_none)

       # This is sane.
       >>> get_hint_pep_origin_or_none(typing.List)
       list
       >>> get_hint_pep_origin_or_none(typing.List[int])
       list
       >>> get_hint_pep_origin_or_none(typing.Union)
       None
       >>> get_hint_pep_origin_or_none(typing.Union[int])
       None

       # This is insane.
       >>> get_hint_pep_origin_or_none(typing.Union[int, str])
       Union

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

    # Return this hint's origin object if any *OR* "None" otherwise.
    return getattr(hint, '__origin__', None)

# ....................{ GETTERS ~ origin : type            }....................
#FIXME: Unit test us up, please.
def get_hint_pep_origin_type(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    #FIXME: This should probably be a new "BeartypeDecorHintPepOriginException"
    #type, instead. But it's unclear whether users will even ever see this
    #exception. So, for now, laziness prevails. Huzzah! *sigh*
    exception_cls: TypeException = _BeartypeUtilTypeException,
    exception_prefix: str = '',
) -> type:
    '''
    **Origin type** (i.e., class such that *all* objects satisfying the passed
    PEP-compliant type hint are instances of this class) originating this hint
    if this hint originates from such a type *or* raise an exception otherwise
    (i.e., if this hint originates from *no* such type).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`.callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Type hint to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`._BeartypeUtilTypeException`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    -------
    type
        Type originating this hint.

    Raises
    ------
    exception_cls
        If this hint either:

        * Does *not* originate from another object.
        * Originates from an object that is *not* a type.

    See Also
    --------
    :func:`.get_hint_pep_origin_or_none`
        Further details.
    '''

    # Origin type originating this hint if any *OR* "None" otherwise.
    hint_origin = get_hint_pep_origin_type_or_none(hint)

    # If *NO* origin type originates this hint...
    if hint_origin is None:
        assert isinstance(exception_cls, type), (
            f'{exception_cls} not exception type.')
        assert isinstance(exception_prefix, str), (
            f'{exception_prefix} not string.')

        # Origin non-type originating this hint if any *OR* "None" otherwise.
        hint_origin_nontype = get_hint_pep_origin_or_none(hint)

        # If this hint does *NOT* originate from another object, raise an
        # appropriate exception.
        if hint_origin_nontype is None:
            raise exception_cls(
                f'{exception_prefix}type hint {repr(hint)} '
                f'originates from no other object.'
            )
        # Else, this hint originates from another object. By definition, this
        # object *CANNOT* be a type.

        # Raise an appropriate exception.
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} '
            f'originates from non-type {repr(hint_origin_nontype)}.'
        )
    # Else, this origin type originates this hint.

    # Return this origin type.
    return hint_origin


#FIXME: Unit test us up, please.
def get_hint_pep_origin_type_or_none(
    # Mandatory parameters.
    hint: Any,

    # Optional parameters.
    is_self_fallback: bool = False,
) -> Optional[type]:
    '''
    **Origin type** (i.e., class such that *all* objects satisfying the passed
    PEP-compliant type hint are instances of this class) originating this hint
    if this hint originates from such a type *or* :data:`None` otherwise (i.e.,
    if this hint originates from *no* such type).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`.callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    -------
    **This high-level getter should always be called in lieu of either calling
    the low-level** :func:`.get_hint_pep_origin_or_none` **getter or attempting
    to directly access the low-level** ``__origin__`` **dunder attribute.**

    Parameters
    ----------
    hint : object
        Type hint to be inspected.
    is_self_fallback : bool = False
        :data:`True` only if returning the passed hint as a last-ditch fallback
        when this hint is a type defining the ``__origin__`` dunder attribute to
        be a non-type. Equivalently, if the passed hint is such a hint *and*
        this parameter is:

        * :data:`True`, this getter returns this hint as is.
        * :data:`False`, this getter returns :data:`None`.

        Defaults to :data:`False`. Explicit is better than implicit.

    Returns
    -------
    Optional[type]
        Either:

        * If this hint originates from a type, that type.
        * Else, :data:`None`.

    See Also
    --------
    :func:`.get_hint_pep_origin_or_none`
        Further details.
    '''
    assert isinstance(is_self_fallback, bool), (
        f'{repr(is_self_fallback)} not boolean.')

    # Unsafe origin type originating this hint if any *OR* "None" otherwise,
    # initialized to the arbitrary object set as the "hint.__origin__" dunder
    # attribute if this hint defines that attribute.
    hint_origin: Optional[type] = get_hint_pep_origin_or_none(hint)  # type: ignore[assignment]

    #FIXME: Unit test this up, please. *shrug*
    # If this origin is *NOT* a type...
    #
    # Ideally, this attribute would *ALWAYS* be a type for all possible
    # PEP-compliant type hints. For unknown reasons, type hint factories defined
    # by the standard "typing" module often set their origins to those same type
    # hint factories, despite those factories *NOT* being types. Why? Frankly,
    # we have no idea and neither does anyone else. Behold, true horror:
    #    >>> import typing
    #    >>> typing.Literal[1, 2].__origin__
    #    typing.Literal  # <-- do you even know what you are doing, python?
    #    >>> typing.Optional[int].__origin__
    #    typing.Union  # <-- wut? this is insane, python.
    if not isinstance(hint_origin, type):
        # Default this origin type to either...
        hint_origin = (
            # If...
            hint if (
                # The caller requests the "self" fallback logic *AND*...
                is_self_fallback and
                # This hint is itself a type, this hint could be euphemistically
                # said to originate from "itself." Fallback to this hint itself.
                # Look. Just go with it. We wave our hands in the air
                isinstance(hint, type)
            ) else
            # Else, either the caller did not request the "self" fallback logic
            # *OR* this hint is not a type. In either case, fallback to "None".
            None
        )
    # Else, this origin is a type.

    # Return this origin type.
    return hint_origin


def get_hint_pep_origin_type_isinstanceable(hint: Hint) -> type:
    '''
    **Isinstanceable origin type** (i.e., class passable as the second argument
    to the :func:`isinstance` builtin such that *all* objects satisfying the
    passed PEP-compliant type hint are instances of this class) originating
    this hint if this hint originates from such a type *or* raise an exception
    otherwise (i.e., if this hint does *not* originate from such a type).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : Hint
        Type hint to be inspected.

    Returns
    -------
    type
        Standard origin type originating this hint.

    Raises
    ------
    BeartypeDecorHintPepException
        If this hint does *not* originate from a standard origin type.

    See Also
    --------
    :func:`get_hint_pep_origin_type_isinstanceable_or_none`
        Related getter.
    '''

    # Origin type originating this object if any *OR* "None" otherwise.
    hint_origin_type = get_hint_pep_origin_type_isinstanceable_or_none(hint)

    # If this type does *NOT* exist, raise an exception.
    if hint_origin_type is None:
        raise BeartypeDecorHintPepException(
            f'Type hint {repr(hint)} not isinstanceable (i.e., does not '
            f'originate from isinstanceable class).'
        )
    # Else, this type exists.

    # Return this type.
    return hint_origin_type


def get_hint_pep_origin_type_isinstanceable_or_none(
    hint: Hint) -> Optional[type]:
    '''
    **Standard origin type** (i.e., isinstanceable class declared by Python's
    standard library such that *all* objects satisfying the passed
    PEP-compliant type hint are instances of this class) originating this hint
    if this hint originates from such a type *or* :data:`None` otherwise (i.e.,
    if this hint does *not* originate from such a type).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    -------
    **This high-level getter should always be called in lieu of the low-level**
    :func:`get_hint_pep_origin_or_none` **getter or attempting to
    directly access the low-level** ``__origin__`` **dunder attribute.**

    Parameters
    ----------
    hint : Hint
        Object to be inspected.

    Returns
    -------
    Optional[type]
        Either:

        * If this hint originates from a standard origin type, that type.
        * Else, :data:`None`.

    See Also
    --------
    :func:`get_hint_pep_origin_type_isinstanceable`
        Related getter.
    :func:`get_hint_pep_origin_or_none`
        Further details.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign_or_none

    # Sign uniquely identifying this hint if any *OR* "None" otherwise.
    hint_sign = get_hint_pep_sign_or_none(hint)

    # Return either...
    return (
        # If this sign originates from an origin type, that type;
        get_hint_pep_origin_or_none(hint)  # type: ignore[return-value]
        if hint_sign in HINT_SIGNS_ORIGIN_ISINSTANCEABLE else
        # Else, "None".
        None
    )

# ....................{ PRIVATE ~ args                     }....................
#FIXME: Shift into the "beartype._data.hint" subpackage somewhere, please.
_HINT_ARGS_EMPTY_TUPLE = ((),)
'''
Tuple containing only the empty tuple, to be returned from the
:func:`get_hint_pep_args` getter when passed either:

* A :pep:`585`-compliant type hint subscripted by the empty tuple (e.g.,
  ``tuple[()]``).
* A :pep:`484`-compliant type hint subscripted by the empty tuple (e.g.,
  ``typing.Tuple[()]``) under Python >= 3.11, which applied the :pep:`585`
  approach throughout the :mod:`typing` module.
'''
