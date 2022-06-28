#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant generic type hint exception raisers** (i.e., functions
raising human-readable exceptions called by :mod:`beartype`-decorated callables
on the first invalid parameter or return value failing a type-check against the
PEP-compliant generic type hint annotating that parameter or return).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Optional
from beartype._data.hint.pep.sign.datapepsigns import HintSignGeneric
from beartype._decor._error._errortype import get_cause_or_none_instance_type
from beartype._decor._error._errorsleuth import CauseSleuth
from beartype._util.hint.pep.proposal.pep484585.utilpep484585generic import (
    get_hint_pep484585_generic_type,
    iter_hint_pep484585_generic_bases_unerased_tree,
)

# ....................{ GETTERS                            }....................
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

    # Reduce this hint to the object originating this generic (if any) by
    # stripping all child type hints subscripting this hint from this hint.
    # print(f'[get_cause_or_none_generic] sleuth.pith: {sleuth.pith}')
    # print(f'[get_cause_or_none_generic] sleuth.hint [pre-reduction]: {sleuth.hint}')
    sleuth.hint = get_hint_pep484585_generic_type(
        hint=sleuth.hint, exception_prefix=sleuth.exception_prefix)
    # print(f'[get_cause_or_none_generic] sleuth.hint [post-reduction]: {sleuth.hint}')

    # Human-readable string describing the failure of this pith to be an
    # instance of this type if this pith is not an instance of this type *OR*
    # "None" otherwise (i.e., if this pith is not an instance of this type).
    pith_cause = get_cause_or_none_instance_type(sleuth)

    # If this pith is *NOT* an instance of this type, return this string.
    if pith_cause is not None:
        return pith_cause
    # Else, this pith is an instance of this type.

    #FIXME: *OKAY.* This overly simplistic algorithm has become extremely
    #desynchronized from the considerably less simplistic algorithm performed by
    #"_pephint". To synchronize the two, let's:
    #* Shift the everything in "_pephint" beginning with the line
    #  "hint_bases = acquire_fixed_list(...)" and ending with the end of the
    #  following "while ..." statement into a new
    #  iter_hint_pep484585_generic_bases_unerased_recursive() iterator
    #  implemented as a generator comprehension. Yes, that's probably painfully
    #  slow -- but this simply needs to work and the code duplication here is
    #  clearly encouraging painful and non-trivial issues. Ergo, just do this.
    #* Refactor "_pephint" to defer to that iterator.
    #* Iterate over that iterator below rather than the current logic we're
    #  performing, please.
    #FIXME: After doing so, remove the now useless
    #get_hint_pep484_generic_base_erased_from_unerased() getter, please.

    # For each unignorable unerased transitive pseudo-superclass originally
    # declared as an erased superclass of this generic...
    for hint_child in iter_hint_pep484585_generic_bases_unerased_tree(
        hint=sleuth.hint, exception_prefix=sleuth.exception_prefix):
        # Human-readable string describing the failure of this pith to satisfy
        # this pseudo-superclass if this pith actually fails to satisfy
        # this pseudo-superclass *or* "None" otherwise.
        # print(f'tuple pith: {pith_item}\ntuple hint child: {hint_child}')
        pith_base_cause = sleuth.permute(hint=hint_child).get_cause_or_none()

        # If this pseudo-superclass is the cause of this failure, return a
        # substring describing this failure by embedding this failure in a
        # longer string.
        if pith_base_cause is not None:
            return f'generic base {repr(hint_child)} {pith_base_cause}'
        # Else, this pseudo-superclass is *NOT* the cause of this failure.
        # Silently continue to the next.
        # print(f'[get_cause_or_none_generic] Ignoring satisfied base {hint_child}...')

    # Return "None", as this pith satisfies both this generic itself *AND* all
    # pseudo-superclasses subclassed by this generic, implying this pith to
    # deeply satisfy this hint.
    return None
