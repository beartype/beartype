#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`646`-compliant **tuple type hint reducers** (i.e., low-level
callables converting parent tuple hints subscripted by either a
:pep:`646`-compliant type variable tuples *or* :pep:`646`-compliant unpacked
child tuple hint to lower-level type hints more readily consumable by
:mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Currently, we only shallowly type-check PEP 646-compliant mixed
#fixed-variadic tuple hints as... tuples. It's not much. Obviously, we need to
#deeply type-check these tuple data structures as soon as feasible. There exist
#two distinct use cases here:
#* Fixed-variadic tuple hints containing exactly one unpacked child tuple hint
#  (e.g., "tuple[int, *tuple[str, ...], float]"). Note that a tuple hint may
#  only contain *AT MOST* one unpacked child tuple hint.
#* Fixed-variadic tuple hints containing exactly one type variable tuple, either
#  as:
#  * The first child hint (e.g., "tuple[*Ts, int]").
#  * The last child hint (e.g., "tuple[str, bytes, *Ts]"). Note that this case
#    has a prominent edge case. Fixed-variadic tuple hints of the form
#    "tuple[hint_child, *Ts]" for *ANY* "hint_child" and type variable tuple
#    "Ts" trivially reduce to variadic tuple hints of the form
#    "tuple[hint_child, ...]" at the moment, as we silently ignore *ALL* type
#    variable tuples. Ergo, if a hint is a fixed-variadic tuple hint whose last
#    child hint is a type variable tuple, this hint *MUST* by definition be
#    prefixed by two or more child hints that are *NOT* type variable tuples.
#  * Any child hint other than the first or last (e.g.,
#    "tuple[float, *Ts, bool]").
#
#  Note that:
#  * A parent tuple hint can contain at most *ONE* unpacked child tuple hint.
#    So, we'll now need to record the number of unpacked child tuple hints that
#    have been previously visited and raise an exception if two or more are
#    seen. Ugh!
#  * Again, these cases have a prominent edge case. Fixed-variadic tuple hints
#    of the form "tuple[*Ts]" for *ANY* type variable tuple "Ts" trivially
#    reduce to the builtin type "tuple" at the moment, as we silently ignore
#    *ALL* type variable tuples.
#
#Unsure whether fixed-variadic tuple hints can contain both a type variable
#tuple *AND* unpacked child tuple hint (e.g., "tuple[*Ts, *tuple[int, ...]]")?
#Probably. Yet more edge cases arise, of course. PEP 646 is a beast with many
#backs, indeed.
#
#The first place to start with all of this is implementing a new code generation
#algorithm for the new "HintSignPep646TupleFixedVariadic" sign, which currently
#just shallowly reduces to the builtin "tuple" type. Obviously, that's awful.
#The first-draft implementation of this algorithm should just focus on
#fixed-variadic tuple hints containing exactly one type variable tuple (e.g.,
#"tuple[float, *Ts, bool]") for now, as that's the simpler use case. Of course,
#even that's *NOT* simple -- but it's a more reasonable start than unpacked
#child tuple hints, which spiral into madness far faster and harder.
#
#This code generation algorithm should manually detect and handle both type
#variable tuples *AND* unpacked child tuple hints *BEFORE* performing child
#hint reductions by calling reduce_hint_child(). Why? Because the reducers
#defined below currently unconditionally ignore type variable tuples. We don't
#even bother ignoring unpacked child tuple hints at the moment, because they can
#*ONLY* appear inside a "tuple[...]" context.
#
#Lastly, note that we can trivially handle unpacked child tuple hints in a
#simple, effective way *WITHOUT* actually investing any effort in doing so. How?
#By simply treating each unpacked child tuple hint as a type variable tuple
#(e.g., by treating "tuple[str, *tuple[int, ...], bytes]" as equivalent to
#"tuple[str, *Ts, bytes]"). Since we already need to initially handle type
#variable tuples anyway, we shatter two birds with one hand. Yes! Yes!

#FIXME: Raise an exception if a tuple hint contains two or more:
#* Type variable tuples.
#* Unpacked child tuple hints.
#
#Note that this is best done during code generation, where we already
#necessarily iterate over all child hints and their indices. Ergo, we defer
#performing this validation until we begin generating code for this.
#
#When we're ready to do so, note that we've already documented the exceptions to
#be raised by this validation as follows:
#    Raises
#    ------
#    BeartypeDecorHintPep646Exception
#        If this tuple hint is subscripted by either:
#
#        * Two or more :pep:`646`-compliant type variable tuples.
#        * Two or more :pep:`646`-compliant unpacked child tuple hints.
#        * Two or more :pep:`646`-compliant type variable tuples.
#        * A :pep:`646`-compliant type variable tuple *and* an unpacked child
#          tuple hint.

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep646Exception
# from beartype.typing import Optional
from beartype._data.hint.datahintpep import Hint
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignPep646TupleUnpacked,
    HintSignUnpack,
)
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_PEP646_TUPLE_HINT_CHILD_UNPACKED)
from beartype._util.hint.pep.proposal.pep484585646 import (
    make_hint_pep484585646_tuple_fixed)
from beartype._util.hint.pep.utilpepget import get_hint_pep_args
from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign_or_none

# ....................{ REDUCERS                           }....................
#FIXME: Unit test us up, please.
def reduce_hint_pep646_tuple(
    hint: Hint, exception_prefix: str, **kwargs) -> Hint:
    '''
    Reduce the passed :pep:`646`-compliant **tuple hint** (i.e., parent tuple
    hints subscripted by either a :pep:`646`-compliant type variable tuples *or*
    :pep:`646`-compliant unpacked child tuple hint) to a more readily digestible
    hint.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : object
        :pep:`646`-compliant tuple hint to be reduced.
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    Returns
    -------
    Hint
        Lower-level hint currently supported by :mod:`beartype`.
    '''

    # ....................{ LOCALS                         }....................
    # Tuple of the one or more child hints subscripting this parent tuple hint.
    #
    # Note that the previously called
    # get_hint_pep484585646_tuple_sign_unambiguous() getter responsible for
    # disambiguating PEP 484- and 585-compliant tuple hints from this PEP
    # 646-compliant tuple hint has already pre-validated this tuple hint to be
    # subscripted by two or more child hints.
    hint_childs = get_hint_pep_args(hint)

    # Number of child hints subscripting this parent tuple hint.
    hint_childs_len = len(hint_childs)

    # Assert this parent tuple hint is subscripted by at least one child hint.
    # Note that the previously called
    # get_hint_pep484585646_tuple_sign_unambiguous() getter should have already
    # guaranteed this. Ergo, we avoid raising a full-blown exception here.
    assert hint_childs_len >= 1, (
        f'PEP 646 tuple hint {repr(hint)} subscripted by no child hints.')

    #FIXME: Interestingly, there's a final reduction that can be performed.
    #Fixed-length unpacked child tuple hints (e.g., "tuple[int, *tuple[str,
    #float]]") are nonsensical, because the child child hints subscripting those
    #child tuple hints could have simply directly subscripted this parent tuple
    #hint as a PEP 585-compliant fixed-length tuple hint. Thus, do so (e.g.,
    #from "tuple[int, *tuple[str, float]]" to "tuple[int, str, float]").
    #
    #Fixed-length unpacked child tuple hints are any *EXCEPT* variable-length
    #unpacked child tuple hints, detected as 2-tuples suffixed by an ellipsis.
    #FIXME: We probably want to define a new utility tester resembling:
    #    def is_hint_pep484585646_tuple_variadic(hint: Hint) -> bool:
    #        # Child hints subscripting this tuple hint.
    #        hint_childs = get_hint_pep_args(hint)
    #
    #        return (
    #            # This parent tuple hint is subscripted by exactly two child hints
    #            # *AND*...
    #            len(hint_childs) == 2 and
    #            # This second child hint is the PEP 484- and 585-compliant ellipsis
    #            # singleton (e.g., the unquoted character sequence "..." in
    #            # "tuple[str, ...]").
    #            hint_childs[1] is Ellipsis
    #        )
    #FIXME: Replace the DRY violation repeating this test in
    #get_hint_pep484585646_tuple_sign_unambiguous() with a call to this new
    #is_hint_pep484585646_tuple_variadic() tester.
    #FIXME: Grep the codebase for any similar DRY violations referencing the
    #"Ellipsis" singleton as well, please. *sigh*
    #FIXME: Interestingly, since performing this reduction requires iteration
    #over all child hints of this parent tuple hint, we'd might as well validate
    #that this parent tuple hint contains at most one PEP 646-compliant child
    #hint. To ensure this validation *ALWAYS* occurs, we'll thus need to perform
    #this iteration first *BEFORE* attempting any further reductions below.

    # ....................{ CHILDS                         }....................
    # If this parent tuple hint is subscripted by exactly one child hint...
    if hint_childs_len == 1:
        # Child hint subscripting this parent tuple hint.
        hint_child = hint_childs[0]

        # Sign uniquely identifying the child hint subscripting this parent
        # tuple hint if this child hint is PEP-compliant *OR* "None" otherwise.
        hint_child_sign = get_hint_pep_sign_or_none(hint_child)

        # If this child hint is a PEP 646-compliant unpacked type variable tuple
        # (e.g., the "*Ts" in "tuple[*Ts]"), reduce this PEP 646-compliant tuple
        # hint to the builtin "tuple" type.
        #
        # The justification here is somewhat subtle. @beartype currently ignores
        # all type parameters -- including both PEP 484-compliant type variables
        # and 646-compliant type variable tuples. Whereas a conventional type
        # variable is trivially reducible to the ignorable "typing.Any"
        # singleton, however, type variable tuples are only reducible to the
        # less ignorable PEP 646-compliant unpacked child tuple hint
        # "*tuple[typing.Any, ...]". Type variable tuples imply *VARIADICITY*
        # (i.e., a requirement that zero or more tuple items be matched). This
        # requirement *CANNOT* be trivially ignored. Ergo, any PEP 646-complaint
        # parent tuple hint of the form "tuple[*Ts]" for *ANY* type variable
        # tuple "*Ts" is reducible to the also PEP 646-compliant parent tuple
        # hint "tuple[*tuple[typing.Any, ...]]", which unpacks to the PEP
        # 646-*AGNOSTIC* parent tuple hint "tuple[typing.Any, ...]", which then
        # simply reduces to the builtin "tuple" type.
        if hint_child_sign is HintSignUnpack:
            return tuple
        # Else, this child hint is *NOT* a PEP 646-compliant unpacked type
        # variable tuple.
        #
        # If this child hint is a PEP 646-compliant unpacked child tuple hint
        # (e.g., the "*tuple[str, ...]" in "tuple[*tuple[str, ...]]"), reduce
        # this PEP 646-compliant tuple hint to the semantically equivalent PEP
        # 585-compliant tuple hint subscripted by the child child hints
        # subscripting this unpacked child tuple hint (e.g., from
        # "tuple[*tuple[str, ...]]" to "tuple[str, ...]"). This could be
        # regarded as a non-recursive "unboxing" or "unpacking" operation.
        #
        # Note that this edge case is syntactically permitted by PEP 646 for
        # orthogonality, despite being semantically superfluous and thus
        # conveying *NO* meaningful typing not already conveyed by the simpler
        # PEP 585-compliant tuple hint that this PEP 646-compliant tuple hint
        # reduces to. So it goes, Pythonistas. So it goes.
        elif hint_child_sign is HintSignPep646TupleUnpacked:
            # Tuple of the zero or more child child hints subscripting this
            # unpacked child tuple hint.
            #
            # Note that the CPython parser itself prevents unpacked child tuple
            # hints from being trivially subscripted by *NO* child child hints.
            # Interestingly, doing so is still non-trivially feasible by the
            # standard empty tuple "()" trick: e.g.,
            #     >>> tuple[*tuple[]]
            #                ^^^^^^^
            #     SyntaxError: invalid syntax. Perhaps you forgot a comma?
            #
            #     >>> tuple[*tuple[()]]
            #     tuple[*tuple[()]]
            hint_child_childs = get_hint_pep_args(hint_child)

            # Reduce this PEP 646-compliant tuple hint to the semantically
            # equivalent PEP 585-compliant tuple hint subscripted by the child
            # child hints subscripting this unpacked child tuple hint.
            return make_hint_pep484585646_tuple_fixed(hint_child_childs)
        # Else, this child hint is *NOT* a PEP 646-compliant unpacked child
        # tuple hint.

        # Raise a fatal exception. Why? Because the previously called
        # get_hint_pep484585646_tuple_sign_unambiguous() getter already
        # validated this tuple hint to be PEP 646-compliant and thus be
        # subscripted by one or more PEP 646-compliant child hints... Yet this
        # hint is subscripted by only one PEP 646-noncompliant child hint!
        raise BeartypeDecorHintPep646Exception(  # pragma: no cover
            f'{exception_prefix}PEP 646 tuple type hint {repr(hint)} '
            f'child hint {repr(hint_child)} not PEP 646-compliant '
            f'(i.e., neither unpacked type variable tuple nor '
            f'unpacked child tuple type hint).'
        )
    # Else, this parent tuple hint is *NOT* subscripted by one child hint.
    #
    # If this parent tuple hint is subscripted by exactly two child hints...
    elif hint_childs_len == 2:
        # Signs uniquely identifying the first and second child hints
        # subscripting this parent tuple hint if these child hints are
        # PEP-compliant *OR* "None" otherwise.
        hint_child_1_sign = get_hint_pep_sign_or_none(hint_childs[0])
        hint_child_2_sign = get_hint_pep_sign_or_none(hint_childs[1])

        # If this first child hint is not PEP 646-compliant but this second
        # child hint is a PEP 646-compliant unpacked type variable tuple (e.g.,
        # the "*Ts" in "tuple[str, *Ts]"), reduce this PEP 646-compliant tuple
        # hint to the semantically equivalent PEP 585-compliant tuple hint
        # subscripted by the same first child hint followed by an ellipsis
        # (e.g., from "tuple[str, *Ts]" to "tuple[str, ...]").
        #
        # The justification here is similar to the prior justification for the
        # treatment of PEP 646-compliant tuple type hints of the form
        # "tuple[*Ts]" as equivalent to "tuple". Recall that the PEP
        # 646-complaint unpacked child tuple hint "*tuple[typing.Any, ...]"
        # conveys a requirement that zero or more tuple items be matched. Then
        # in this related case, a PEP 646-compliant tuple type hint of the
        # longer form "tuple[hint_child, *Ts]" for *ANY* child hint "hint_child"
        # and type variable tuple "*Ts" is reducible by the same argument to
        # "tuple[hint_child, *tuple[typing.Any, ...]]", which unpacks to the
        # familiar PEP 484- or 585-compliant parent tuple hint
        # "tuple[hint_child, ...]".
        #
        # Specifically...
        if (
            # If this first child hint is neither:
            # * A PEP 646-compliant type variable tuple *OR*...
            # * A PEP 646-compliant unpacked child tuple hint...
            #
            # ...then this first child hint is *NOT* PEP 646-compliant. In this
            # case, this PEP 646-compliant tuple hint *COLUD* be reducible to a
            # simpler PEP 585-compliant variable-length tuple hint.
            hint_child_1_sign not in (
                HINT_SIGNS_PEP646_TUPLE_HINT_CHILD_UNPACKED) and
            # *AND* this second child hint is a PEP 646-compliant unpacked type
            # variable tuple...
            hint_child_2_sign is HintSignUnpack
        ):
            # Tuple of the exactly two child hints with which to subscript this
            # semantically equivalent PEP 585-compliant tuple hint.
            hint_childs_new = (hint_childs[0], ...)

            # Reduce this PEP 646-compliant tuple hint to this replacement.
            return make_hint_pep484585646_tuple_fixed(hint_childs_new)
        # Else, this second child hint is *NOT* a PEP 646-compliant unpacked
        # type variable tuple.
    # Else, this parent tuple hint is subscripted by three or more child hints.
    # Since this hint is irreducible, preserve this hint as is.

    # ....................{ RETURN                         }....................
    #FIXME: *STOP DOING THIS* as soon as we implement a proper code generator
    #for PEP 646-compliant tuple hints, please. *sigh*
    # Reduce this non-trivial PEP 646-compliant tuple hint to the builtin
    # "tuple" type as a temporary means of shallowly ignoring *ALL* child hints
    # subscripting this hint. Although obviously non-ideal, this simplistic
    # approach does have the benefit of actually working -- an improvement over
    # our prior approach of raising fatal exceptions for these hints.
    return tuple
