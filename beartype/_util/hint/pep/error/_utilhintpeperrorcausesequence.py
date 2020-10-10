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
from beartype._util.hint.pep.error._utilhintpeperrorcause import (
    get_cause_or_none, get_cause_or_none_type)
from beartype._util.hint.pep.utilhintpepdata import (
    TYPING_ATTRS_SEQUENCE_STANDARD)
from beartype._util.hint.utilhintget import get_hint_type_origin
from beartype._util.hint.utilhinttest import is_hint_ignorable

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS ~ attr : sequence         }....................
def get_cause_or_none_sequence_standard(
    pith: object,
    hint: object,
    hint_attr: object,
    cause_indent: str,
    exception_label: str,
) -> 'Optional[str]':
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed **PEP-compliant standard sequence type hint** (i.e.,
    PEP-compliant type hint accepting exactly one subscripted type hint
    argument constraining *all* items of this object, which necessarily
    satisfies the :class:`collections.abc.Sequence` protocol with guaranteed
    ``O(1)`` indexation across all sequence items) if this object actually
    fails to satisfy this hint *or* ``None`` otherwise (i.e., if this object
    satisfies this hint).

    See Also
    ----------
    :func:`_get_cause_or_none`
        Further details.
    '''
    assert hint_attr in TYPING_ATTRS_SEQUENCE_STANDARD, (
        '{!r} not argumentless "typing" '
        'standard sequence attribute.'.format(hint_attr))

    # Non-"typing" class originating this attribute (e.g., "list" for "List").
    hint_type_origin = get_hint_type_origin(hint_attr)

    # If this pith is *NOT* an instance of this class, defer to the getter
    # function handling non-"typing" classes.
    if not isinstance(pith, hint_type_origin):
        return get_cause_or_none_type(pith=pith, hint=hint_type_origin)
    # Else, this pith is an instance of this class and is thus a sequence.

    # Tuple of all subscripted arguments defining this sequence.
    hint_childs = hint.__args__

    # Assert this sequence was subscripted by exactly one argument. Note that
    # the "typing" module should have already guaranteed this on our behalf.
    assert len(hint_childs) == 1, (
        '{} PEP standard sequence type hint {!r} subscripted by '
        'multiple arguments.'.format(exception_label, hint))

    # Lone child hint of this parent hint.
    hint_child = hint_childs[0]

    # If this child hint is *NOT* ignorable...
    if not is_hint_ignorable(hint_child):
        # For each enumerated item of this pith...
        for pith_item_index, pith_item in enumerate(pith):
            # Human-readable string describing the failure of this item to
            # satisfy this child hint if this item actually fails to satisfy
            # this child hint *or* "None" otherwise.
            pith_item_cause = get_cause_or_none(
                pith=pith_item,
                hint=hint_child,
                cause_indent=cause_indent,
                exception_label=exception_label,
            )

            # If this item is the cause of this failure, return a substring
            # describing this failure by embedding this failure (itself
            # intended to be embedded in a longer string).
            if pith_item_cause is not None:
                #FIXME: Refactor to leverage f-strings after dropping Python
                #3.5 support, which are the optimal means of performing string
                #formatting.
                return '{} item {} {}'.format(
                    type(pith).__name__,
                    pith_item_index,
                    pith_item_cause,
                )
            # Else, this item is *NOT* the cause of this failure. Silently
            # continue to the next.
    # Else, this child hint is ignorable.

    # Return "None", as all items of this pith are valid, implying this pith to
    # deeply satisfy this hint.
    return None
