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
from beartype._decor._code._pep._error._peperrortype import (
    get_cause_or_none_type)
from beartype._decor._code._pep._error._peperrorsleuth import CauseSleuth
from beartype._util.hint.utilhinttest import is_hint_ignorable
from beartype._util.hint.pep.proposal.utilhintpep484 import (
    get_hint_pep484_generic_base_erased_from_unerased)
from beartype._util.hint.pep.utilhintpeptest import is_hint_pep_typing
from typing import Generic

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS                           }....................
def get_cause_or_none_generic(sleuth: CauseSleuth) -> 'Optional[str]':
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed `PEP 484`_-compliant **generic** (i.e., type hint
    subclassing a combination of one or more of the :mod:`typing.Generic`
    superclass, the :mod:`typing.Protocol` superclass, and/or other
    :mod:`typing` non-class pseudo-superclasses) if this object actually fails
    to satisfy this hint *or* ``None`` otherwise (i.e., if this object
    satisfies this hint).

    Parameters
    ----------
    sleuth : CauseSleuth
        Type-checking error cause sleuth.
    '''
    assert isinstance(sleuth, CauseSleuth), f'{repr(sleuth)} not cause sleuth.'
    assert isinstance(sleuth.hint, type), f'{repr(sleuth.hint)} not class.'
    assert sleuth.hint_sign is Generic, (
        f'{repr(sleuth.hint_sign)} not generic.')

    # If this pith is *NOT* an instance of this generic, defer to the getter
    # function handling non-"typing" classes.
    if not isinstance(sleuth.pith, sleuth.hint):
        return get_cause_or_none_type(sleuth)
    # Else, this pith is an instance of this generic.

    # For each pseudo-superclass of this generic...
    for hint_base in sleuth.hint_childs:
        # If this pseudo-superclass is an actual superclass, this
        # pseudo-superclass is effectively ignorable. Why? Because the
        # isinstance() call above already type-checked this pith against the
        # generic subclassing this superclass and thus this superclass as well.
        # In this case, skip to the next pseudo-superclass.
        if isinstance(hint_base, type):
            continue
        # Else, this pseudo-superclass is *NOT* an actual class.
        #
        # If this pseudo-superclass is *NOT* defined by the "typing" module
        # (and is thus user-defined), reduce this pseudo-superclass to a real
        # superclass originating this pseudo-superclass. See related commentary
        # in the "_pephint" submodule.
        elif not is_hint_pep_typing(hint_base):
            hint_base = get_hint_pep484_generic_base_erased_from_unerased(
                hint_base)
        # Else, this pseudo-superclass is defined by the "typing" module.

        # If this superclass is ignorable, do so.
        if is_hint_ignorable(hint_base):
            continue
        # Else, this superclass is unignorable.

        # Human-readable string describing the failure of this pith to satisfy
        # this pseudo-superclass if this pith actually fails to satisfy
        # this pseudo-superclass *or* "None" otherwise.
        # print(f'tuple pith: {pith_item}\ntuple hint child: {hint_child}')
        pith_base_cause = sleuth.permute(hint=hint_base).get_cause_or_none()

        # If this pseudo-superclass is the cause of this failure, return a
        # substring describing this failure by embedding this failure (itself
        # intended to be embedded in a longer string).
        if pith_base_cause is not None:
            # print(f'tuple pith: {sleuth_copy.pith}\ntuple hint child: {sleuth_copy.hint}\ncause: {pith_item_cause}')
            return f'generic base {repr(hint_base)} {pith_base_cause}'
        # Else, this pseudo-superclass is *NOT* the cause of this failure.
        # Silently continue to the next.

    # Return "None", as this pith satisfies both this generic itself *AND* all
    # pseudo-superclasses subclassed by this generic, implying this pith to
    # deeply satisfy this hint.
    return None
