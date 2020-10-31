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
from beartype.roar import _BeartypeUtilRaisePepException
from beartype._decor._code._pep._error._peperrorsleuth import CauseSleuth
from beartype._util.hint.pep.utilhintpepget import (
    get_hint_pep_type_origin_or_none)
from beartype._util.text.utiltextrepr import get_object_representation
from beartype._util.utilobject import get_object_type_name_qualified

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

    # If this hint is *NOT* a class, raise an exception.
    if not isinstance(sleuth.hint, type):
        raise _BeartypeUtilRaisePepException(
            f'{sleuth.exception_label} non-PEP type hint '
            f'{repr(sleuth.hint)} unsupported '
            f'(i.e., neither PEP-compliant nor standard class).'
        )

    # If this pith is an instance of this type, return "None".
    if isinstance(sleuth.pith, sleuth.hint):
        return None
    # Else, this pith is *NOT* an instance of this type.

    # Fully-qualified name of this class.
    classname = get_object_type_name_qualified(sleuth.hint)

    # If this name contains one or more periods, this class is *NOT* a builtin
    # (e.g., "list"). Whereas builtin classes are largely self-explanatory,
    # non-builtin classes are *NOT* and thus benefit from more verbose
    # human-readable explanation.
    if '.' in classname:
        classname = f'instance of <class "{classname}">'

    # Truncated representation of this pith.
    pith_repr = get_object_representation(sleuth.pith)

    # Return a substring describing this failure intended to be embedded in a
    # longer string.
    return f'value {pith_repr} not {classname}'


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

    # Origin type originating this hint if any *OR* "None" otherwise.
    hint_type_origin = get_hint_pep_type_origin_or_none(sleuth.hint_sign)

    # If this hint does *NOT* originate from such a type, raise an exception.
    if hint_type_origin is None:
        raise _BeartypeUtilRaisePepException(
            f'{sleuth.exception_label} type hint '
            f'{repr(sleuth.hint)} not originated from an origin type.'
        )
    # Else, this hint originates from such a type.

    # Defer to the getter function handling non-"typing" classes. Presto!
    return get_cause_or_none_type(sleuth.permute(hint=hint_type_origin))
