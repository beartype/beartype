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
import typing
from beartype.roar import _BeartypeUtilRaisePepException
from beartype._util.hint.utilhintget import get_hint_type_origin
from beartype._util.hint.utilhinttest import is_hint_ignorable
from beartype._util.hint.pep.error._utilhintpeperrorcause import (
    get_cause_or_none)
from beartype._util.hint.pep.utilhintpepdata import TYPING_ATTRS_UNION
from beartype._util.hint.pep.utilhintpepget import get_hint_pep_typing_attr
from beartype._util.hint.pep.utilhintpeptest import is_hint_pep
from beartype._util.text.utiltextjoin import join_delimited_disjunction
from beartype._util.text.utiltextmunge import (
    suffix_unless_suffixed, uppercase_char_first)
from beartype._util.text.utiltextrepr import get_object_representation

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS                           }....................
def get_cause_or_none_union(
    pith: object,
    hint: object,
    hint_attr: object,
    cause_indent: str,
    exception_label: str,
) -> 'Optional[str]':
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed PEP-compliant union type hint if this object actually
    fails to satisfy this hint *or* ``None`` otherwise (i.e., if this object
    satisfies this hint).

    See Also
    ----------
    :func:`_get_cause_or_none`
        Further details.
    '''
    assert hint_attr in TYPING_ATTRS_UNION, (
        '{!r} not argumentless "typing" union attribute.'.format(hint_attr))

    # Tuple of all subscripted arguments defining this union, localized for
    # both minor efficiency and major readability.
    hint_childs = hint.__args__

    # Assert this union is unsubscripted. Note that the "typing" module should
    # have already guaranteed this on our behalf.
    assert hint_childs, '{} PEP union type hint {!r} unsubscripted.'.format(
        exception_label, hint)
    # Else, this union is subscripted by two or more arguments.

    # Subset of all classes shallowly associated with these child hints (i.e.,
    # by being either these child hints in the case of non-"typing" classes
    # *OR* the classes originating these child hints in the case of
    # PEP-compliant type hints) that this pith does *NOT* shallowly satisfy.
    hint_types_unsatisfied = set()

    # List of all human-readable strings describing the failure of this pith to
    # satisfy each of these child hints.
    causes_union = []

    # Indentation preceding each line of the strings returned by child getter
    # functions called by this parent getter function, offset to visually
    # demarcate child from parent causes in multiline strings.
    CAUSE_INDENT_CHILD = cause_indent + '  '

    # For each subscripted argument of this union...
    for hint_child in hint_childs:
        # If this child hint is ignorable, continue to the next.
        if is_hint_ignorable(hint_child):
            continue
        # Else, this child hint is unignorable.

        # If this child hint is PEP-compliant...
        if is_hint_pep(hint_child):
            # Argumentless "typing" attribute identifying this child hint.
            hint_child_attr = get_hint_pep_typing_attr(hint_child)

            # Non-"typing" class originating this child attribute.
            hint_child_type_origin = get_hint_type_origin(hint_child_attr)

            # If this pith is *NOT* an instance of this class...
            if not isinstance(pith, hint_child_type_origin):
                # Add this class to the subset of all classes this pith does
                # *NOT* satisfy.
                hint_types_unsatisfied.add(hint_child_type_origin)

                # Continue to the next child hint.
                continue
            # Else, this pith is an instance of this class and thus shallowly
            # (but *NOT* necessarily deeply) satisfies this child hint.

            # Human-readable string describing the failure of this pith to
            # deeply satisfy this child hint if this pith actually fails to
            # deeply satisfy this child hint *or* "None" otherwise.
            pith_cause_hint_child = get_cause_or_none(
                pith=pith,
                hint=hint_child,
                cause_indent=CAUSE_INDENT_CHILD,
                exception_label=exception_label,
            )

            # If this pith deeply satisfies this child hint, return "None".
            if pith_cause_hint_child is None:
                # print('Union child {!r} pith {!r} deeply satisfied!'.format(hint_child, pith))
                return None
            # Else, this pith does *NOT* deeply satisfy this child hint.

            # Append a cause as a discrete bullet-prefixed line.
            causes_union.append(pith_cause_hint_child)
        # Else, this child hint is PEP-noncompliant. In this case...
        else:
            # Assert this child hint to be a non-"typing" class. Note that
            # the "typing" module should have already guaranteed that all
            # subscripted arguments of unions are either PEP-compliant type
            # hints or non-"typing" classes.
            assert isinstance(hint_child, type), (
                '{} PEP union type hint {!r} child hint {!r} invalid (i.e.,'
                'neither PEP type hint nor non-"typing" class).'.format(
                    exception_label, hint, hint_child))
            # Else, this child hint is a non-"typing" type.

            # If this pith is an instance of this class, this pith satisfies
            # this hint. In this case, return "None".
            if isinstance(pith, hint_child):
                return None

            # Else, this pith is *NOT* an instance of this class, implying this
            # pith to *NOT* satisfy this hint. In this case, add this class to
            # the subset of all classes this pith does *NOT* satisfy.
            hint_types_unsatisfied.add(hint_child)

    # If this pith does *NOT* shallowly satisfy one or more classes,
    # concatenate these failures onto a single discrete bullet-prefixed line.
    if hint_types_unsatisfied:
        # If this pith does *NOT* shallowly satisfy exactly one class...
        if len(hint_types_unsatisfied) == 1:
            # This class, destructively removed from this set for simplicity.
            hint_type_unsatisfied = hint_types_unsatisfied.pop()

            # Name of this class.
            cause_types_unsatisfied = hint_type_unsatisfied.__name__
        # Else, this pith does *NOT* shallowly satisfy two or more classes. In
        # this case...
        else:
            # Human-readable comma-delimited disjunction of the names of these
            # classes (e.g., "bool, float, int, or str").
            cause_types_unsatisfied = join_delimited_disjunction(tuple(
                hint_type_unsatisfied.__name__
                for hint_type_unsatisfied in hint_types_unsatisfied
            ))

        #FIXME: Refactor to leverage f-strings after dropping Python 3.5
        #support, which are the optimal means of performing string formatting.

        # Prepend this cause as a discrete bullet-prefixed line.
        #
        # Note that this cause is intentionally prependend rather than appended
        # to this list. Since this cause applies *ONLY* to the shallow type of
        # the current pith rather than any items contained in this pith,
        # listing this shallow cause *BEFORE* other deeper causes typically
        # applying to items contained in this pith produces substantially more
        # human-readable exception messages: e.g.,
        #     # This reads well.
        #     @beartyped pep_hinted() parameter pep_hinted_param=(1,) violates
        #     PEP type hint typing.Union[int, typing.Sequence[str]], as (1,):
        #     * Not int.
        #     * Tuple item 0 value "1" not str.
        #
        #     # This does not.
        #     @beartyped pep_hinted() parameter pep_hinted_param=(1,) violates
        #     PEP type hint typing.Union[int, typing.Sequence[str]], as (1,):
        #     * Tuple item 0 value "1" not str.
        #     * Not int.
        #
        # Note that prepending to lists is an O(n) operation, but that this
        # cost is negligible in this case both due to the negligible number of
        # child hints of the average "typing.Union" in general *AND* due to the
        # fact that this function is only called when a catastrophic type-check
        # failure has already occurred.
        causes_union.insert(0, 'not {}'.format(cause_types_unsatisfied))

    # If prior logic appended *NO* causes, raise an exception.
    if not causes_union:
        raise _BeartypeUtilRaisePepException(
            '{} PEP type hint {!r} failure causes unknown.'.format(
                exception_label, hint))
    # Else, prior logic appended one or more strings describing these failures.

    # Truncated object representation of this pith.
    pith_repr = get_object_representation(pith)

    # If prior logic appended one cause, return this cause as a single-line
    # substring intended to be embedded in a longer string.
    if len(causes_union) == 1:
        #FIXME: Refactor to leverage f-strings after dropping Python 3.5
        #support, which are the optimal means of performing string formatting.
        return '{} {}'.format(pith_repr, causes_union[0])
    # Else, prior logic appended two or more causes.

    # return causes_union[-1]
    # Return a multiline string comprised of...
    return '{}:\n{}'.format(
        # This truncated object representation.
        pith_repr,
        # The newline-delimited concatenation of each cause as a discrete
        # bullet-prefixed line...
        '\n'.join(
            '{}* {}'.format(
                # Indented by the current indent.
                cause_indent,
                # Whose first character is uppercased.
                uppercase_char_first(
                    # Suffixed by a period if *NOT* yet suffixed by a period.
                    suffix_unless_suffixed(text=cause_union, suffix='.')
                )
            )
            # '{}* {}.'.format(cause_indent, uppercase_char_first(cause_union))
            for cause_union in causes_union
        )
    )
