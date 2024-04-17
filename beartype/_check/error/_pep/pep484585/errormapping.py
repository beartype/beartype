#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`484`- and :pep:`585`-compliant **mapping type hint violation
describers** (i.e., functions returning human-readable strings explaining
violations of :pep:`484`- and :pep:`585`-compliant mapping type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype import BeartypeStrategy
from beartype.typing import (
    Iterable,
    Tuple,
    Hashable,
)
from beartype._data.hint.pep.sign.datapepsignset import HINT_SIGNS_MAPPING
from beartype._check.error._errorcause import ViolationCause
from beartype._check.error._errortype import find_cause_type_instance_origin
from beartype._util.text.utiltextprefix import prefix_pith_type
from beartype._util.text.utiltextrepr import represent_pith

# ....................{ FINDERS                            }....................
def find_cause_mapping(cause: ViolationCause) -> ViolationCause:
    '''
    Output cause describing whether the pith of the passed input cause either
    satisfies or violates the **mapping type hint** (i.e., PEP-compliant type
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
    assert cause.hint_sign in HINT_SIGNS_MAPPING, (
        f'{repr(cause.hint)} not mapping hint.')

    # Assert this mapping was subscripted by exactly two arguments. Note that
    # the "typing" module should have already guaranteed this on our behalf.
    assert len(cause.hint_childs) == 2, (
        f'Mapping hint {repr(cause.hint)} subscripted by '
        f'{len(cause.hint_childs)} != 2.')
    # print(f'Validating mapping {repr(cause.pith)}...')

    # Shallow output cause to be returned, type-checking only whether this path
    # is an instance of the type originating this hint (e.g., "list" for
    # "list[str]").
    cause_shallow = find_cause_type_instance_origin(cause)

    # If this pith is *NOT* an instance of this type, return this shallow cause.
    if cause_shallow.cause_str_or_none is not None:
        return cause_shallow
    # Else, this pith is an instance of this type and is thus a mapping.
    #
    # If this mapping is empty, all items of this mapping (of which there are
    # none) are valid. This mapping satisfies this hint. Just go with it!
    elif not cause.pith:
        return cause
    # Else, this mapping is non-empty.

    # Child key and value hints subscripting this mapping hint.
    hint_key = cause.hint_childs[0]
    hint_value = cause.hint_childs[1]

    # True only if these hints are unignorable.
    hint_key_unignorable = hint_key is not None
    hint_value_unignorable = hint_value is not None

    # Arbitrary iterator vaguely satisfying the dict.items() protocol,
    # yielding zero or more 2-tuples of the form "(key, value)", where:
    # * "key" is the key of the current key-value pair.
    # * "value" is the value of the current key-value pair.
    pith_items: Iterable[Tuple[Hashable, object]] = None  # type: ignore[assignment]

    # If the only the first key-value pair of this mapping was
    # type-checked by the the parent @beartype-generated wrapper
    # function in O(1) time, type-check only this key-value pair of this
    # mapping in O(1) time as well.
    if cause.conf.strategy is BeartypeStrategy.O1:
        # First key-value pair of this mapping.
        pith_item = next(iter(cause.pith.items()))

        # Tuple containing only this pair.
        pith_items = (pith_item,)
        # print(f'Checking item {pith_item_index} in O(1) time!')
    # Else, all keys of this mapping were type-checked by the parent
    # @beartype-generated wrapper function in O(n) time. In this case,
    # type-check *ALL* indices of this mapping in O(n) time as well.
    else:
        # Iterator yielding all key-value pairs of this mapping.
        pith_items = cause.pith.items()
        # print('Checking mapping in O(n) time!')

    # For each key-value pair of this mapping...
    for pith_key, pith_value in pith_items:
        # If this child key hint is unignorable...
        if hint_key_unignorable:
            # Deep output cause, type-checking whether this key satisfies
            # this child key hint.
            cause_deep = cause.permute(
                pith=pith_key, hint=hint_key).find_cause()

            # If this key is the cause of this failure...
            if cause_deep.cause_str_or_none is not None:
                # Human-readable substring prefixing this failure with
                # metadata describing this key.
                cause_deep.cause_str_or_none = (
                    f'{prefix_pith_type(pith=cause.pith, is_color=True)}'
                    f'key {cause_deep.cause_str_or_none}'
                )

                # Return this cause.
                return cause_deep
            # Else, this key is *NOT* the cause of this failure. Silently
            # continue to this value.
        # Else, this child key hint is ignorable.

        # If this child value hint is unignorable...
        if hint_value_unignorable:
            # Deep output cause, type-checking whether this value satisfies
            # this child value hint.
            cause_deep = cause.permute(
                pith=pith_value, hint=hint_value).find_cause()

            # If this value is the cause of this failure...
            if cause_deep.cause_str_or_none is not None:
                # Human-readable substring prefixing this failure with
                # metadata describing this value.
                cause_deep.cause_str_or_none = (
                    f'{prefix_pith_type(pith=cause.pith, is_color=True)}'
                    f'key {represent_pith(pith_key)} '
                    f'value {cause_deep.cause_str_or_none}'
                )

                # Return this cause.
                return cause_deep
            # Else, this value is *NOT* the cause of this failure. Silently
            # continue to the key-value pair.
        # Else, this child value hint is ignorable.

    # Return this cause as is; all items of this mapping are valid, implying
    # this mapping to deeply satisfy this hint.
    return cause
