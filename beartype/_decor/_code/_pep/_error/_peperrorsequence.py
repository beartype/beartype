#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint call-time utilities** (i.e., callables
operating on PEP-compliant type hints intended to be called by dynamically
generated wrapper functions wrapping decorated callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._decor._code._pep._error._peperrortype import (
    get_cause_or_none_type)
from beartype._decor._code._pep._error._peperrorsleuth import CauseSleuth
from beartype._util.hint.data.pep.utilhintdatapep import (
    HINT_PEP_SIGNS_SEQUENCE_STANDARD)
from beartype._util.hint.pep.utilhintpepget import get_hint_pep_type_origin
from beartype._util.hint.utilhinttest import is_hint_ignorable
from beartype._util.text.utiltextrepr import get_object_representation
from typing import Tuple

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS ~ sequence                }....................
def get_cause_or_none_sequence_standard(
    sleuth: CauseSleuth) -> 'Optional[str]':
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed **PEP-compliant standard sequence type hint** (i.e.,
    PEP-compliant type hint accepting exactly one subscripted type hint
    argument constraining *all* items of this object, which necessarily
    satisfies the :class:`collections.abc.Sequence` protocol with guaranteed
    ``O(1)`` indexation across all sequence items) if this object actually
    fails to satisfy this hint *or* ``None`` otherwise (i.e., if this object
    satisfies this hint).

    Parameters
    ----------
    sleuth : CauseSleuth
        Type-checking error cause sleuth.
    '''
    assert isinstance(sleuth, CauseSleuth), f'{repr(sleuth)} not cause sleuth.'
    assert sleuth.hint_sign in HINT_PEP_SIGNS_SEQUENCE_STANDARD, (
        f'{repr(sleuth.hint)} not standard sequence.')

    # Assert this sequence was subscripted by exactly one argument. Note that
    # the "typing" module should have already guaranteed this on our behalf.
    assert len(sleuth.hint_childs) == 1, (
        f'Standard sequence {repr(sleuth.hint)} subscripted by '
        f'multiple arguments.')

    # Non-"typing" class originating this attribute (e.g., "list" for "List").
    hint_type_origin = get_hint_pep_type_origin(sleuth.hint_sign)

    # If this pith is *NOT* an instance of this class, defer to the getter
    # function handling non-"typing" classes.
    if not isinstance(sleuth.pith, hint_type_origin):
        return get_cause_or_none_type(sleuth.permute(hint=hint_type_origin))

    # Else, this pith is an instance of this class and is thus a sequence.
    # Defer to the getter function supporting simple sequences.
    return _get_cause_or_none_sequence(sleuth)


def get_cause_or_none_tuple(sleuth: CauseSleuth) -> 'Optional[str]':
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed **PEP-compliant standard sequence type hint** (i.e.,
    PEP-compliant type hint accepting exactly one subscripted type hint
    argument constraining *all* items of this object, which necessarily
    satisfies the :class:`collections.abc.Sequence` protocol with guaranteed
    ``O(1)`` indexation across all sequence items) if this object actually
    fails to satisfy this hint *or* ``None`` otherwise (i.e., if this object
    satisfies this hint).

    Parameters
    ----------
    sleuth : CauseSleuth
        Type-checking error cause sleuth.
    '''
    assert isinstance(sleuth, CauseSleuth), f'{repr(sleuth)} not cause sleuth.'
    assert sleuth.hint_sign is Tuple, f'{repr(sleuth.hint_sign)} not tuple.'

    # If this pith is *NOT* an instance of this class, defer to the getter
    # function handling non-"typing" classes.
    if not isinstance(sleuth.pith, tuple):
        return get_cause_or_none_type(sleuth.permute(hint=tuple))

    # If this hint is...
    if (
        # This tuple is subscripted by exactly two child hints *AND*...
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
    # If this hint is subscripted by exactly one child hint *AND* this child
    # hint is the empty tuple, validate this pith to be the empty tuple. Ugh!
    elif len(sleuth.hint_childs) == 1 and sleuth.hint_childs[0] == ():
        # If this pith is a non-empty tuple and thus fails to satisfy this
        # hint...
        if sleuth.pith:
            # Truncated representation of this tuple.
            pith_repr = get_object_representation(sleuth.pith)

            # Return a substring describing this failure.
            return f'tuple {pith_repr} non-empty'
        # Else, this pith is the empty tuple and thus satisfies this hint.
    # Else, this hint is a standard fixed-length tuple. In this case...
    else:
        # If this pith and hint are of differing lengths, this tuple fails to
        # satisfy this hint. In this case...
        if len(sleuth.pith) != len(sleuth.hint_childs):
            # Truncated representation of this tuple.
            pith_repr = get_object_representation(sleuth.pith)

            # Return a substring describing this failure.
            return (
                f'tuple {pith_repr} length '
                f'{len(sleuth.pith)} not {len(sleuth.hint_childs)}'
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
                return f'tuple item {pith_item_index} {pith_item_cause}'
            # Else, this item is *NOT* the cause of this failure. Silently
            # continue to the next.

    # Return "None", as all items of this fixed-length tuple are valid,
    # implying this pith to deeply satisfy this hint.
    return None

# ....................{ GETTERS ~ private                 }....................
def _get_cause_or_none_sequence(sleuth: CauseSleuth) -> 'Optional[str]':
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed **PEP-compliant possibly non-standard sequence type
    hint** (i.e., PEP-compliant type hint accepting one or more subscripted
    type hint arguments constraining *all* items of this object, which
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
    assert (
        sleuth.hint_sign in HINT_PEP_SIGNS_SEQUENCE_STANDARD or (
            sleuth.hint_sign is Tuple and
            len(sleuth.hint_childs) == 2 and
            sleuth.hint_childs[1] is Ellipsis
        )
    ), f'{repr(sleuth.hint)} neither standard sequence nor variadic tuple.'

    # First child hint of this hint. All remaining child hints if any are
    # ignorable. Specifically, if this hint is:
    # * A standard sequence (e.g., "typing.List[str]"), this hint is
    #   subscripted by only one child hint.
    # * A variadic tuple (e.g., "typing.Tuple[str, ...]"), this hint is
    #   subscripted by only two child hints the latter of which is ignorable
    #   syntactic chuff.
    hint_child = sleuth.hint_childs[0]

    # If this child hint is *NOT* ignorable...
    if not is_hint_ignorable(hint_child):
        # For each enumerated item of this pith...
        for pith_item_index, pith_item in enumerate(sleuth.pith):
            # Human-readable string describing the failure of this item to
            # satisfy this child hint if this item actually fails to satisfy
            # this child hint *or* "None" otherwise.
            pith_item_cause = sleuth.permute(
                pith=pith_item, hint=hint_child).get_cause_or_none()

            # If this item is the cause of this failure, return a substring
            # describing this failure by embedding this failure (itself
            # intended to be embedded in a longer string).
            if pith_item_cause is not None:
                return (
                    f'{sleuth.pith.__class__.__name__} item '
                    f'{pith_item_index} {pith_item_cause}')
            # Else, this item is *NOT* the cause of this failure. Silently
            # continue to the next.
    # Else, this child hint is ignorable.

    # Return "None", as all items of this pith are valid, implying this pith to
    # deeply satisfy this hint.
    return None
