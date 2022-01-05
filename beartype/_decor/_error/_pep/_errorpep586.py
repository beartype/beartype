#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`586`-compliant :attr:`typing.Literal` **type hint exception
raisers** (i.e., functions raising human-readable exceptions called by
:mod:`beartype`-decorated callables on the first invalid parameter or return
value failing a type-check against the :pep:`586`-compliant
:attr:`typing.Literal` type hint annotating that parameter or return).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._decor._error._errorsleuth import CauseSleuth
from beartype._data.hint.pep.sign.datapepsigns import HintSignLiteral
from beartype._util.hint.pep.proposal.utilpep586 import (
    get_hint_pep586_literals)
from beartype._util.text.utiltextjoin import join_delimited_disjunction
from beartype._util.text.utiltextrepr import represent_object
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
    assert sleuth.hint_sign is HintSignLiteral, (
        f'{repr(sleuth.hint_sign)} not HintSignLiteral.')

    # Tuple of zero or more literal objects subscripting this hint,
    # intentionally replacing the current such tuple due to the non-standard
    # implementation of the third-party "typing_extensions.Literal" factory.
    hint_childs = get_hint_pep586_literals(
        hint=sleuth.hint, exception_prefix=sleuth.exception_prefix)

    # If this pith is equal to any literal object subscripting this hint, this
    # pith satisfies this hint. Specifically, if there exists at least one...
    if any(
        # Literal object subscripting this hint such that...
        (
            # This pith is of the same type as that of this literal *AND*...
            #
            # Note that PEP 586 explicitly requires this pith to be validated
            # to be an instance of the same type as this literal *BEFORE*
            # validated as equal to this literal, due to subtle edge cases in
            # equality comparison that could yield false positives.
            isinstance(sleuth.pith, type(hint_literal)) and
            # This pith is equal to this literal.
            sleuth.pith == hint_literal
        )
        # For each literal object subscripting this hint...
        for hint_literal in hint_childs
    # Then return "None", as this pith deeply satisfies this hint.
    ):
        return None
    # Else, this pith fails to satisfy this hint.

    # Isinstanceable tuple of the types of all literals subscripting this hint.
    hint_literal_types = tuple(
        type(hint_literal) for hint_literal in hint_childs)

    # Human-readable string describing the failure of this pith to be an
    # instance of one or more of these types if this pith is not such an
    # instance *OR* "None" otherwise.
    # Human-readable string describing the failure of this pith to satisfy this
    # hint if this pith fails to satisfy this hint *or* "None" otherwise.
    pith_cause = sleuth.permute(
        pith=sleuth.pith, hint=hint_literal_types).get_cause_or_none()

    # If this pith is *NOT* such an instance, return this string.
    if pith_cause is not None:
        return pith_cause
    # Else, this pith is such an instance and thus shallowly satisfies this
    # hint. Since this pith fails to satisfy this hint, this pith must by
    # deduction be unequal to all literals subscripting this hint.

    # Human-readable comma-delimited disjunction of the machine-readable
    # representations of all literal objects subscripting this hint.
    cause_literals_unsatisfied = join_delimited_disjunction(
        repr(hint_literal) for hint_literal in hint_childs)

    # Return a human-readable string describing this failure.
    return f'{represent_object(sleuth.pith)} != {cause_literals_unsatisfied}.'
