#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint call-time utilities** (i.e., callables
operating on PEP-compliant type hints intended to be called by dynamically
generated wrapper functions wrapping decorated callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.hint.utilhintget import get_hint_type_origin
from beartype._util.hint.pep.utilhintpepdata import (
    TYPING_ATTR_TO_TYPE_ORIGIN)
from beartype._util.hint.pep.error._utilhintpeperrorsleuth import CauseSleuth
from beartype._util.text.utiltextrepr import get_object_representation

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS                           }....................
def get_cause_or_none_type(sleuth: CauseSleuth) -> 'Optional[str]':
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to be an instance of the passed non-:mod:`typing` class if this object is
    *not* an instance of this class *or* ``None`` otherwise (i.e., if this
    object is an instance of this class).

    Parameters
    ----------
    sleuth : CauseSleuth
        Type-checking error cause sleuth.
    '''
    assert isinstance(sleuth, CauseSleuth), f'{repr(sleuth)} not cause sleuth.'
    assert isinstance(sleuth.hint, type), (
        f'{repr(sleuth.hint)} not non-"typing" type.')

    # If this object is an instance of this type, return "None".
    if isinstance(sleuth.pith, sleuth.hint):
        return None
    # Else, this object is *NOT* an instance of this type.

    # Truncated representation of this object.
    pith_repr = get_object_representation(sleuth.pith)

    # Return a substring describing this failure intended to be embedded in a
    # longer string.
    return f'value {pith_repr} not {sleuth.hint.__name__}'


def get_cause_or_none_type_origin(sleuth: CauseSleuth) -> 'Optional[str]':
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed **PEP-compliant originative type hint** (i.e.,
    PEP-compliant type hint originating from a non-:mod:`typing` class) if this
    object actually fails to satisfy this hint *or* ``None`` otherwise (i.e.,
    if this object satisfies this hint).

    Parameters
    ----------
    sleuth : CauseSleuth
        Type-checking error cause sleuth.
    '''
    assert isinstance(sleuth, CauseSleuth), f'{repr(sleuth)} not cause sleuth.'
    assert sleuth.hint_attr in TYPING_ATTR_TO_TYPE_ORIGIN, (
        f'{repr(sleuth.hint)} not isinstance()-able.')

    # Non-"typing" class originating this attribute (e.g., "list" for "List").
    hint_type_origin = get_hint_type_origin(sleuth.hint_attr)

    # Defer to the getter function handling non-"typing" classes. Presto!
    return get_cause_or_none_type(sleuth.permute(hint=hint_type_origin))
