#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`593`-compliant **type hint violation describers** (i.e.,
functions returning human-readable strings explaining violations of
:pep:`593`-compliant :attr:`typing.Annotated` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeCallHintPepRaiseException
from beartype.typing import Optional
from beartype._data.hint.pep.sign.datapepsigns import HintSignAnnotated
from beartype._decor._error._errorsleuth import CauseSleuth
from beartype._decor._error._errortext import represent_pith
from beartype._util.hint.pep.proposal.utilpep593 import (
    get_hint_pep593_metadata,
    get_hint_pep593_metahint,
)
from beartype._util.text.utiltextmagic import CODE_INDENT_1

# ....................{ GETTERS                            }....................
def get_cause_or_none_annotated(sleuth: CauseSleuth) -> Optional[str]:
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed :pep:`593`-compliant :mod:`beartype`-specific
    **metahint** (i.e., type hint annotating a standard class with one or more
    :class:`beartype.vale._core._valecore.BeartypeValidator` objects, each
    produced by subscripting the :class:`beartype.vale.Is` class or a subclass
    of that class) if this object actually fails to satisfy this hint *or*
    ``None`` otherwise (i.e., if this object satisfies this hint).

    Parameters
    ----------
    sleuth : CauseSleuth
        Type-checking error cause sleuth.
    '''
    assert isinstance(sleuth, CauseSleuth), f'{repr(sleuth)} not cause sleuth.'
    assert sleuth.hint_sign is HintSignAnnotated, (
        f'{sleuth.hint_sign} not HintSignAnnotated.')

    # Defer heavyweight imports.
    from beartype.vale._core._valecore import BeartypeValidator

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
    for hint_validator in get_hint_pep593_metadata(sleuth.hint):
        # If this object is *NOT* beartype-specific, raise an exception.
        #
        # Note that this object should already be beartype-specific, as the
        # @beartype decorator enforces this constraint at decoration time.
        if not isinstance(hint_validator, BeartypeValidator):
            raise _BeartypeCallHintPepRaiseException(
                f'{sleuth.exception_prefix}PEP 593 type hint '
                f'{repr(sleuth.hint)} argument {repr(hint_validator)} '
                f'not beartype validator '
                f'(i.e., "beartype.vale.Is*[...]" object).'
            )
        # Else, this object is beartype-specific.

        # If this pith fails to satisfy this validator and is thus the cause of
        # this failure...
        if not hint_validator.is_valid(sleuth.pith):
            #FIXME: Unit test this up, please.
            # Human-readable string diagnosing this failure.
            hint_diagnosis = hint_validator.get_diagnosis(
                obj=sleuth.pith,
                indent_level_outer=CODE_INDENT_1,
                indent_level_inner='',
            )

            # Return a human-readable string describing this failure.
            return (
                f'{represent_pith(sleuth.pith)} violates validator '
                f'{repr(hint_validator)}:\n'
                f'{hint_diagnosis}'
            )
        # Else, this pith satisfies this validator. Ergo, this validator is
        # *NOT* the cause of this failure. Silently continue to the next.

    # Return "None", as this pith satisfies both this non-"typing" class itself
    # *AND* all validators annotating that class, implying this pith to deeply
    # satisfy this metahint.
    return None
