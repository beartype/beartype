#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint call-time utilities** (i.e., callables
operating on PEP-compliant type hints intended to be called by dynamically
generated wrapper functions wrapping decorated callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar._roarexc import _BeartypeCallHintPepRaiseException
from beartype._decor._error._errorsleuth import CauseSleuth
from beartype._data.hint.pep.sign.datapepsigns import HintSignForwardRef
from beartype._util.hint.nonpep.utilnonpeptest import (
    die_unless_hint_nonpep_tuple)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_type_stdlib_or_none)
from beartype._util.hint.utilhintget import (
    get_hint_forwardref_classname_relative_to_object)
from beartype._util.mod.utilmodimport import import_module_attr
from beartype._util.text.utiltextcause import (
    get_cause_object_not_type,
    get_cause_object_not_types,
)
from typing import Optional

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS ~ forwardref              }....................
def get_cause_or_none_forwardref(sleuth: CauseSleuth) -> Optional[str]:
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed **forward reference type hint** (i.e., string whose
    value is the name of a user-defined class which has yet to be defined) if
    this object actually fails to satisfy this hint *or* ``None`` otherwise
    (i.e., if this object satisfies this hint).

    Parameters
    ----------
    sleuth : CauseSleuth
        Type-checking error cause sleuth.
    '''
    assert isinstance(sleuth, CauseSleuth), f'{repr(sleuth)} not cause sleuth.'
    assert sleuth.hint_sign is HintSignForwardRef, (
        f'Sign {repr(sleuth.hint_sign)} not forward reference.')

    # Fully-qualified classname referred to by this forward reference relative
    # to the decorated callable.
    hint_forwardref_classname = get_hint_forwardref_classname_relative_to_object(
        hint=sleuth.hint, obj=sleuth.func)

    # User-defined class dynamically imported from this classname.
    hint_forwardref_class = import_module_attr(
        module_attr_name=hint_forwardref_classname,
        module_attr_label=(
            f'{sleuth.exception_label} forward reference type hint'),
        exception_cls=_BeartypeCallHintPepRaiseException,
    )

    # Defer to the getter function handling non-"typing" classes. Neato!
    return get_cause_or_none_type(sleuth.permute(hint=hint_forwardref_class))

# ....................{ GETTERS ~ type                    }....................
def get_cause_or_none_type(sleuth: CauseSleuth) -> Optional[str]:
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to be an instance of the passed isinstanceable class if this object is
    *not* an instance of this class *or* ``None`` otherwise (i.e., if this
    object is an instance of this class).

    Parameters
    ----------
    sleuth : CauseSleuth
        Type-checking error cause sleuth.
    '''
    assert isinstance(sleuth, CauseSleuth), f'{repr(sleuth)} not cause sleuth.'

    # If this hint is *NOT* a type, raise an exception.
    if not isinstance(sleuth.hint, type):
        raise _BeartypeCallHintPepRaiseException(
            f'{sleuth.exception_label} non-PEP type hint '
            f'{repr(sleuth.hint)} unsupported '
            f'(i.e., neither PEP-compliant nor standard class).'
        )
    # Else, this hint is a type.
    #
    # If this pith is an instance of this type, return "None".
    elif isinstance(sleuth.pith, sleuth.hint):
        return None
    # Else, this pith is *NOT* an instance of this type.

    # Return a substring describing this failure intended to be embedded in a
    # longer string.
    return get_cause_object_not_type(pith=sleuth.pith, hint=sleuth.hint)


def get_cause_or_none_type_stdlib(sleuth: CauseSleuth) -> Optional[str]:
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
    hint_type_stdlib = get_hint_pep_type_stdlib_or_none(sleuth.hint)

    # If this hint does *NOT* originate from such a type, raise an exception.
    if hint_type_stdlib is None:
        raise _BeartypeCallHintPepRaiseException(
            f'{sleuth.exception_label} type hint '
            f'{repr(sleuth.hint)} not originated from an origin type.'
        )
    # Else, this hint originates from such a type.

    # Defer to the getter function handling non-"typing" classes. Presto!
    return get_cause_or_none_type(sleuth.permute(hint=hint_type_stdlib))

# ....................{ GETTERS ~ types                   }....................
def get_cause_or_none_types(sleuth: CauseSleuth) -> Optional[str]:
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to be an instance of one or more isinstanceable classes in the passed tuple
    of classes if this object is *not* an instance of such a class *or*
    ``None`` otherwise (i.e., if this object is an instance of such a class).

    Parameters
    ----------
    sleuth : CauseSleuth
        Type-checking error cause sleuth.
    '''
    assert isinstance(sleuth, CauseSleuth), f'{repr(sleuth)} not cause sleuth.'

    # If this hint is *NOT* a tuple union, raise an exception.
    die_unless_hint_nonpep_tuple(
        hint=sleuth.hint,
        hint_label=sleuth.exception_label,
        exception_cls=_BeartypeCallHintPepRaiseException,
    )
    # Else, this hint is a tuple union.

    # If this pith is an instance of one or more types in this tuple union,
    # return "None".
    if isinstance(sleuth.pith, sleuth.hint):
        return None
    # Else, this pith is an instance of *NO* types in this tuple union.

    # Return a substring describing this failure intended to be embedded in a
    # longer string.
    return get_cause_object_not_types(pith=sleuth.pith, hint=sleuth.hint)
