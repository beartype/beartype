#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`484`- and :pep:`604`-compliant **union type hint violation
describers** (i.e., functions returning human-readable strings explaining
violations of :pep:`484`-compliant and :pep:`604`-compliant union type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeCallHintPepRaiseException
from beartype._check.cls.hint.data.hintdataerror import HintDataError
from beartype._check.cls.hint.tree.hinttreeerror import HintTreeError
from beartype._check.cls.hint.hintsane import (
    HINT_SANE_IGNORABLE,
    HintSane,
    make_hint_sane,
)
from beartype._data.hint.sign.datahintsignset import HINT_SIGNS_UNION
from beartype._util.bear.plug.utilbearplugtype import (
    get_type_beartype_plugin_get_violation_str_or_none)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_origin_type_isinstanceable_or_none)
from beartype._util.hint.pep.utilpeptest import is_hint_pep
from beartype._util.text.utiltextjoin import join_types_commaed_or
from beartype._util.text.utiltextmunge import (
    suffix_str_unless_suffixed,
    uppercase_str_char_first,
)
from beartype._util.text.utiltextrepr import represent_pith

# ....................{ GETTERS                            }....................
def find_cause_pep484604_union(cause: HintTreeError) -> HintTreeError:
    '''
    Output cause describing whether the pith of the passed input cause either
    satisfies or violates the PEP-compliant union type hint of that cause.

    Parameters
    ----------
    cause : HintTreeError
        Input cause providing this data.

    Returns
    -------
    HintTreeError
        Output cause type-checking this data.
    '''
    assert isinstance(cause, HintTreeError), f'{repr(cause)} not cause.'
    assert cause.hint_curr.hint_sign in HINT_SIGNS_UNION, (
        f'{repr(cause.hint_curr_sanified)} not union sign.')
    # print(f'[union] Finding cause for child hints {cause.hint_childs_sane}...')

    # ....................{ LOCALS                         }....................
    # Indentation preceding each line of the strings returned by child getter
    # functions called by this parent getter function, offset to visually
    # demarcate child from parent causes in multiline strings.
    CAUSE_INDENT_CHILD = cause.cause_indent + '  '

    # List of all human-readable strings describing the failure of this pith to
    # satisfy each of these child hints.
    cause_strs = []

    # List of sanified metadata describing the sanification of all unignorable
    # PEP-compliant child hints subscripting this union. Iteration performed
    # below filters the lower-level "cause.hint_childs_sane" property as follows
    # into this higher-level list, initialized to the empty list:
    # * Ignorable child hints are omitted.
    # * PEP-compliant child hints originating from PEP-noncompliant
    #   isinstanceable types such that this pith is *NOT* an instance of these
    #   types are instead added to the "hint_childs_type_violated" set.
    # * PEP-noncompliant isinstanceable types are instead added to the
    #   "hint_childs_type_violated" set.
    hint_childs_sane_unignorable = []

    #FIXME: *NON-IDEAL*. Sets fail to preserve order. Refactor this into a
    #dictionary instead. Actually, perhaps this would be a useful time to define
    #an order-preserving set type. Using dictionaries is seriously lame...
    # Subset of all classes shallowly associated with these child hints (i.e.,
    # by being either these child hints in the case of non-"typing" classes
    # *OR* the classes originating these child hints in the case of
    # PEP-compliant type hints) that this pith fails to shallowly satisfy.
    hint_childs_nonpep = set()

    # Truncated object representation of this pith.
    pith_repr = represent_pith(cause.pith)

    # 0-based index of the first non-whitespace character following this
    # representation in violation causes collected below. Look. Just accept it.
    PITH_REPR_INDEX = len(pith_repr) + 1

    # ....................{ PHASE ~ filter                 }....................
    # In this first phase, we filter the lower-level "cause.hint_childs_sane"
    # tuple of sanified metadata describing the sanification of all child hints
    # subscripting this union into:
    # * "hint_childs_sane_unignorable", the subset of this sanified metadata
    #   describing the sanification of all unignorable PEP-compliant child hints
    #   subscripting this union.
    # * "hint_childs_nonpep", the subset of all unignorable PEP-noncompliant
    #   child hints that are isinstanceable types subscripting this union.

    # For the sanified metadata describing the sanification of each child hint
    # subscripting this union...
    for hint_child_sane in cause.hint_childs_sane:
        # If this child hint is ignorable, continue to the next.
        if hint_child_sane is HINT_SANE_IGNORABLE:
            continue
        # Else, this child hint is unignorable.

        # Child hint encapsulated by this metadata.
        hint_child = hint_child_sane.hint

        # If this child hint is PEP-compliant...
        if is_hint_pep(hint_child):
            # Isinstanceable type originating this child hint if any *OR* "None"
            # otherwise (i.e., if this child hint originates from no such type).
            hint_child_origin_type = (
                get_hint_pep_origin_type_isinstanceable_or_none(hint_child))

            # If...
            if (
                # This child hint originates from an isinstanceable type
                # *AND*...
                hint_child_origin_type is not None and
                # This pith is *NOT* an instance of this type...
                not isinstance(cause.pith, hint_child_origin_type)
            # Then this pith shallowly violates this child hint. In this case...
            ):
                # Add this type to the subset of all types this pith violates.
                hint_childs_nonpep.add(hint_child_origin_type)
            # Else, this pith is an instance of this type and thus shallowly
            # (but *NOT* necessarily deeply) satisfies this child hint. In this
            # case, append this child hint's sanified metadata to this list.
            else:
                hint_childs_sane_unignorable.append(hint_child_sane)
        # Else, this child hint is PEP-noncompliant. In this case...
        else:
            # Assert this child hint to be an isinstanceable class. Note that
            # both the standard "typing" module *AND* beartype itself should
            # have already guaranteed that all child hints subscripting unions
            # are either PEP-compliant type hints or isinstanceable classes.
            assert isinstance(hint_child, type), (
                f'{cause.exception_prefix}'
                f'union type hint {repr(cause.hint_curr_sanified)} '
                f'child hint {repr(hint_child)} invalid '
                f'(i.e., neither type hint nor isinstanceable type).'
            )

            # If this pith is an instance of this type and thus satisfies this
            # child hint, this pith also necessarily satisfies this parent union
            # hint. In this case, return this cause as is.
            if isinstance(cause.pith, hint_child):
                return cause
            # Else, this pith is *NOT* an instance of this type, implying that
            # this pith violates this hint.

            # Beartype-specific __instancecheck_str__() dunder method if the
            # metaclass of this type defines this method *OR* "None" otherwise
            # (i.e., if that metaclass does *NOT* define this method).
            get_hint_child_violation_str = (
                get_type_beartype_plugin_get_violation_str_or_none(hint_child))

            # If the metaclass of this type does *NOT* define this method. In
            # this case, describe this type along with all other "normal"
            # PEP-noncompliant types subscripting this union also *NOT* defining
            # this method. Specifically...
            #
            # Note that this is the common case and thus intentionally tested
            # first. By "common case", we mean 99.99999999999% of all types.
            if get_hint_child_violation_str is None:
                # Add this class to the subset of all types this pith violates.
                hint_childs_nonpep.add(hint_child)
            # Else, the metaclass of this type defines this method. In this
            # case, describe this type visually demarcated from the other
            # "normal" PEP-noncompliant types subscripting this union that do
            # *NOT* define this method. Specifically...
            else:
                # Append this child hint's sanified metadata to this list.
                hint_childs_sane_unignorable.append(hint_child_sane)
            # print(f'[union] Appended PEP-noncompliant child hint {hint_child}!')

    # ....................{ PHASE ~ types                  }....................
    # In this next phase, we coerce the "hint_childs_nonpep" subset of all
    # unignorable PEP-noncompliant child hints that are isinstanceable types
    # subscripting this union into a new item of the
    # "hint_childs_sane_unignorable" list of sanified metadata describing the
    # sanification of all unignorable child hints subscripting this union. How?
    # By congealing these one or more isinstanceable types (if defined) into a
    # PEP-noncompliant tuple union of these types.

    # If this pith shallowly violates one or more of the isinstanceable types
    # subscripting this union...
    if hint_childs_nonpep:
        # PEP-noncompliant tuple union of these types.
        hint_childs_nonpep_tuple = (*hint_childs_nonpep,)

        # Sanified metadata describing the sanification of this tuple union.
        hint_childs_nonpep_sane = make_hint_sane(
            hint=hint_childs_nonpep_tuple,
            hint_parent_sane=cause.hint_curr.hint_sane,
        )

        # Prepend this sanified metadata to this list.
        #
        # Note that this sanified metadata is intentionally prepended rather
        # than appended to this list. Since this cause applies *ONLY* to the
        # shallow type of the current pith rather than any items contained in
        # this pith, listing this shallow cause *BEFORE* other deeper causes
        # (which usually apply to items contained in this pith) produces *MUCH*
        # more human-readable exception messages: e.g.,
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
        # fact that this function is only called when a catastrophic
        # type-checking violation has already occurred.
        hint_childs_sane_unignorable.insert(0, hint_childs_nonpep_sane)
    # Else, this pith shallowly satisfies *ALL* of the isinstanceable types
    # subscripting this union.

    # ....................{ PHASE ~ causes                 }....................
    # In this next phase, we generate human-readable causes detailing why this
    # pith violates this union from the filtered "hint_childs_sane_unignorable"
    # list of sanified metadata describing the sanification of all unignorable
    # child hints subscripting this union produced above.

    # For each subscripted argument of this union...
    for hint_child_sane_unignorable in hint_childs_sane_unignorable:
        # Child hint encapsulated by this metadata.
        hint_child = hint_child_sane_unignorable.hint

        # Child hint output cause to be returned, type-checking *ONLY* whether
        # this pith deeply satisfies this child hint.
        cause_child = cause.permute_cause(
            hint_curr=HintDataError(hint_child_sane_unignorable),
            cause_indent=CAUSE_INDENT_CHILD,
        ).find_cause()

        # If this pith deeply satisfies this child hint, this pith necessarily
        # also deeply satisfies this parent union hint. In this case, return
        # this cause.
        if cause_child.cause_str_or_none is None:
            # print('Union child {!r} pith {!r} deeply satisfied!'.format(hint_child, pith))
            return cause
        # Else, this pith deeply violates this child hint.

        # Cause of this violation.
        cause_str = cause_child.cause_str_or_none

        # If this cause is prefixed by the truncated object representation of
        # this pith...
        #
        # Note that this should *ALWAYS* be the case. Nonetheless, let's *NOT*
        # assume anything to avoid exploding everything.
        if cause_str.startswith(pith_repr):
            # Strip the prefixing representation of this pith from this cause
            # (e.g., the prefix "MuhClass <object MuhClass at 0x7fbc277a2cf0>"
            # from the cause 'MuhClass <object MuhClass at 0x7fbc277a2cf0> not
            # instance of <protocol "muh_package.MuhProtocol">'). Why? Because
            # the block of text preceding the bulleted list containing this
            # cause is already redundantly prefixed by this representation.
            cause_str = cause_str[PITH_REPR_INDEX:]
        # Else, this cause is *NOT* prefixed by the truncated object
        # representation of this pith. In this case, silently accept that Bad
        # Things have happened and that we should move to a Bad Future.

        # Append the cause of this violation as a bullet-prefixed line to the
        # running list of these lines.
        cause_strs.append(cause_str)
        # print(f'[union] Appended PEP-compliant child hint {hint_child} cause {cause_str}!')

    # ....................{ PHASE ~ str                    }....................
    # In this final phase, we flatten the human-readable causes detailing why
    # this pith violates this union into a single string such that each of these
    # causes are formatted as bullet points in this string.

    # If prior logic appended *NO* causes, raise an exception.
    #
    # Naturally, this should *NEVER* occur. Naturally, this just occurred.
    if not cause_strs:  # pragma: no cover
        raise _BeartypeCallHintPepRaiseException(
            f'{cause.exception_prefix}type hint '
            f'{repr(cause.hint_curr_sanified)} failure causes unknown.'
        )
    # Else, prior logic appended one or more strings describing these failures.

    # Output cause to be returned, permuted from this input cause such that the
    # output cause justification is either...
    cause_return = cause.permute_cause(cause_str_or_none=(
        # If prior logic appended one cause, a single-line substring intended to
        # be embedded in a longer string;
        f'{pith_repr} {cause_strs[0]}'
        if len(cause_strs) == 1 else
        # Else, prior logic appended two or more causes. In this case, a
        # multiline string comprised of...
        '{}:\n{}'.format(
            # This truncated object representation followed by...
            pith_repr,
            # The newline-delimited concatenation of each cause as a discrete
            # bullet-prefixed line...
            '\n'.join(
                '{}* {}'.format(
                    # Indented by the current indent...
                    cause.cause_indent,
                    # Whose first character is uppercased...
                    uppercase_str_char_first(
                        # Suffixed by a period if not yet suffixed by a period.
                        suffix_str_unless_suffixed(text=cause_str, suffix='.')
                    )
                )
                for cause_str in cause_strs
            )
        )
    ))

    # ....................{ RETURN                         }....................
    # Return this cause.
    return cause_return
