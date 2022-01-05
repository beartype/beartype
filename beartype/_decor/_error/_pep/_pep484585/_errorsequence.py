#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint call-time utilities** (i.e., callables
operating on PEP-compliant type hints intended to be called by dynamically
generated wrapper functions wrapping decorated callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._decor._error._errorsleuth import CauseSleuth
from beartype._decor._error._errortype import (
    get_cause_or_none_type_instance_origin)
from beartype._data.hint.pep.sign.datapepsigns import HintSignTuple
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_SEQUENCE_ARGS_1)
from beartype._util.hint.pep.proposal.pep484585.utilpep484585 import (
    is_hint_pep484585_tuple_empty)
from beartype._util.hint.utilhinttest import is_hint_ignorable
from beartype._util.text.utiltextlabel import label_obj_type
from beartype._util.text.utiltextrepr import represent_object
from typing import Optional

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS ~ sequence                }....................
def get_cause_or_none_sequence_args_1(sleuth: CauseSleuth) -> Optional[str]:
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed **PEP-compliant single-argument variadic sequence
    type hint** (i.e., PEP-compliant type hint accepting exactly one
    subscripted argument constraining *all* items of this object, which
    necessarily satisfies the :class:`collections.abc.Sequence` protocol with
    guaranteed ``O(1)`` indexation across all sequence items) if this object
    actually fails to satisfy this hint *or* ``None`` otherwise (i.e., if this
    object satisfies this hint).

    Parameters
    ----------
    sleuth : CauseSleuth
        Type-checking error cause sleuth.
    '''
    assert isinstance(sleuth, CauseSleuth), f'{repr(sleuth)} not cause sleuth.'
    assert sleuth.hint_sign in HINT_SIGNS_SEQUENCE_ARGS_1, (
        f'{repr(sleuth.hint)} not 1-argument sequence hint.')

    # Assert this sequence was subscripted by exactly one argument. Note that
    # the "typing" module should have already guaranteed this on our behalf.
    assert len(sleuth.hint_childs) == 1, (
        f'1-argument sequence hint {repr(sleuth.hint)} subscripted by '
        f'{len(sleuth.hint_childs)} != 1.')

    # Human-readable string describing the failure of this pith to be an
    # instance of the type originating this hint (e.g., "list" for "list[str]")
    # if this pith is not an instance of this type *OR* "None" otherwise.
    pith_cause = get_cause_or_none_type_instance_origin(sleuth)

    # Return either...
    return (
        # If this pith is *NOT* an instance of this type, this string;
        pith_cause
        if pith_cause is not None else
        # Else, this pith is an instance of this type and is thus a sequence.
        # In this case, defer to the getter function supporting sequences.
        _get_cause_or_none_sequence(sleuth)
    )


def get_cause_or_none_tuple(sleuth: CauseSleuth) -> Optional[str]:
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed **PEP-compliant tuple type hint** (i.e.,
    PEP-compliant type hint accepting either zero or more subscripted arguments
    iteratively constraining each item of this fixed-length tuple *or* exactly
    one subscripted arguments constraining *all* items of this variadic tuple)
    if this object actually fails to satisfy this hint *or* ``None`` otherwise
    (i.e., if this object satisfies this hint).

    Parameters
    ----------
    sleuth : CauseSleuth
        Type-checking error cause sleuth.
    '''
    assert isinstance(sleuth, CauseSleuth), f'{repr(sleuth)} not cause sleuth.'
    assert sleuth.hint_sign is HintSignTuple, (
        f'{repr(sleuth.hint_sign)} not tuple hint.')

    # Human-readable string describing the failure of this pith to be a tuple
    # if this pith is not a tuple *OR* "None" otherwise.
    pith_cause = get_cause_or_none_type_instance_origin(sleuth)

    # If this pith is *NOT* a tuple, return this string.
    if pith_cause is not None:
        return pith_cause
    # Else, this pith is a tuple.

    # If this hint is a tuple...
    if (
        # Subscripted by exactly two child hints *AND*...
        len(sleuth.hint_childs) == 2 and
        # The second child hint is just an unquoted ellipsis...
        sleuth.hint_childs[1] is Ellipsis
    ):
    # Then this hint is of the variadic form "Tuple[{typename}, ...]", typing a
    # tuple accepting a variadic number of items all satisfying the
    # child hint "{typename}". Since this case semantically reduces to a simple
    # sequence, defer to the getter function supporting simple sequences.
        return _get_cause_or_none_sequence(sleuth)
    # Else, this hint is of the fixed-length form "Tuple[{typename1}, ...,
    # {typenameN}]", typing a tuple accepting a fixed number of items each
    # satisfying a unique child hint.
    #
    # If this hint is the empty fixed-length tuple, validate this pith to be
    # the empty tuple.
    elif is_hint_pep484585_tuple_empty(sleuth.hint):
        # If this pith is non-empty and thus fails to satisfy this hint...
        if sleuth.pith:
            # Truncated representation of this tuple.
            pith_repr = represent_object(sleuth.pith)

            # Return a substring describing this failure.
            return f'tuple {pith_repr} non-empty'
        # Else, this pith is the empty tuple and thus satisfies this hint.
    # Else, this hint is a standard fixed-length tuple. In this case...
    else:
        # If this pith and hint are of differing lengths, this tuple fails to
        # satisfy this hint. In this case...
        if len(sleuth.pith) != len(sleuth.hint_childs):
            # Truncated representation of this tuple.
            pith_repr = represent_object(sleuth.pith)

            # Return a substring describing this failure.
            return (
                f'tuple {pith_repr} length '
                f'{len(sleuth.pith)} != {len(sleuth.hint_childs)}'
            )
        # Else, this pith and hint are of the same length.

        # For each enumerated item of this tuple...
        for pith_item_index, pith_item in enumerate(sleuth.pith):
            # Child hint corresponding to this tuple item. Since this pith and
            # hint are of the same length, this child hint exists.
            hint_child = sleuth.hint_childs[pith_item_index]

            # If this child hint is ignorable, continue to the next.
            if is_hint_ignorable(hint_child):
                continue
            # Else, this child hint is unignorable.

            # Human-readable string describing the failure of this tuple item
            # to satisfy this child hint if this item actually fails to satisfy
            # this child hint *or* "None" otherwise.
            # print(f'tuple pith: {pith_item}\ntuple hint child: {hint_child}')
            # sleuth_copy = sleuth.permute(pith=pith_item, hint=hint_child)
            # pith_item_cause = sleuth_copy.get_cause_or_none()
            pith_item_cause = sleuth.permute(
                pith=pith_item, hint=hint_child).get_cause_or_none()

            # If this item is the cause of this failure, return a substring
            # describing this failure by embedding this failure (itself
            # intended to be embedded in a longer string).
            if pith_item_cause is not None:
                # print(f'tuple pith: {sleuth_copy.pith}\ntuple hint child: {sleuth_copy.hint}\ncause: {pith_item_cause}')
                return f'tuple index {pith_item_index} item {pith_item_cause}'
            # Else, this item is *NOT* the cause of this failure. Silently
            # continue to the next.

    # Return "None", as all items of this fixed-length tuple are valid,
    # implying this pith to deeply satisfy this hint.
    return None

# ....................{ GETTERS ~ private                 }....................
def _get_cause_or_none_sequence(sleuth: CauseSleuth) -> Optional[str]:
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed **PEP-compliant variadic sequence type hint** (i.e.,
    PEP-compliant type hint accepting one or more subscripted arguments
    constraining *all* items of this object, which necessarily satisfies the
    :class:`collections.abc.Sequence` protocol with guaranteed ``O(1)``
    indexation across all sequence items) if this object actually fails to
    satisfy this hint *or* ``None`` otherwise (i.e., if this object satisfies
    this hint).

    Parameters
    ----------
    sleuth : CauseSleuth
        Type-checking error cause sleuth.
    '''
    # Assert this type hint to describe a variadic sequence. See the parent
    # get_cause_or_none_sequence_args_1() and get_cause_or_none_tuple()
    # functions for derivative logic.
    #
    # Note that this pith need *NOT* be validated to be an instance of the
    # expected variadic sequence, as the caller guarantees this to be the case.
    assert isinstance(sleuth, CauseSleuth), f'{repr(sleuth)} not cause sleuth.'
    assert (
        sleuth.hint_sign in HINT_SIGNS_SEQUENCE_ARGS_1 or (
            sleuth.hint_sign is HintSignTuple and
            len(sleuth.hint_childs) == 2 and
            sleuth.hint_childs[1] is Ellipsis
        )
    ), (f'{repr(sleuth.hint)} neither '
        f'standard sequence nor variadic tuple hint.')

    # If this sequence is non-empty...
    if sleuth.pith:
        # First child hint of this hint. All remaining child hints if any are
        # ignorable. Specifically, if this hint is:
        # * A standard sequence (e.g., "typing.List[str]"), this hint is
        #   subscripted by only one child hint.
        # * A variadic tuple (e.g., "typing.Tuple[str, ...]"), this hint is
        #   subscripted by only two child hints the latter of which is
        #   ignorable syntactic chuff.
        hint_child = sleuth.hint_childs[0]

        # If this child hint is *NOT* ignorable...
        if not is_hint_ignorable(hint_child):
            # Arbitrary iterator satisfying the enumerate() protocol, yielding
            # zero or more 2-tuples of the form "(item_index, item)", where:
            # * "item" is an arbitrary item of this sequence.
            # * "item_index" is the 0-based index of this item.
            pith_enumerator = None

            # If this sequence was indexed by the parent @beartype-generated
            # wrapper function by a pseudo-random integer in O(1) time,
            # type-check *ONLY* the same index of this sequence also in O(1)
            # time. Since the current call to that function failed a
            # type-check, either this index is the index responsible for that
            # failure *OR* this sequence is valid and another container
            # entirely is responsible for that failure. In either case, no
            # other indices of this sequence need be checked.
            if sleuth.random_int is not None:
                # 0-based index of this item calculated from this random
                # integer in the *SAME EXACT WAY* as in the parent
                # @beartype-generated wrapper function.
                pith_item_index = sleuth.random_int % len(sleuth.pith)

                # Pseudo-random item with this index in this sequence.
                pith_item = sleuth.pith[pith_item_index]

                # 2-tuple of this index and item in the same order as the
                # 2-tuples returned by the enumerate() builtin.
                pith_enumeratable = (pith_item_index, pith_item)

                # Iterator yielding only this 2-tuple.
                pith_enumerator = iter((pith_enumeratable,))
                # print(f'Checking item {pith_item_index} in O(1) time!')
            # Else, this sequence was iterated by the parent
            # @beartype-generated wrapper function in O(n) time. In this case,
            # type-check *ALL* indices of this sequence in O(n) time as well.
            else:
                # Iterator yielding all indices and items of this sequence.
                pith_enumerator = enumerate(sleuth.pith)
                # print('Checking sequence in O(n) time!')

            # For each enumerated item of this (sub)sequence...
            for pith_item_index, pith_item in pith_enumerator:
                # Human-readable string describing the failure of this item to
                # satisfy this child hint if this item actually fails to
                # satisfy this child hint *or* "None" otherwise.
                pith_item_cause = sleuth.permute(
                    pith=pith_item, hint=hint_child).get_cause_or_none()

                # If this item is the cause of this failure, return a substring
                # describing this failure by embedding this failure (itself
                # intended to be embedded in a longer string).
                if pith_item_cause is not None:
                    return (
                        f'{label_obj_type(sleuth.pith)} '
                        f'index {pith_item_index} item {pith_item_cause}'
                    )
                # Else, this item is *NOT* the cause of this failure. Silently
                # continue to the next.
        # Else, this child hint is ignorable.
    # Else, this sequence is empty, in which case all items of this sequence
    # (of which there are none) are valid. Just go with it, people.

    # Return "None", as all items of this sequence are valid, implying this
    # sequence to deeply satisfy this hint.
    return None
