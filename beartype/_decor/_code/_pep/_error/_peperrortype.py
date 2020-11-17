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
from beartype.roar import _BeartypeCallHintPepRaiseException
from beartype._decor._code._pep._error._peperrorsleuth import CauseSleuth
from beartype._util.hint.data.pep.proposal.utilhintdatapep484 import (
    HINT_PEP484_BASE_FORWARDREF)
from beartype._util.hint.utilhintget import (
    get_hint_forwardref_classname_relative_to_obj)
from beartype._util.hint.pep.proposal.utilhintpep544 import (
    is_hint_pep544_protocol)
from beartype._util.hint.pep.utilhintpepget import (
    get_hint_pep_type_origin_or_none)
from beartype._util.py.utilpymodule import import_module_attr
from beartype._util.text.utiltextrepr import get_object_representation
from beartype._util.utilobject import get_object_classname

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS ~ forwardref              }....................
def get_cause_or_none_forwardref(sleuth: CauseSleuth) -> 'Optional[str]':
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
    assert sleuth.hint_sign is HINT_PEP484_BASE_FORWARDREF, (
        f'PEP type hint sign {repr(sleuth.hint_sign)} not forward reference.')

    # Fully-qualified classname referred to by this forward reference relative
    # to the decorated callable.
    hint_forwardref_classname = get_hint_forwardref_classname_relative_to_obj(
        obj=sleuth.func, hint=sleuth.hint)

    # User-defined class dynamically imported from this classname.
    hint_forwardref_class = import_module_attr(
        module_attr_name=hint_forwardref_classname,
        exception_label=(
            f'{sleuth.exception_label} forward reference type hint'),
        exception_cls=_BeartypeCallHintPepRaiseException,
    )

    # Defer to the getter function handling non-"typing" classes. Neato!
    return get_cause_or_none_type(sleuth.permute(hint=hint_forwardref_class))

# ....................{ GETTERS ~ type                    }....................
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
        raise _BeartypeCallHintPepRaiseException(
            f'{sleuth.exception_label} non-PEP type hint '
            f'{repr(sleuth.hint)} unsupported '
            f'(i.e., neither PEP-compliant nor standard class).'
        )
    # Else, this hint is a class.
    #
    # Else if this pith is an instance of this class, return "None".
    elif isinstance(sleuth.pith, sleuth.hint):
        return None
    # Else, this pith is *NOT* an instance of this type.

    # Fully-qualified name of this class.
    classname = get_object_classname(sleuth.hint)

    # If this name contains one or more periods, this class is *NOT* a builtin
    # (e.g., "list"). Whereas builtin classes are largely self-explanatory,
    # non-builtin classes are *NOT* and thus benefit from more verbose
    # human-readable explanation. In this case...
    if '.' in classname:
        # If this class is a PEP 544-compliant protocol supporting structural
        # subtyping, describe this protocol.
        if is_hint_pep544_protocol(sleuth.hint):
            classname = (
                f'structural (i.e., duck-typed) instance of '
                f'<protocol "{classname}">'
            )
        # Else if this class is a standard abstract base class (ABC) defined by
        # a stdlib submodule also known to support structural subtyping (e.g.,
        # "collections.abc.Hashable", "contextlib.AbstractContextManager"),
        # describe this ABC.
        #
        # Note that user-defined ABCs do *NOT* generally support structural
        # subtyping. Doing so requires arcane knowledge of undocumented and
        # mostly private "abc.ABCMeta" metaclass internals unlikely to be
        # implemented by third-party developers.
        elif (
            classname.startswith('collections.abc.') or
            classname.startswith('contextlib.')
        ):
            classname = (
                f'structural (i.e., duck-typed) instance of '
                f'<protocol ABC "{classname}">'
            )
        # Else, this is a standard class. In this case, describe this class.
        else:
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
        raise _BeartypeCallHintPepRaiseException(
            f'{sleuth.exception_label} type hint '
            f'{repr(sleuth.hint)} not originated from an origin type.'
        )
    # Else, this hint originates from such a type.

    # Defer to the getter function handling non-"typing" classes. Presto!
    return get_cause_or_none_type(sleuth.permute(hint=hint_type_origin))
