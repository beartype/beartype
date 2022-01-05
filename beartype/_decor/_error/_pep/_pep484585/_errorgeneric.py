#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant generic type hint exception raisers** (i.e., functions
raising human-readable exceptions called by :mod:`beartype`-decorated callables
on the first invalid parameter or return value failing a type-check against the
PEP-compliant generic type hint annotating that parameter or return).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._data.hint.pep.sign.datapepsigns import HintSignGeneric
from beartype._decor._error._errortype import (
    get_cause_or_none_instance_type)
from beartype._decor._error._errorsleuth import CauseSleuth
from beartype._util.hint.pep.proposal.pep484585.utilpep484585generic import (
    get_hint_pep484585_generic_bases_unerased,
    get_hint_pep484585_generic_type,
)
from beartype._util.hint.pep.proposal.pep484.utilpep484generic import (
    get_hint_pep484_generic_base_erased_from_unerased)
from beartype._util.hint.pep.proposal.utilpep585 import is_hint_pep585_builtin
from beartype._util.hint.pep.utilpeptest import is_hint_pep_typing
from beartype._util.hint.utilhinttest import is_hint_ignorable
from typing import Optional

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS                           }....................
def get_cause_or_none_generic(sleuth: CauseSleuth) -> Optional[str]:
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed :pep:`484`- or :pep:`585`-compliant **generic**
    (i.e., type hint subclassing a combination of one or more of the
    :mod:`typing.Generic` superclass, the :mod:`typing.Protocol` superclass,
    and/or other :mod:`typing` non-class pseudo-superclasses) if this object
    actually fails to satisfy this hint *or* ``None`` otherwise (i.e., if this
    object satisfies this hint).

    Parameters
    ----------
    sleuth : CauseSleuth
        Type-checking error cause sleuth.
    '''
    assert isinstance(sleuth, CauseSleuth), f'{repr(sleuth)} not cause sleuth.'
    assert sleuth.hint_sign is HintSignGeneric, (
        f'{repr(sleuth.hint_sign)} not generic.')

    # If this hint is *NOT* a class, reduce this hint to the generic class
    # originating this hint if any. See the is_hint_pep484_generic() tester.
    sleuth.hint = get_hint_pep484585_generic_type(sleuth.hint)

    # Human-readable string describing the failure of this pith to be an
    # instance of this class if this pith is not an instance of this class *OR*
    # "None" otherwise.
    pith_cause = get_cause_or_none_instance_type(sleuth)

    # If this pith is *NOT* an instance of this class, return this string.
    if pith_cause is not None:
        return pith_cause
    # Else, this pith is an instance of this class.

    # Tuple of the one or more unerased pseudo-superclasses originally
    # subclassed by this generic.
    hint_bases = get_hint_pep484585_generic_bases_unerased(
        hint=sleuth.hint, exception_prefix=sleuth.exception_prefix)

    # For each such pseudo-superclass...
    for hint_base in hint_bases:
        # If this pseudo-superclass is an actual superclass, this
        # pseudo-superclass is effectively ignorable. Why? Because the
        # isinstance() call above already type-checked this pith against the
        # class subclassing this superclass and thus this superclass as well.
        # In this case, skip to the next pseudo-superclass.
        if isinstance(hint_base, type):
            continue
        # Else, this pseudo-superclass is *NOT* an actual class.
        #
        # If this pseudo-superclass is neither...
        elif not (
            # A PEP 585-compliant type hint *NOR*...
            is_hint_pep585_builtin(hint_base) and
            # A PEP-compliant type hint defined by the "typing" module...
            is_hint_pep_typing(hint_base)
        ):
            # Reduce this pseudo-superclass to the real superclass originating
            # this pseudo-superclass. See the "_pephint" submodule.
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
        # substring describing this failure by embedding this failure in a
        # longer string.
        if pith_base_cause is not None:
            # print(f'tuple pith: {sleuth_copy.pith}\ntuple hint child: {sleuth_copy.hint}\ncause: {pith_item_cause}')
            return f'generic base {repr(hint_base)} {pith_base_cause}'
        # Else, this pseudo-superclass is *NOT* the cause of this failure.
        # Silently continue to the next.

    # Return "None", as this pith satisfies both this generic itself *AND* all
    # pseudo-superclasses subclassed by this generic, implying this pith to
    # deeply satisfy this hint.
    return None
