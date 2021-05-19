#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`586`-compliant :attr:`typing.Literal` **type hint exception
raisers** (i.e., functions raising human-readable exceptions called by
:mod:`beartype`-decorated callables on the first invalid parameter or return
value failing a type-check against the :pep:`586`-compliant
:attr:`typing.Literal` type hint annotating that parameter or return).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._decor._error._errorsleuth import CauseSleuth
from beartype._util.hint.data.pep.utilhintdatapepsign import (
    HINT_PEP586_SIGN_LITERAL)
from beartype._util.text.utiltextcause import get_cause_object_representation
from typing import Optional

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS                           }....................
def get_cause_or_none_literal(sleuth: CauseSleuth) -> Optional[str]:
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed :pep:`586`-compliant :mod:`beartype`-specific
    **literal** (i.e., :attr:`typing.Literal` type hint) if this object
    actually fails to satisfy this hint *or* ``None`` otherwise (i.e., if this
    object satisfies this hint).

    Parameters
    ----------
    sleuth : CauseSleuth
        Type-checking error cause sleuth.
    '''
    assert isinstance(sleuth, CauseSleuth), f'{repr(sleuth)} not cause sleuth.'
    assert sleuth.hint_sign is HINT_PEP586_SIGN_LITERAL, (
        f'{repr(sleuth.hint_sign)} not literal.')

    # For each literal object subscripting this hint...
    for hint_literal in sleuth.hint_childs:
        # Human-readable string describing the failure of this pith to be an
        # instance of the same type as this literal if this pith is an instance
        # of a differing type *OR* "None" otherwise.
        #
        # Note that PEP 586 explicitly requires this pith to be iteratively
        # validated to be an instance of the same type as this literal *BEFORE*
        # validated as equal to this literal.
        pith_cause = sleuth.permute(
            pith=sleuth.pith, hint=type(hint_literal)).get_cause_or_none()

        # If this pith is an instance of a differing type, return this string.
        if pith_cause is not None:
            return pith_cause
        # Else, this pith is an instance of the same type as this literal.
        #
        # If this pith is unequal to this literal and is thus the cause of this
        # failure, return a human-readable string describing this failure.
        elif sleuth.pith != hint_literal:
            return (
                f'{get_cause_object_representation(sleuth.pith)} != literal '
                f'{repr(hint_literal)}.'
            )
        # Else, this pith is equal to this literal. Ergo, this literal is *NOT*
        # the cause of this failure. Silently continue to the next.

    # Return "None", as this pith is both of the same type *AND* equal to all
    # literal objects subscripting this hint, implying this pith to deeply
    # satisfy this hint.
    return None
