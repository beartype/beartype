#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`593`-compliant :class:`typing.Annotated` **type hint
exception raisers** (i.e., functions raising human-readable exceptions called
by :mod:`beartype`-decorated callables on the first invalid parameter or return
value failing a type-check against the :pep:`593`-compliant
:class:`typing.Annotated` type hint annotating that parameter or return).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar._roarexc import _BeartypeCallHintPepRaiseException
from beartype._decor._error._errorsleuth import CauseSleuth
from beartype._data.hint.pep.sign.datapepsigns import HintSignAnnotated
from beartype._util.hint.pep.proposal.utilpep593 import (
    get_hint_pep593_metadata,
    get_hint_pep593_metahint,
)
from beartype._util.text.utiltextrepr import represent_object
from beartype._vale._valesub import _SubscriptedIs
from typing import Optional

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS                           }....................
def get_cause_or_none_annotated(sleuth: CauseSleuth) -> Optional[str]:
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed :pep:`593`-compliant :mod:`beartype`-specific
    **metahint** (i.e., type hint annotating a standard class with one or more
    :class:`_SubscriptedIs` objects, each produced by subscripting the
    :class:`beartype.vale.Is` class or a subclass of that class) if this object
    actually fails to satisfy this hint *or* ``None`` otherwise (i.e., if this
    object satisfies this hint).

    Parameters
    ----------
    sleuth : CauseSleuth
        Type-checking error cause sleuth.
    '''
    assert isinstance(sleuth, CauseSleuth), f'{repr(sleuth)} not cause sleuth.'
    assert sleuth.hint_sign is HintSignAnnotated, (
        f'{repr(sleuth.hint_sign)} not HintSignAnnotated.')

    # PEP-compliant type hint annotated by this metahint.
    metahint = get_hint_pep593_metahint(sleuth.hint)

    # Human-readable string describing the failure of this pith to satisfy this
    # hint if this pith fails to satisfy this hint *or* "None" otherwise.
    pith_cause = sleuth.permute(
        pith=sleuth.pith, hint=metahint).get_cause_or_none()

    # If this pith fails to satisfy this hint, return this cause as is.
    if pith_cause is not None:
        return pith_cause
    # Else, this pith satisfies this hint.

    # For each arbitrary object annotating this metahint...
    for hint_metadatum in get_hint_pep593_metadata(sleuth.hint):
        # If this object is *NOT* beartype-specific, raise an exception.
        #
        # Note that this object should already be beartype-specific, as the
        # @beartype decorator enforces this constraint at decoration time.
        if not isinstance(hint_metadatum, _SubscriptedIs):
            raise _BeartypeCallHintPepRaiseException(
                f'{sleuth.exception_label} PEP 593 type hint '
                f'{repr(sleuth.hint)} argument {repr(hint_metadatum)} not '
                f'not subscription of "beartype.vale.Is*" class.'
            )
        # Else, this object is beartype-specific.

        # If this pith fails to satisfy this validator and is thus the cause of
        # this failure, return a human-readable string describing this failure.
        if not hint_metadatum.is_valid(sleuth.pith):
            return (
                f'{represent_object(sleuth.pith)} violates '
                f'validator {repr(hint_metadatum)}.'
            )
        # Else, this pith satisfies this validator. Ergo, this validator is
        # *NOT* the cause of this failure. Silently continue to the next.

    # Return "None", as this pith satisfies both this non-"typing" class itself
    # *AND* all validators annotating that class, implying this pith to deeply
    # satisfy this metahint.
    return None
