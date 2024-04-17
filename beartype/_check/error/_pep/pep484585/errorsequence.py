#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`484`- and :pep:`585`-compliant **sequence type hint violation
describers** (i.e., functions returning human-readable strings explaining
violations of :pep:`484`- and :pep:`585`-compliant sequence type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.hint.pep.sign.datapepsigns import HintSignTuple
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_SEQUENCE_ARGS_1)
from beartype._check.error._errorcause import ViolationCause
from beartype._check.error._errortype import find_cause_type_instance_origin
from beartype._util.hint.pep.proposal.pep484585.utilpep484585 import (
    is_hint_pep484585_tuple_empty)
from beartype._util.text.utiltextansi import color_type
from beartype._util.text.utiltextprefix import prefix_pith_type
from beartype._util.text.utiltextrepr import represent_pith

# ....................{ FINDERS                            }....................
def find_cause_sequence_args_1(cause: ViolationCause) -> ViolationCause:
    '''
    Output cause describing whether the pith of the passed input cause either
    satisfies or violates the **single-argument variadic sequence type hint**
    (i.e., PEP-compliant type hint accepting exactly one subscripted argument
    constraining *all* items of this pith, which necessarily satisfies the
    :class:`collections.abc.Sequence` protocol with guaranteed :math:`O(1)`
    indexation across all sequence items) of that cause.

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
    assert cause.hint_sign in HINT_SIGNS_SEQUENCE_ARGS_1, (
        f'{repr(cause.hint)} not 1-argument sequence hint.')

    # Assert this sequence was subscripted by exactly one argument. Note that
    # the "typing" module should have already guaranteed this on our behalf.
    assert len(cause.hint_childs) == 1, (
        f'1-argument sequence hint {repr(cause.hint)} subscripted by '
        f'{len(cause.hint_childs)} != 1.')

    # Shallow output cause to be returned, type-checking only whether this path
    # is an instance of the type originating this hint (e.g., "list" for
    # "list[str]").
    cause_shallow = find_cause_type_instance_origin(cause)

    # Return either...
    return (
        # If this pith is *NOT* an instance of this type, this shallow cause;
        cause_shallow
        if cause_shallow.cause_str_or_none is not None else
        # Else, this pith is an instance of this type and is thus a sequence.
        # In this case, defer to this function supporting arbitrary sequences.
        _find_cause_sequence(cause)
    )


def find_cause_tuple(cause: ViolationCause) -> ViolationCause:
    '''
    Output cause describing whether the pith of the passed input cause either
    satisfies or violates the **tuple type hint** (i.e., PEP-compliant type hint
    accepting either zero or more subscripted arguments iteratively constraining
    each item of this fixed-length tuple *or* exactly one subscripted arguments
    constraining *all* items of this variadic tuple) of that cause.

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
    assert cause.hint_sign is HintSignTuple, (
        f'{repr(cause.hint_sign)} not "HintSignTuple".')

    # Shallow output cause to be returned, type-checking only whether this path
    # is an instance of the type originating this hint (e.g., "list" for
    # "list[str]").
    cause_shallow = find_cause_type_instance_origin(cause)

    # If this pith is *NOT* a tuple, return this shallow cause.
    if cause_shallow.cause_str_or_none is not None:
        return cause_shallow
    # Else, this pith is a tuple.
    #
    # If this hint is a tuple...
    elif (
        # Subscripted by exactly two child hints *AND*...
        len(cause.hint_childs) == 2 and
        # The second child hint is just an unquoted ellipsis...
        cause.hint_childs[1] is Ellipsis
    ):
    # Then this hint is of the variadic form "Tuple[{typename}, ...]", typing a
    # tuple accepting a variadic number of items all satisfying the
    # child hint "{typename}". Since this case semantically reduces to a simple
    # sequence, defer to this function supporting arbitrary sequences.
        return _find_cause_sequence(cause)
    # Else, this hint is of the fixed-length form "Tuple[{typename1}, ...,
    # {typenameN}]", typing a tuple accepting a fixed number of items each
    # satisfying a unique child hint.
    #
    # If this hint is the empty fixed-length tuple, validate this pith to be
    # the empty tuple.
    elif is_hint_pep484585_tuple_empty(cause.hint):
        # If this pith is the empty tuple, this path satisfies this hint.
        if not cause.pith:
            return cause
        # Else, this tuple is non-empty and thus fails to satisfy this hint.

        # Deep output cause to be returned, permuted from this input cause
        # with a human-readable string describing this failure.
        cause_deep = cause.permute(cause_str_or_none=(
            f'tuple {represent_pith(cause.pith)} non-empty'))

        # Return this cause.
        return cause_deep
    # Else, this hint is a standard fixed-length tuple.

    # If this pith and hint are of differing lengths, this tuple fails to
    # satisfy this hint. In this case...
    if len(cause.pith) != len(cause.hint_childs):
        # Deep output cause to be returned, permuted from this input cause
        # with a human-readable string describing this failure.
        cause_deep = cause.permute(cause_str_or_none=(
            f'tuple {represent_pith(cause.pith)} length '
            f'{len(cause.pith)} != {len(cause.hint_childs)}'
        ))

        # Return this cause.
        return cause_deep
    # Else, this pith and hint are of the same length.

    # For each enumerated item of this tuple...
    for pith_item_index, pith_item in enumerate(cause.pith):
        # Child hint corresponding to this tuple item. Since this pith and
        # hint are of the same length, this child hint exists.
        hint_child = cause.hint_childs[pith_item_index]
        # print(f'tuple pith: {repr(pith_item)}\ntuple hint child: {repr(hint_child)}')

        # If this child hint is ignorable, continue to the next.
        if hint_child is None:
            continue
        # Else, this child hint is unignorable.

        # Deep output cause to be returned, type-checking whether this tuple
        # item satisfies this child hint.
        # sleuth_copy = cause.permute(pith=pith_item, hint=hint_child)
        # pith_item_cause = sleuth_copy.find_cause()
        cause_deep = cause.permute(
            pith=pith_item, hint=hint_child).find_cause()

        # If this item is the cause of this failure...
        if cause_deep.cause_str_or_none is not None:
            # print(f'tuple pith: {sleuth_copy.pith}\ntuple hint child: {sleuth_copy.hint}\ncause: {pith_item_cause}')

            # Human-readable substring prefixing this failure with metadata
            # describing this item.
            cause_deep.cause_str_or_none = (
                f'{prefix_pith_type(pith=cause.pith, is_color=cause.conf.is_color)}'
                f'index {color_type(text=str(pith_item_index), is_color=cause.conf.is_color)} '
                f'item {cause_deep.cause_str_or_none}'
            )

            # Return this cause.
            return cause_deep
        # Else, this item is *NOT* the cause of this failure. Silently
        # continue to the next.

    # Return this cause as is; all items of this fixed-length tuple are valid,
    # implying this pith to deeply satisfy this hint.
    return cause

# ....................{ PRIVATE ~ finders                  }....................
def _find_cause_sequence(cause: ViolationCause) -> ViolationCause:
    '''
    Output cause describing whether the pith of the passed input cause either
    satisfies or violates the **variadic sequence type hint** (i.e.,
    PEP-compliant type hint accepting one or more subscripted arguments
    constraining *all* items of this object, which necessarily satisfies the
    :class:`collections.abc.Sequence` protocol with guaranteed ``O(1)``
    indexation across all sequence items) of that cause.

    Parameters
    ----------
    cause : ViolationCause
        Input cause providing this data.

    Returns
    -------
    ViolationCause
        Output cause type-checking this data.
    '''
    # Assert this type hint to describe a variadic sequence. See the parent
    # find_cause_sequence_args_1() and find_cause_tuple()
    # functions for derivative logic.
    #
    # Note that this pith need *NOT* be validated to be an instance of the
    # expected variadic sequence, as the caller guarantees this to be the case.
    assert isinstance(cause, ViolationCause), f'{repr(cause)} not cause.'
    assert (
        cause.hint_sign in HINT_SIGNS_SEQUENCE_ARGS_1 or (
            cause.hint_sign is HintSignTuple and
            len(cause.hint_childs) == 2 and
            cause.hint_childs[1] is Ellipsis
        )
    ), (f'{repr(cause.hint)} neither '
        f'standard sequence nor variadic tuple hint.')

    # If this sequence is empty, all items of this sequence (of which there are
    # none) are valid. This sequence satisfies this hint. Just go with it!
    if not cause.pith:
        return cause
    # Else, this sequence is non-empty.

    # First child hint subscripting this sequence hint. All remaining child
    # hints if any are ignorable. Specifically, if this hint is:
    # * A standard sequence (e.g., "typing.List[str]"), this hint is
    #   subscripted by only one child hint.
    # * A variadic tuple (e.g., "typing.Tuple[str, ...]"), this hint is
    #   subscripted by only two child hints the latter of which is
    #   ignorable syntactic chuff.
    hint_child = cause.hint_childs[0]

    # If this child hint is ignorable, this sequence satisfies this hint.
    if hint_child is None:
        return cause
    # Else, this child hint is unignorable.

    # Arbitrary iterator satisfying the enumerate() protocol, yielding zero or
    # more 2-tuples of the form "(item_index, item)", where:
    # * "item_index" is the 0-based index of this item.
    # * "item" is an arbitrary item of this sequence.
    pith_enumerator = None

    # If this sequence was indexed by the parent @beartype-generated wrapper
    # function by a pseudo-random integer in O(1) time, type-check *ONLY* the
    # same index of this sequence also in O(1) time. Since the current call to
    # that function failed a type-check, either this index is the index
    # responsible for that failure *OR* this sequence is valid and another
    # container is responsible for that failure. In either case, no other
    # indices of this sequence need be checked.
    if cause.random_int is not None:
        # 0-based index of this item calculated from this random integer in the
        # *SAME EXACT WAY* as in the parent @beartype-generated wrapper.
        pith_item_index = cause.random_int % len(cause.pith)

        # Pseudo-random item with this index in this sequence.
        pith_item = cause.pith[pith_item_index]

        # 2-tuple of this index and item in the same order as the 2-tuples
        # returned by the enumerate() builtin.
        pith_enumeratable = (pith_item_index, pith_item)

        # Iterator yielding only this 2-tuple.
        pith_enumerator = iter((pith_enumeratable,))
        # print(f'Checking item {pith_item_index} in O(1) time!')
    # Else, this sequence was iterated by the parent @beartype-generated wrapper
    # function in O(n) time. In this case, type-check *ALL* indices of this
    # sequence in O(n) time as well.
    else:
        # Iterator yielding all indices and items of this sequence.
        pith_enumerator = enumerate(cause.pith)
        # print('Checking sequence in O(n) time!')

    # For each enumerated item of this sequence...
    for pith_item_index, pith_item in pith_enumerator:
        # Deep output cause, type-checking whether this item satisfies this
        # child hint.
        cause_deep = cause.permute(
            pith=pith_item, hint=hint_child).find_cause()

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
        # to the next.

    # Return this cause as is; all items of this sequence are valid, implying
    # this sequence to deeply satisfy this hint.
    return cause
