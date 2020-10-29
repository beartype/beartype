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
    get_hint_pep484_generic_bases_or_none)
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
    assert sleuth.hint_sign is Generic, (
        f'{repr(sleuth.hint_sign)} not generic.')
    assert isinstance(sleuth.hint, type), f'{repr(sleuth.hint)} not class.'

    # If this pith is *NOT* an instance of this generic, defer to the getter
    # function handling non-"typing" classes.
    if not isinstance(sleuth.pith, sleuth.hint):
        return get_cause_or_none_type(sleuth)
    # Else, this pith is an instance of this generic.

    # Tuple of the one or more unerased pseudo-superclasses (i.e., "typing"
    # objects originally listed as superclasses prior to their implicit type
    # erasure by the "typing" module) subclassed by this generic.
    hint_bases = get_hint_pep484_generic_bases_or_none(sleuth.hint)

    # Assert this generic subclassed at least one pseudo-superclass.
    assert hint_bases, (
        f'PEP generic {repr(sleuth.hint)} subclasses no superclasses.')

    # For each pseudo-superclass of this generic...
    for hint_base in hint_bases:
        # If this pseudo-superclass is either...
        if (
            # An actual superclass, this pseudo-superclass is effectively
            # ignorable. Why? Because the isinstance() call above already
            # type-checked this pith against the generic subclassing this
            # superclass and thus this superclass as well.
            isinstance(hint_base, type) or
            # Explicitly ignorable...
            is_hint_ignorable(hint_base)
        # Then this pseudo-superclass is ignorable. In this case, skip to the
        # next pseudo-superclass.
        ):
            continue
        # Else, this pseudo-superclass is unignorable.

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
