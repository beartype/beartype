#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`557`-compliant type hint utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep557Exception
from beartype._data.datatyping import TypeException
from beartype._data.hint.pep.sign.datapepsigns import HintSignDataclassInitVar

# ....................{ GETTERS                           }....................
def get_hint_pep557_initvar_arg(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep557Exception,
    exception_prefix: str = '',
) -> object:
    '''
    PEP-compliant child type hint subscripting the passed PEP-compliant parent
    type hint describing a **dataclass-specific initialization-only instance
    variable** (i.e., instance of the :pep:`557`-compliant
    :class:`dataclasses.InitVar` class introduced by Python 3.8.0).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Type hint to be inspected.
    exception_cls : TypeException
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep557Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    ----------
    object
        PEP-compliant child type hint subscripting this parent type hint.

    Raises
    ----------
    BeartypeDecorHintPep557Exception
        If this object does *not* describe a dataclass-specific
        initialization-only instance variable.
    '''
    
    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none

    # Sign uniquely identifying this hint if this hint is identifiable *OR*
    # "None" otherwise.
    hint_sign = get_hint_pep_sign_or_none(hint)

    # If this hint does *NOT* describe a dataclass-specific
    # initialization-only instance variable, raise an exception.
    if hint_sign is not HintSignDataclassInitVar:
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} not '
            f'PEP 557-compliant "dataclasses.TypeVar" instance.'
        )
    # Else, this hint describes such a variable.

    # Return the child type hint subscripting this parent type hint. Yes,
    # this hint exposes this child via a non-standard instance variable
    # rather than the "__args__" dunder tuple standardized by PEP 484.
    return hint.type  # type: ignore[attr-defined]
