#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint call-time utilities** (i.e., callables
operating on PEP-compliant type hints intended to be called by dynamically
generated wrapper functions wrapping decorated callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeCallHintForwardRefException
from beartype.roar._roarexc import _BeartypeCallHintPepRaiseException
from beartype._cave._cavefast import TestableTypes
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignForwardRef,
    HintSignType,
)
from beartype._decor._error._errorsleuth import CauseSleuth
from beartype._util.cls.utilclstest import is_type_subclass
from beartype._util.cls.pep.utilpep3119 import (
    die_unless_type_isinstanceable,
    die_unless_type_issubclassable,
)
from beartype._util.hint.nonpep.utilnonpeptest import (
    die_unless_hint_nonpep_tuple)
from beartype._util.hint.pep.proposal.pep484585.utilpep484585ref import (
    import_pep484585_forwardref_type_relative_to_object)
from beartype._util.hint.pep.proposal.pep484585.utilpep484585type import (
    get_hint_pep484585_subclass_superclass)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_type_isinstanceable_or_none)
from beartype._util.text.utiltextjoin import join_delimited_disjunction_types
from beartype._util.text.utiltextlabel import label_type
from beartype._util.text.utiltextrepr import represent_object
from typing import Optional

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS ~ instance : type         }....................
def get_cause_or_none_instance_type(sleuth: CauseSleuth) -> Optional[str]:
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

    # If this hint is *NOT* an isinstanceable type, raise an exception.
    die_unless_type_isinstanceable(
        cls=sleuth.hint,
        exception_cls=_BeartypeCallHintPepRaiseException,
        exception_prefix=sleuth.exception_prefix,
    )
    # Else, this hint is an isinstanceable type.

    # If this pith is an instance of this type, return "None".
    if isinstance(sleuth.pith, sleuth.hint):
        return None
    # Else, this pith is *NOT* an instance of this type.

    # Return a substring describing this failure intended to be embedded in a
    # longer string.
    return (
        f'{represent_object(sleuth.pith)} not instance of '
        f'{label_type(sleuth.hint)}'
    )


def get_cause_or_none_instance_type_forwardref(
    sleuth: CauseSleuth) -> Optional[str]:
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
        f'{sleuth.hint_sign} not forward reference.')

    # Class referred to by this forward reference.
    hint_forwardref_type = import_pep484585_forwardref_type_relative_to_object(
        hint=sleuth.hint,
        obj=sleuth.func,
        exception_cls=BeartypeCallHintForwardRefException,
        exception_prefix=sleuth.exception_prefix,
    )

    # Defer to the getter function handling isinstanceable classes. Neato!
    return get_cause_or_none_instance_type(
        sleuth.permute(hint=hint_forwardref_type))


def get_cause_or_none_type_instance_origin(
    sleuth: CauseSleuth) -> Optional[str]:
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

    # Isinstanceable origin type originating this hint if any *OR* "None"
    # otherwise.
    hint_type_origin_isinstanceable = (
        get_hint_pep_type_isinstanceable_or_none(sleuth.hint))

    # If this hint does *NOT* originate from such a type, raise an exception.
    if hint_type_origin_isinstanceable is None:
        raise _BeartypeCallHintPepRaiseException(
            f'{sleuth.exception_prefix}type hint '
            f'{repr(sleuth.hint)} not originated from '
            f'isinstanceable origin type.'
        )
    # Else, this hint originates from such a type.

    # Defer to the getter function handling non-"typing" classes. Presto!
    return get_cause_or_none_instance_type(
        sleuth.permute(hint=hint_type_origin_isinstanceable))

# ....................{ GETTERS ~ instance : types        }....................
def get_cause_or_none_instance_types_tuple(
    sleuth: CauseSleuth) -> Optional[str]:
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
        exception_prefix=sleuth.exception_prefix,
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
    return (
        f'{represent_object(sleuth.pith)} not instance of '
        f'{join_delimited_disjunction_types(sleuth.hint)}'
    )

# ....................{ GETTERS ~ subclass : type         }....................
def get_cause_or_none_subclass_type(sleuth: CauseSleuth) -> Optional[str]:
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to subclass the passed issubclassable superclass if this object is
    *not* a subclass of this superclass *or* ``None`` otherwise (i.e., if this
    object is a subclass of this superclass).

    Parameters
    ----------
    sleuth : CauseSleuth
        Type-checking error cause sleuth.
    '''
    assert isinstance(sleuth, CauseSleuth), f'{repr(sleuth)} not cause sleuth.'
    assert sleuth.hint_sign is HintSignType, (
        f'{sleuth.hint_sign} not HintSignType.')

    # Superclass this pith is required to be a subclass of.
    hint_superclass = get_hint_pep484585_subclass_superclass(
        hint=sleuth.hint, exception_prefix=sleuth.exception_prefix)

    # If this superclass is neither a class nor tuple of classes, this
    # superclass *MUST* by process of elimination and the validation already
    # performed above by the get_hint_pep484585_subclass_superclass() getter be
    # a forward reference to a class. In this case...
    if not isinstance(hint_superclass, TestableTypes):
        # Reduce this superclass to the class referred to by this forward
        # reference.
        hint_superclass = import_pep484585_forwardref_type_relative_to_object(
            hint=hint_superclass,
            obj=sleuth.func,
            exception_cls=BeartypeCallHintForwardRefException,
            exception_prefix=sleuth.exception_prefix,
        )

        # If this superclass is *NOT* issubclassable, raise an exception.
        die_unless_type_issubclassable(
            cls=hint_superclass,
            exception_cls=_BeartypeCallHintPepRaiseException,
            exception_prefix=sleuth.exception_prefix,
        )
        # Else, this superclass is issubclassable.
    # In either case, this superclass is now issubclassable.

    # If this pith subclasses this superclass, return "None".
    if is_type_subclass(sleuth.pith, hint_superclass):
        return None
    # Else, this pith does *NOT* subclass this superclass.

    # Description of this superclasses, defined as either...
    hint_superclass_label = (
        # If this superclass is a class, a description of this class;
        label_type(hint_superclass)
        if isinstance(hint_superclass, type) else
        # Else, this superclass is a tuple of classes. In this case, a
        # description of these classes...
        join_delimited_disjunction_types(hint_superclass)
    )

    # Return a substring describing this failure.
    return (
        f'{represent_object(sleuth.pith)} not subclass of '
        f'{hint_superclass_label}'
    )
