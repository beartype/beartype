#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **union type hint exception raisers** (i.e.,
functions raising human-readable exceptions called by :mod:`beartype`-decorated
callables on the first invalid parameter or return value failing a type-check
against the :pep:`484`-compliant union type hint annotating that parameter or
return).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar._roarexc import _BeartypeCallHintPepRaiseException
from beartype._decor._error._errorsleuth import CauseSleuth
from beartype._data.hint.pep.sign.datapepsignset import HINT_SIGNS_UNION
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_type_isinstanceable_or_none)
from beartype._util.hint.pep.utilpeptest import is_hint_pep
from beartype._util.hint.utilhinttest import is_hint_ignorable
from beartype._util.text.utiltextjoin import join_delimited_disjunction_types
from beartype._util.text.utiltextmunge import (
    suffix_unless_suffixed, uppercase_char_first)
from beartype._util.text.utiltextrepr import represent_object
from typing import Optional

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS                           }....................
def get_cause_or_none_union(sleuth: CauseSleuth) -> Optional[str]:
    '''
    Human-readable string describing the failure of the passed arbitrary object
    to satisfy the passed PEP-compliant union type hint if this object actually
    fails to satisfy this hint *or* ``None`` otherwise (i.e., if this object
    satisfies this hint).

    Parameters
    ----------
    sleuth : CauseSleuth
        Type-checking error cause sleuth.
    '''
    assert isinstance(sleuth, CauseSleuth), f'{repr(sleuth)} not cause sleuth.'
    assert sleuth.hint_sign in HINT_SIGNS_UNION, (
        f'{repr(sleuth.hint)} not union sign.')

    # Subset of all classes shallowly associated with these child hints (i.e.,
    # by being either these child hints in the case of non-"typing" classes
    # *OR* the classes originating these child hints in the case of
    # PEP-compliant type hints) that this pith fails to shallowly satisfy.
    hint_classes_unsatisfied = set()

    # List of all human-readable strings describing the failure of this pith to
    # satisfy each of these child hints.
    causes_union = []

    # Indentation preceding each line of the strings returned by child getter
    # functions called by this parent getter function, offset to visually
    # demarcate child from parent causes in multiline strings.
    CAUSE_INDENT_CHILD = sleuth.cause_indent + '  '

    # For each subscripted argument of this union...
    for hint_child in sleuth.hint_childs:
        # If this child hint is ignorable, continue to the next.
        if is_hint_ignorable(hint_child):
            continue
        # Else, this child hint is unignorable.

        # If this child hint is PEP-compliant...
        if is_hint_pep(hint_child):
            # Non-"typing" class originating this child hint if any *OR* "None"
            # otherwise.
            hint_child_type_origin = get_hint_pep_type_isinstanceable_or_none(
                hint_child)

            # If...
            if (
                # This child hint originates from a non-"typing" class *AND*...
                hint_child_type_origin is not None and
                # This pith is *NOT* an instance of this class...
                not isinstance(sleuth.pith, hint_child_type_origin)
            # Then this pith fails to satisfy this child hint. In this case...
            ):
                # Add this class to the subset of all classes this pith does
                # *NOT* satisfy.
                hint_classes_unsatisfied.add(hint_child_type_origin)

                # Continue to the next child hint.
                continue
            # Else, this pith is an instance of this class and thus shallowly
            # (but *NOT* necessarily deeply) satisfies this child hint.

            # Human-readable string describing the failure of this pith to
            # deeply satisfy this child hint if this pith actually fails to
            # deeply satisfy this child hint *or* "None" otherwise.
            pith_cause_hint_child = sleuth.permute(
                hint=hint_child,
                cause_indent=CAUSE_INDENT_CHILD,
            ).get_cause_or_none()

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
                f'{sleuth.exception_prefix}union type hint '
                f'{repr(sleuth.hint)} child hint {repr(hint_child)} invalid '
                f'(i.e., neither type hint nor non-"typing" class).')
            # Else, this child hint is a non-"typing" type.

            # If this pith is an instance of this class, this pith satisfies
            # this hint. In this case, return "None".
            if isinstance(sleuth.pith, hint_child):
                return None

            # Else, this pith is *NOT* an instance of this class, implying this
            # pith to *NOT* satisfy this hint. In this case, add this class to
            # the subset of all classes this pith does *NOT* satisfy.
            hint_classes_unsatisfied.add(hint_child)

    # If this pith fails to shallowly satisfy one or more classes, concatenate
    # these failures onto a discrete bullet-prefixed line.
    if hint_classes_unsatisfied:
        # Human-readable comma-delimited disjunction of the names of these
        # classes (e.g., "bool, float, int, or str").
        cause_types_unsatisfied = join_delimited_disjunction_types(
            hint_classes_unsatisfied)

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
        causes_union.insert(0, f'not {cause_types_unsatisfied}')

    # If prior logic appended *NO* causes, raise an exception.
    if not causes_union:
        raise _BeartypeCallHintPepRaiseException(
            f'{sleuth.exception_prefix}type hint '
            f'{repr(sleuth.hint)} failure causes unknown.'
        )
    # Else, prior logic appended one or more strings describing these failures.

    # Truncated object representation of this pith.
    pith_repr = represent_object(sleuth.pith)

    # If prior logic appended one cause, return this cause as a single-line
    # substring intended to be embedded in a longer string.
    if len(causes_union) == 1:
        return f'{pith_repr} {causes_union[0]}'
    # Else, prior logic appended two or more causes.

    # Return a multiline string comprised of...
    return '{}:\n{}'.format(
        # This truncated object representation.
        pith_repr,
        # The newline-delimited concatenation of each cause as a discrete
        # bullet-prefixed line...
        '\n'.join(
            '{}* {}'.format(
                # Indented by the current indent.
                sleuth.cause_indent,
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
