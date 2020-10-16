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
from beartype._util.hint.pep.error._utilhintpeperrortype import (
    get_cause_or_none_type)
from beartype._util.hint.pep.utilhintpepdata import (
    TYPING_ATTRS_SEQUENCE_STANDARD)
from beartype._util.hint.pep.error._utilhintpeperrorsleuth import CauseSleuth
from beartype._util.hint.utilhintget import get_hint_type_origin
from beartype._util.hint.utilhinttest import is_hint_ignorable
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
    assert sleuth.hint_attr in TYPING_ATTRS_SEQUENCE_STANDARD, (
        f'{repr(sleuth.hint_attr)} not '
        f'argumentless "typing" standard sequence attribute.')

    # Non-"typing" class originating this attribute (e.g., "list" for "List").
    hint_type_origin = get_hint_type_origin(sleuth.hint_attr)

    # If this pith is *NOT* an instance of this class, defer to the getter
    # function handling non-"typing" classes.
    if not isinstance(sleuth.pith, hint_type_origin):
        return get_cause_or_none_type(sleuth.permute(hint=hint_type_origin))
    # Else, this pith is an instance of this class and is thus a sequence.

    # Tuple of all subscripted arguments defining this sequence.
    hint_childs = sleuth.hint.__args__

    # Assert this sequence was subscripted by exactly one argument. Note that
    # the "typing" module should have already guaranteed this on our behalf.
    assert len(hint_childs) == 1, (
        f'{sleuth.exception_label} PEP standard sequence type hint '
        f'{repr(sleuth.hint)} subscripted by multiple arguments.')

    # Lone child hint of this parent hint.
    hint_child = hint_childs[0]

    # If this child hint is *NOT* ignorable...
    if not is_hint_ignorable(hint_child):
        # For each enumerated item of this pith...
        for pith_item_index, pith_item in enumerate(sleuth.pith):
            # Human-readable string describing the failure of this item to
            # satisfy this child hint if this item actually fails to satisfy
            # this child hint *or* "None" otherwise.
            pith_item_cause = sleuth.permute(
                pith=pith_item,
                hint=hint_child,
            ).get_cause_or_none()

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
    assert sleuth.hint_attr is Tuple, (
        f'{repr(sleuth.hint_attr)} not {repr(Tuple)}.')

    #FIXME: Remove after implementing us up. To do so:
    #* Refactor the existing _get_cause_or_none_sequence_standard() function to
    #  defer to the new _get_cause_or_none_sequence() function.
    #* Detect whether this tuple is variadic or fixed.
    #* If fixed, implement fixed tuple type-checking here.
    #* If variadic, defer to the _get_cause_or_none_sequence() function.
    from beartype.roar import _BeartypeUtilRaisePepException
    raise _BeartypeUtilRaisePepException(
        'get_cause_or_none_tuple() currently unimplemented.')

# ....................{ GETTERS ~ private                 }....................
def _get_cause_or_none_sequence(
    sleuth: CauseSleuth,
    hint_child: object,
) -> 'Optional[str]':
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
    hint_child : object
        Child hint of this sequence to type-check all sequence items as.
    '''
    assert isinstance(sleuth, CauseSleuth), f'{repr(sleuth)} not cause sleuth.'

    #FIXME: Generalize to support variadic tuples.
    # assert sleuth.hint_attr in TYPING_ATTRS_SEQUENCE_STANDARD, (
    #     f'{repr(sleuth.hint_attr)} not '
    #     f'argumentless "typing" standard sequence attribute.')

    # Non-"typing" class originating this attribute (e.g., "list" for "List").
    hint_type_origin = get_hint_type_origin(sleuth.hint_attr)

    # If this pith is *NOT* an instance of this class, defer to the getter
    # function handling non-"typing" classes.
    if not isinstance(sleuth.pith, hint_type_origin):
        return get_cause_or_none_type(sleuth.permute(hint=hint_type_origin))
    # Else, this pith is an instance of this class and is thus a sequence.

    # If this child hint is *NOT* ignorable...
    if not is_hint_ignorable(hint_child):
        # For each enumerated item of this pith...
        for pith_item_index, pith_item in enumerate(sleuth.pith):
            # Human-readable string describing the failure of this item to
            # satisfy this child hint if this item actually fails to satisfy
            # this child hint *or* "None" otherwise.
            pith_item_cause = sleuth.permute(
                pith=pith_item,
                hint=hint_child,
            ).get_cause_or_none()

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
