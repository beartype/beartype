#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-, :pep:`612`-, and :pep:`646`-compliant **type parameter
utilities** (i.e., low-level callables generically handling :pep:`484`-compliant
type variables, pep:`612`-compliant parameter specifications, and
:pep:`646`-compliant type variable tuples).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep484612646Exception
from beartype.typing import TypeVar
from beartype._cave._cavefast import (
    HintPep646692UnpackedType,
    HintPep484612646TypeArgPackedTypes,
)
from beartype._data.typing.datatypingport import (
    Hint,
    TypeIs,
)
from beartype._data.typing.datatyping import (
    Pep484612646TypeArg,
    TypeException,
)

# ....................{ RAISERS                            }....................
# def die_unless_hint_pep484612646_typearg_unpacked(
#     # Mandatory parameters.
#     hint: object,
#
#     # Optional parameters.
#     exception_cls: TypeException = BeartypeDecorHintPep484612646Exception,
#     exception_prefix: str = '',
# ) -> None:
#     '''
#     Raise an exception unless the passed object is an **unpacked type
#     parameter** (i.e., :pep:`484`-compliant type variable, pep:`612`-compliant
#     parameter specification, or :pep:`646`-compliant type variable tuples).
#
#     Equivalently, this validator raises an exception if this object is neither:
#
#     * A string whose value is the syntactically valid name of a class.
#     * An instance of the :class:`typing.ForwardRef` class. The :mod:`typing`
#       module implicitly replaces all strings subscripting :mod:`typing` objects
#       (e.g., the ``MuhType`` in ``List['MuhType']``) with
#       :class:`typing.ForwardRef` instances containing those strings as instance
#       variables, for nebulous reasons that make little justifiable sense but
#       what you gonna do 'cause this is 2020. *Fight me.*
#
#     Parameters
#     ----------
#     hint : object
#         Object to be validated.
#     exception_cls : Type[Exception], default: BeartypeDecorHintForwardRefException
#         Type of exception to be raised in the event of a fatal error. Defaults
#         to :exc:`.BeartypeDecorHintForwardRefException`.
#     exception_prefix : str, default: ''
#         Human-readable substring prefixing raised exception messages. Defaults
#         to the empty string.
#
#     Raises
#     ------
#     exception_cls
#         If this object is *not* a forward reference type hint.
#     '''
#
#     # If this object is *NOT* a forward reference type hint, raise an exception.
#     if not isinstance(hint, TYPES_PEP484585_REF):
#         assert isinstance(exception_cls, type), (
#             f'{repr(exception_cls)} not exception subclass.')
#         assert isinstance(exception_prefix, str), (
#             f'{repr(exception_prefix)} not string.')
#
#         raise exception_cls(
#             f'{exception_prefix}type hint {repr(hint)} not forward reference '
#             f'(i.e., neither string nor "typing.ForwardRef" object).'
#         )
#     # Else, this object is a forward reference type hint.

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please.
def is_hint_pep484646_typearg_unpacked(
    hint: Hint) -> TypeIs[Pep484612646TypeArg]:  # pyright: ignore
    '''
    :data:`True` only if the passed type hint is a **packed type parameter**
    (i.e., :pep:`484`-compliant type variable, pep:`612`-compliant parameter
    specification, or :pep:`646`-compliant type variable tuples).

    Caveats
    -------
    **The** :func:`.is_hint_pep484612646_typearg_packed_unpacked` **tester
    should typically be called instead.** Most type parameters of real-world
    interest to end users are unpacked rather than packed.

    Parameters
    ----------
    hint : Hint
        Type hint to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this hint is a packed type parameter.
    '''

    # If this hint is a PEP 484-compliant type variable, this hint is a type
    # parameter. In this case, immediately return true.
    if isinstance(hint, TypeVar):
        return True
    # Else, this hint is *NOT* a PEP 484-compliant type variable. This hint
    # could still be a PEP 646-compliant unpacked type variable tuple, though.
    #
    # If this hint is *NOT* a PEP 646-compliant or 692-compliant unpacked hint,
    # this hint *CANNOT* by extension be a PEP 646-compliant unpacked type
    # variable tuple. In this case, return false.
    elif not isinstance(hint, HintPep646692UnpackedType):
        return False
    # Else, this hint is a PEP 646-compliant or 692-compliant unpacked hint and
    # thus could be a PEP 646-compliant unpacked type variable tuple.

    #FIXME: Implement the rest of us up, please. We'll need to defer to
    #get_hint_pep_sign_or_none() to properly differentiate PEP 646 from 692. *sigh*
    # Return true only if this hint is a type parameter.
    return False


#FIXME: Unit test us up, please.
def is_hint_pep484612646_typearg_packed(
    hint: Hint) -> TypeIs[Pep484612646TypeArg]:  # pyright: ignore
    '''
    :data:`True` only if the passed type hint is a **packed type parameter**
    (i.e., :pep:`484`-compliant type variable, pep:`612`-compliant parameter
    specification, or :pep:`646`-compliant type variable tuples).

    Caveats
    -------
    **The** :func:`.is_hint_pep484612646_typearg_packed_unpacked` **tester
    should typically be called instead.** Most type parameters of real-world
    interest to end users are unpacked rather than packed.

    Parameters
    ----------
    hint : Hint
        Type hint to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this hint is a packed type parameter.
    '''

    # Return true only if this hint is a type parameter.
    return isinstance(hint, HintPep484612646TypeArgPackedTypes)

# ....................{ GETTERS                            }....................
def get_hint_pep484612646_typearg_packed_name(
    # Mandatory parameters.
    hint: Pep484612646TypeArg,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484612646Exception,
    exception_prefix: str = '',
) -> str:
    '''
    Unqualified basename of the passed **type parameter** (i.e.,
    :pep:`484`-compliant type variable, pep:`612`-compliant parameter
    specification, or :pep:`646`-compliant type variable tuples).

    Parameters
    ----------
    hint : Pep484612646TypeArg
        Type parameter to be inspected.
    exception_cls : Type[Exception], default: BeartypeDecorHintForwardRefException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintForwardRefException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    str
        Unqualified basename of this type parameter.

    Raises
    ------
    exception_cls
        If this object is *not* a type parameter.
    '''

    # If this hint is *NOT* a type parameter, raise an exception.
    if not is_hint_pep484612646_typearg_packed(hint):  # pyright: ignore
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not exception subclass.')
        assert isinstance(exception_prefix, str), (
            f'{exception_prefix} not string.')

        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} not type parameter '
            f'(i.e., '
            f'PEP 484 "typing.TypeVar" type variable, '
            f'PEP 612 "typing.ParamSpec" parameter specification, or '
            f'PEP 646 "typing.TypeVarTuple" type variable tuple).'
        )
    # Else, this hint is a type parameter.

    # Return the name of this type parameter. Thankfully, *ALL* type parameters
    # generically conform to this simplistic API. We give minor praise.
    return hint.__name__  # type: ignore[union-attr]
