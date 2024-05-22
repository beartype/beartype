#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`484`- and :pep:`585`-compliant **reiterable type hint violation
describers** (i.e., functions returning human-readable strings explaining
violations of :pep:`484`- and :pep:`585`-compliant reiterable type hints,
matching containers satisfying the :class:`collections.abc.Collection` protocol
with guaranteed :math:`O(1)` read-only access to *only* the first item of those
containers).

This private submodule is *not* intended for importation by downstream callers.

See Also
--------
:data:`beartype._data.hint.pep.sign.datapepsignset.HINT_SIGNS_REITERABLE_ARGS_1`
    Further commentary on reiterables.
'''

# ....................{ IMPORTS                            }....................
from beartype import BeartypeStrategy
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_REITERABLE_ARGS_1)
from beartype._check.error._errcause import ViolationCause
from beartype._check.error._errtype import find_cause_type_instance_origin
from beartype._util.text.utiltextansi import color_type
from beartype._util.text.utiltextprefix import prefix_pith_type

# ....................{ FINDERS                            }....................
def find_cause_reiterable(cause: ViolationCause) -> ViolationCause:
    '''
    Output cause describing whether the pith of the passed input cause either
    satisfies or violates the **reiterable type hint** (i.e., PEP-compliant type
    hint accepting exactly two subscripted arguments constraining *all*
    key-value pairs of this pith, which necessarily satisfies the
    :class:`collections.abc.Mapping` protocol) of that cause.

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
    assert cause.hint_sign in HINT_SIGNS_REITERABLE_ARGS_1, (
        f'{repr(cause.hint)} not reiterable hint.')

    # Assert this reiterable was subscripted by exactly one argument. Note that
    # prior logic should have already guaranteed this on our behalf.
    assert len(cause.hint_childs) == 1, (
        f'1-argument reiterable hint {repr(cause.hint)} subscripted by '
        f'{len(cause.hint_childs)} != 1.')

    # Shallow output cause describing the failure of this path to be a shallow
    # instance of the type originating this hint (e.g., "set" for the hint
    # "set[str]") if this pith is not an instance of this type *OR* "None"
    # otherwise (i.e., if this pith is an instance of this type).
    cause_shallow = find_cause_type_instance_origin(cause)

    # If this pith is *NOT* an instance of this type, return this shallow cause.
    if cause_shallow.cause_str_or_none is not None:
        return cause_shallow
    # Else, this pith is an instance of this type and thus a reiterable.

    # Child hint subscripting this parent reiterable hint.
    hint_child = cause.hint_childs[0]

    # If either...
    if (
        # This reiterable is empty, all items of this reiterable (of which there
        # are none) are valid *OR*...
        not cause.pith or
        # This child hint is ignorable...
        hint_child is None
    ):
        # Then this reiterable satisfies this hint. In this case, return the
        # passed cause as is.
        return cause
    # Else, this reiterable is non-empty *AND* this child hint is unignorable.

    # Arbitrary iterator satisfying the enumerate() protocol, yielding zero or
    # more 2-tuples of the form "(item_index, item)", where:
    # * "item_index" is the 0-based index of this item.
    # * "item" is an arbitrary item of this reiterable.
    pith_enumerator = None

    # If the only the first item of this reiterable was type-checked
    # by the parent @beartype-generated wrapper function in O(1) time,
    # type-check only this item of this reiterable in O(1) time as well.
    if cause.conf.strategy is BeartypeStrategy.O1:
        # First item of this reiterable.
        pith_item = next(iter(cause.pith))

        # 0-based index of this item for readability purposes.
        pith_item_index = 0

        # 2-tuple of this index and item in the same order as the 2-tuples
        # returned by the enumerate() builtin.
        pith_enumeratable = (pith_item_index, pith_item)

        # Iterator yielding only this 2-tuple.
        pith_enumerator = iter((pith_enumeratable,))
    # Else, this reiterable was iterated by the parent @beartype-generated
    # wrapper function in O(n) time. In this case, type-check *ALL* items of
    # this reiterable in O(n) time as well.
    else:
        # Iterator yielding all indices and items of this reiterable.
        pith_enumerator = enumerate(cause.pith)

    # For each enumerated item of this reiterable...
    for pith_item_index, pith_item in pith_enumerator:
        # Deep output cause describing the failure of this item to satisfy this
        # child hint if this item violates this child hint *OR* "None" otherwise
        # (i.e., if this item satisfies this child hint).
        cause_deep = cause.permute(pith=pith_item, hint=hint_child).find_cause()

        # If this item is the cause of this failure...
        if cause_deep.cause_str_or_none is not None:
            # Human-readable substring prefixing this failure with metadata
            # describing this item.
            cause_deep.cause_str_or_none = (
                f'{prefix_pith_type(pith=cause.pith, is_color=cause.conf.is_color)}'
                f'index {color_type(text=str(pith_item_index), is_color=cause.conf.is_color)} '
                f'item {cause_deep.cause_str_or_none}'
            )

            # Return this cause.
            return cause_deep
        # Else, this item is *NOT* the cause of this failure. Silently continue
        # to the next item.

    # Return this cause as is; all items of this reiterable are valid, implying
    # this reiterable to deeply satisfy this hint.
    return cause
