#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **dual type hint utilities**
(i.e., callables generically applicable to both :pep:`484`- and
:pep:`585`-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import (
    BeartypeDecorHintPep484585Exception,
    BeartypeDecorHintPep585Exception,
)
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignType,
    HintSignUnion,
)
from beartype._util.cls.pep.utilpep3119 import (
    die_unless_type_issubclassable,
    die_unless_type_or_types_issubclassable,
)
from beartype._util.hint.pep.proposal.pep484585.utilpep484585 import (
    get_hint_pep484585_args_1)
from beartype._util.hint.pep.proposal.pep484585.utilpepforwardref import (
    HINT_PEP484585_FORWARDREF_TYPES,
    HINT_PEP484585_FORWARDREF_UNION,
)
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_7
from typing import Any, Tuple, TypeVar, Union

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ HINTS ~ private                   }....................
_HINT_PEP484585_SUBCLASS_ARGS_1_TYPES = (
    (type, tuple, TypeVar,) + HINT_PEP484585_FORWARDREF_TYPES)
'''
Tuple union of the types of all permissible :pep:`484`- or :pep:`585`-compliant
**subclass type hint arguments** (i.e., PEP-compliant child type hints
subscripting (indexing) a subclass type hint).
'''


_HINT_PEP484585_SUBCLASS_ARGS_1_UNION: Any = (
    # If the active Python interpreter targets Python >= 3.7, include the sane
    # "typing.TypeVar" type in this union;
    Union[type, Tuple[type], TypeVar, HINT_PEP484585_FORWARDREF_UNION,]
    if IS_PYTHON_AT_LEAST_3_7 else
    # Else, the active Python interpreter targets Python 3.6. In this case,
    # exclude the insane "typing.TypeVar" type from this union. Naively
    # including that type here induces fatal runtime exceptions resembling:
    #     AttributeError: type object 'TypeVar' has no attribute '_gorg'
    Union[type, Tuple[type], HINT_PEP484585_FORWARDREF_UNION,]
)
'''
Union of the types of all permissible :pep:`484`- or :pep:`585`-compliant
**subclass type hint arguments** (i.e., PEP-compliant child type hints
subscripting (indexing) a subclass type hint).
'''

# ....................{ GETTERS                           }....................
def get_hint_pep484585_subclass_superclass(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_prefix: str = '',
) -> _HINT_PEP484585_SUBCLASS_ARGS_1_UNION:
    '''
    **Issubclassable superclass(es)** (i.e., class whose metaclass does *not*
    define a ``__subclasscheck__()`` dunder method that raises an exception,
    tuple of such classes, or forward reference to such a class) subscripting
    the passed :pep:`484`- or :pep:`585`-compliant **subclass type hint**
    (i.e., hint constraining objects to subclass that superclass).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.
    exception_prefix : Optional[str]
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    ----------
    _HINT_PEP484585_SUBCLASS_ARGS_1_UNION
        Argument subscripting this subclass type hint, guaranteed to be either:

        * An issubclassable class.
        * A tuple of issubclassable classes.
        * A :pep:`484`-compliant type variable constrained to classes (i.e.,
          :class:`typing.TypeVar` instance).
        * A :pep:`484`-compliant forward reference to an issubclassable class
          that typically has yet to be declared (i.e.,
          :class:`typing.ForwardRef` instance).
        * A :pep:`585`-compliant forward reference to an issubclassable class
          (i.e., string).

    Raises
    ----------
    :exc:`BeartypeDecorHintPep3119Exception`
        If this superclass subscripting this type hint is *not*
        **issubclassable** (i.e., class whose metaclass defines a
        ``__subclasscheck__()`` dunder method raising an exception).
    :exc:`BeartypeDecorHintPep484585Exception`
        If this hint is neither a :pep:`484`- nor :pep:`585`-compliant subclass
        type hint.
    :exc:`BeartypeDecorHintPep585Exception`
        If this hint is either:

        * A :pep:`585`-compliant subclass type hint subscripted by either:

          * *No* arguments.
          * Two or more arguments.

        * A :pep:`484`- or :pep:`585`-compliant subclass type hint subscripted
          by one argument that is neither a class, union of classes, nor
          forward reference to a class.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_args,
        get_hint_pep_sign_or_none,
    )

    # If this is *NOT* a subclass type hint, raise an exception.
    _die_unless_hint_pep484585_subclass(
        hint=hint, exception_prefix=exception_prefix)
    # Else, this is either a subclass type hint.

    # Superclass subscripting this hint.
    hint_superclass = get_hint_pep484585_args_1(
        hint=hint, exception_prefix=exception_prefix)

    # If this superclass is neither a class nor forward reference to a class,
    # raise an exception.
    if not isinstance(hint_superclass, _HINT_PEP484585_SUBCLASS_ARGS_1_TYPES):
        raise BeartypeDecorHintPep585Exception(
            f'{exception_prefix}PEP 585 subclass type hint {repr(hint)} '
            f'argument {repr(hint_superclass)} neither '
            f'class, union of classes, nor forward reference to class.'
        )
    # Else, this superclass is either a class, union of classes, or forward
    # reference to a class.

    # Sign identifying this superclass.
    hint_superclass_sign = get_hint_pep_sign_or_none(hint_superclass)

    # If this superclass is actually a union of superclasses...
    if hint_superclass_sign is HintSignUnion:
        # Efficiently reduce this superclass to the tuple of superclasses
        # subscripting and thus underlying this union.
        hint_superclass = get_hint_pep_args(hint_superclass)

        # If any item of this tuple is *NOT* an issubclassable class, raise an
        # exception.
        die_unless_type_or_types_issubclassable(
            type_or_types=hint_superclass, exception_prefix=exception_prefix)  # type: ignore[arg-type]
    # Else, this superclass is *NOT* a union of superclasses...
    #
    # If this superclass is a class...
    elif isinstance(hint_superclass, type):
        # If this superclass is *NOT* issubclassable, raise an exception.
        die_unless_type_issubclassable(
            cls=hint_superclass, exception_prefix=exception_prefix)
        # Else, this superclass is issubclassable.

    # Return this superclass.
    return hint_superclass

# ....................{ REDUCERS                          }....................
def reduce_hint_pep484585_subclass_superclass_if_ignorable(
    # Mandatory parameters.
    hint: Any,

    # Optional parameters.
    exception_prefix: str = '',
) -> Any:
    '''
    Reduce the passed :pep:`484`- or :pep:`585`-compliant **subclass type
    hint** (i.e., hint constraining objects to subclass that superclass) to the
    :class:`type` superclass if that hint is subscripted by an ignorable child
    type hint (e.g., :attr:`typing.Any`, :class:`type`) *or* preserve this hint
    as is otherwise (i.e., if that hint is *not* subscripted by an ignorable
    child type hint).

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Subclass type hint to be reduced.
    exception_prefix : Optional[str]
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ----------
    :exc:`BeartypeDecorHintPep484585Exception`
        If this hint is neither a :pep:`484`- nor :pep:`585`-compliant subclass
        type hint.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.utilhinttest import is_hint_ignorable

    # If this is *NOT* a subclass type hint, raise an exception.
    _die_unless_hint_pep484585_subclass(
        hint=hint, exception_prefix=exception_prefix)
    # Else, this is either a subclass type hint.

    # Superclass subscripting this hint.
    #
    # Note that we intentionally do *NOT* call the high-level
    # get_hint_pep484585_subclass_superclass() getter here, as the
    # validation performed by that function would raise exceptions for
    # various child type hints that are otherwise permissible (e.g.,
    # "typing.Any").
    hint_superclass = get_hint_pep484585_args_1(
        hint=hint, exception_prefix=exception_prefix)

    # If this argument is either...
    if (
        # An ignorable type hint (e.g., "typing.Any") *OR*...
        is_hint_ignorable(hint_superclass) or
        # The "type" superclass, which is effectively ignorable in this
        # context of subclasses, as *ALL* classes necessarily subclass
        # that superclass.
        hint_superclass is type
    ):
        # Reduce this subclass type hint to the "type" superclass.
        hint = type
    # Else, this argument is unignorable and thus irreducible.

    # Return this possibly reduced type hint.
    return hint

# ....................{ PRIVATE ~ validators              }....................
def _die_unless_hint_pep484585_subclass(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed object is a :pep:`484`- or
    :pep:`585`-compliant **subclass type hint** (i.e., hint constraining
    objects to subclass that superclass).

    Parameters
    ----------
    hint : object
        Object to be validated.
    exception_prefix : Optional[str]
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ----------
    :exc:`BeartypeDecorHintPep484585Exception`
        If this hint is neither a :pep:`484`- nor :pep:`585`-compliant subclass
        type hint.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign

    # If this is neither a PEP 484- nor PEP 585-compliant subclass type hint,
    # raise an exception.
    if get_hint_pep_sign(hint) is not HintSignType:
        raise BeartypeDecorHintPep484585Exception(
            f'{exception_prefix}{repr(hint)} '
            f'neither PEP 484 nor 585 subclass type hint.'
        )
