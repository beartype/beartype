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
from beartype._cave._cavefast import TypeParamTypes
from beartype._data.hint.datahinttyping import TypeParam

# ....................{ FACTORIES                          }....................
def get_hint_pep484612646_typeparam_name(
    # Mandatory parameters.
    hint: TypeParam,

    # Optional parameters.
    exception_prefix: str = '',
) -> str:
    '''
    Unqualified basename of the passed **type parameter** (i.e.,
    :pep:`484`-compliant type variable, pep:`612`-compliant parameter
    specification, or :pep:`646`-compliant type variable tuples).

    Parameters
    ----------
    hint : TypeParam
        Type parameter to be inspected.
    exception_prefix : str, optional
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    str
        Unqualified basename of this type parameter.

    Raises
    ------
    BeartypeDecorHintPep484612646Exception
        If this object is *not* a type parameter.
    '''

    # If this hint is *NOT* a type parameter, raise an exception.
    if not isinstance(hint, TypeParamTypes):
        assert isinstance(exception_prefix, str), (
            f'{exception_prefix} not string.')
        raise BeartypeDecorHintPep484612646Exception(
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
