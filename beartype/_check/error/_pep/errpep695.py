#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`695`-compliant **type alias violation describers** (i.e.,
functions returning human-readable strings explaining violations of
:pep:`695`-compliant type aliases).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.error.errcause import ViolationCause
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignPep695TypeAliasSubscripted)
from beartype._util.hint.pep.proposal.pep695 import (
    get_hint_pep695_subscripted_typevar_to_hint)

# ....................{ FINDERS                            }....................
def find_cause_pep695_type_alias_subscripted(
    cause: ViolationCause) -> ViolationCause:
    '''
    Output cause describing whether the pith of the passed input cause either
    satisfies or violates the :pep:`695`-compliant **subscripted type alias**
    (i.e., object created by subscripting an object created by a statement of
    the form ``type {alias_name}[{type_var}] = {alias_value}`` by one or more
    child type hints) of that cause.

    Parameters
    ----------
    cause : ViolationCause
        Input cause providing this data.

    Returns
    -------
    ViolationCause
        Output cause type-checking this data.
    '''
    assert isinstance(cause, ViolationCause), f'{repr(cause)} not cause.'
    assert cause.hint_sign is HintSignPep695TypeAliasSubscripted, (
        f'{cause.hint_sign} not "HintSignPep695TypeAliasSubscripted".')

    # Reduce this subscripted type alias to:
    # * The semantically useful unsubscripted type alias originating this
    #   semantically useless subscripted type alias.
    # * The type variable lookup table mapping all type variables parametrizing
    #   this alias to all non-type variable hints subscripting this alias.
    hint_child, typevar_to_hint_child = (
        get_hint_pep695_subscripted_typevar_to_hint(
            hint=cause.hint, exception_prefix=cause.exception_prefix))  # type: ignore[arg-type]

    # Full type variable lookup table uniting...
    typevar_to_hint_curr = (
        # The type variable lookup table describing all transitive parent hints
        # of this alias *AND*...
        cause.typevar_to_hint |  # type: ignore[operator]
        # The type variable lookup table describing this alias.
        #
        # Note that this table is intentionally the second rather than first
        # operand of this "|" operation, efficiently ensuring that type
        # variables mapped by this alias take precedence over type variables
        # mapped by transitive parent hints of this alias.
        typevar_to_hint_child
    )

    # Silently ignore this semantically useless subscripted type alias in favour
    # of this semantically useful unsubscripted type alias by trivially
    # replacing *ALL* hint metadata describing the former with the latter.
    cause_return = cause.permute(
        hint=hint_child, typevar_to_hint=typevar_to_hint_curr).find_cause()

    # Return this output cause.
    return cause_return
