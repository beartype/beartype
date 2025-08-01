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
from beartype._data.hint.sign.datahintsigns import (
    HintSignPep646TypeVarTupleUnpacked)
from beartype._data.typing.datatyping import (
    Pep484612646TypeArgPacked,
    TypeException,
)
from beartype._data.typing.datatypingport import (
    Hint,
    TypeIs,
)

# ....................{ RAISERS                            }....................
#FIXME: Is this still called anywhere? Excise if unneeded, please. *sigh*
#FIXME: Unit test us up, please.
def die_unless_hint_pep484612646_typearg_unpacked(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484612646Exception,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed type hint is an **unpacked type
    parameter** (i.e., :pep:`484`-compliant type variable,
    :pep:`612`-compliant unpacked parameter specification, or
    :pep:`646`-compliant unpacked type variable tuple).

    Parameters
    ----------
    hint : Hint
        Type hint to be validated.
    exception_cls : Type[Exception], default: BeartypeDecorHintPep484612646Exception
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintPep484612646Exception`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Raises
    ------
    exception_cls
        If this type hint is *not* an unpacked type parameter.
    '''

    # If this hint is *NOT* an unpacked type parameter, raise an exception.
    if not is_hint_pep484612646_typearg_unpacked(hint):
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not exception subclass.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} not '
            f'unpacked type parameter (i.e., '
            f'PEP 484 "typing.TypeVar(...)" type variable or '
            f'PEP 646 "*typing.TypeVarTuple(...)" unpacked type variable tuple'
            f').'
        )
    # Else, this hint is an unpacked type parameter.


#FIXME: Unit test us up, please.
def die_unless_hint_pep484612646_typearg_packed(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484612646Exception,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed type hint is a **packed type
    parameter** (i.e., :pep:`484`-compliant type variable, pep:`612`-compliant
    parameter specification, or :pep:`646`-compliant type variable tuples).

    Parameters
    ----------
    hint : Hint
        Type hint to be validated.
    exception_cls : Type[Exception], default: BeartypeDecorHintPep484612646Exception
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintPep484612646Exception`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Raises
    ------
    exception_cls
        If this type hint is *not* a packed type parameter.
    '''

    # If this hint is *NOT* a packed type parameter, raise an exception.
    if not is_hint_pep484612646_typearg_packed(hint):
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not exception subclass.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} not '
            f'type parameter (i.e., '
            f'PEP 484 "typing.TypeVar(...)" type variable, or '
            f'PEP 612 "typing.ParamSpec(...)" parameter specification, or '
            f'PEP 646 "typing.TypeVarTuple(...)" unpacked type variable tuple'
            f').'
        )
    # Else, this hint is an unpacked type parameter.

# ....................{ TESTERS                            }....................
#FIXME: Is this still called anywhere? Excise if unneeded, please. *sigh*
#FIXME: Unit test us up, please.
def is_hint_pep484612646_typearg_unpacked(
    hint: Hint) -> TypeIs[Pep484612646TypeArgPacked]:  # pyright: ignore
    '''
    :data:`True` only if the passed type hint is a **unpacked type parameter**
    (i.e., :pep:`484`-compliant type variable, :pep:`612`-compliant unpacked
    parameter specification, or :pep:`646`-compliant unpacked type variable
    tuple).

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

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign_or_none

    # Sign uniquely identifying this hint.
    hint_sign = get_hint_pep_sign_or_none(hint)  # pyright: ignore

    # Return true only if this sign uniquely identifies this hint to be a PEP
    # 646-compliant unpacked type variable tuple.
    return hint_sign is HintSignPep646TypeVarTupleUnpacked


#FIXME: Unit test us up, please.
def is_hint_pep484612646_typearg_packed(
    hint: Hint) -> TypeIs[Pep484612646TypeArgPacked]:  # pyright: ignore
    '''
    :data:`True` only if the passed type hint is a **packed type parameter**
    (i.e., :pep:`484`-compliant type variable, pep:`612`-compliant parameter
    specification, or :pep:`646`-compliant type variable tuples).

    Parameters
    ----------
    hint : Hint
        Type hint to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this hint is a packed type parameter.
    '''

    # Return true only if this hint is a packed type parameter.
    return isinstance(hint, HintPep484612646TypeArgPackedTypes)

# ....................{ GETTERS                            }....................
def get_hint_pep484612646_typearg_packed_name(
    # Mandatory parameters.
    hint: Pep484612646TypeArgPacked,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484612646Exception,
    exception_prefix: str = '',
) -> str:
    '''
    Unqualified basename of the passed **packed type parameter** (i.e.,
    :pep:`484`-compliant type variable, pep:`612`-compliant parameter
    specification, or :pep:`646`-compliant type variable tuples).

    Parameters
    ----------
    hint : Pep484612646TypeArgPacked
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

    # If this hint is *NOT* a packed type parameter, raise an exception.
    die_unless_hint_pep484612646_typearg_packed(
        hint=hint,  # pyright: ignore
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # Else, this hint is a packed type parameter.

    # Return the name of this type parameter. Thankfully, *ALL* type parameters
    # generically conform to this simplistic API. We give minor praise.
    return hint.__name__  # type: ignore[union-attr]
