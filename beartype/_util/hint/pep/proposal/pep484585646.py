#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-, :pep:`585`-, and :pep:`646`-compliant **tuple type
hint utilities** (i.e., low-level callables generically applicable to
:pep:`484`- and :pep:`585`-compliant purely fixed- and variadic-length tuple
type hints *and* :pep:`646`-compliant mixed fixed-variadic tuple type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Tuple
from beartype._cave._cavefast import (
    EllipsisType,
    HintPep646TypeVarTupleType,
)
from beartype._data.hint.datahintpep import Hint
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignPep484585TupleFixed,
    HintSignPep484585TupleVariadic,
    HintSignPep646TupleFixedVariadic,
)
from beartype._util.hint.pep.proposal.pep484.pep484 import (
    HINT_PEP484_TUPLE_EMPTY)
from beartype._util.hint.pep.proposal.pep585 import (
    HINT_PEP585_TUPLE_EMPTY)

# ....................{ TESTERS                            }....................
def is_hint_pep484585646_tuple_empty(hint: Hint) -> bool:
    '''
    :data:`True` only if the passed object is either a :pep:`484`- or
    :pep:`585`-compliant **empty fixed-length tuple type hint** (i.e., hint
    constraining objects to be the empty tuple).

    This tester is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as this tester is only called under fairly
    uncommon edge cases.

    Motivation
    ----------
    Since type variables are not themselves types but rather placeholders
    dynamically replaced with types by type checkers according to various
    arcane heuristics, both type variables and types parametrized by type
    variables warrant special-purpose handling.

    Parameters
    ----------
    hint : Hint
        Type hint to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is an empty fixed-length tuple hint.
    '''

    # Return true only if this hint resembles either the PEP 484- or
    # 585-compliant fixed-length empty tuple type hint. Since there only exist
    # two such hints *AND* comparison against these hints is mostly fast, this
    # test is efficient in the general case.
    #
    # Note that this test may also be inefficiently performed by explicitly
    # obtaining this hint's sign and then subjecting this hint to specific
    # tests conditionally depending on which sign and thus PEP this hint
    # complies with: e.g.,
    #     # Return true only if this hint is either...
    #     return true (
    #         # A PEP 585-compliant "tuple"-based hint subscripted by no
    #         # child hints *OR*...
    #         (
    #             hint.__origin__ is tuple and
    #             hint_childs_len == 0
    #         ) or
    #         # A PEP 484-compliant "typing.Tuple"-based hint subscripted
    #         # by exactly one child hint *AND* this child hint is the
    #         # empty tuple,..
    #         (
    #             hint.__origin__ is Tuple and
    #             hint_childs_len == 1 and
    #             hint_childs[0] == ()
    #         )
    #     )
    return (
        hint == HINT_PEP585_TUPLE_EMPTY or
        hint == HINT_PEP484_TUPLE_EMPTY
    )

# ....................{ GETTERS                            }....................
#FIXME: Note that this getter now exhibits worst-case O(n) time complexity for n
#the number of child hints subscripting this tuple hint. Since this getter is
#only called by the memoized parent get_hint_pep_sign_or_none() getter, this
#inefficiency is ignorable.
#FIXME: Unit test us up, please.
def get_hint_pep484585646_tuple_sign_unambiguous(hint: Hint) -> HintSign:
    '''
    Disambiguate the passed **tuple type hint** (i.e., :pep:`484`- or
    :pep:`585`-compliant purely fixed- and variable-length tuple type hint *or*
    :pep:`646`-compliant mixed fixed-variadic tuple type hint) ambiguously
    identified by the :data:`.HintSignTuple` sign into whichever of the
    unambiguous :data:`.HintSignPep484585TupleFixed`,
    :data:`HintSignPep484585TupleVariadic`, or
    :data:`HintSignPep646TupleFixedVariadic` signs uniquely identify this kind
    of tuple type hint.

    This low-level getter assists the higher-level
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_sign` getter to
    disambiguate the originally ambiguous :data:`.HintSignTuple` sign.

    Parameters
    ----------
    hint : Hint
        Type hint to be inspected.

    Returns
    -------
    HintSign
        Sign uniquely and unambiguously identifying this hint. Specifically, if
        this hint is a:

        * :pep:`484`- or :pep:`585`-compliant **fixed-length tuple hint** (e.g.,
          of the form ``tuple[{hint_child_1}, ..., {hint_child_N}]``), this
          getter returns :data:`.HintSignPep484585TupleFixed`.
        * :pep:`484`- or :pep:`585`-compliant **variable-length tuple hint**
          (e.g., of the form ``tuple[{hint_child}, ...]``), this getter returns
          :data:`.HintSignPep484585TupleVariadic`.
        * :pep:`646`-compliant **fixed-variable tuple hint** (e.g., of the form
          ``tuple[{hint_child_1}, ..., {type_var_tuple}, ...,
          {hint_child_N}]``), this getter returns
          :data:`.HintSignPep646TupleFixedVariadic`.
    '''

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype._util.hint.pep.proposal.pep646 import (
        is_pep646_hint_tuple_unpacked)
    from beartype._util.hint.pep.utilpepget import get_hint_pep_args

    # ....................{ LOCALS                         }....................
    # Child hints subscripting this parent tuple hint.
    hint_childs = get_hint_pep_args(hint)
    # print(f'hint_childs: {hint_childs}')

    # Number of child hints subscripting this parent tuple hint.
    hint_childs_len = len(hint_childs)

    # ....................{ PEP (484|585) ~ variadic       }....................
    # If this parent tuple hint is subscripted by *NO* child hints, this hint is
    # the unsubscripted "typing.Tuple" type hint factory semantically equivalent
    # to the PEP 484-compliant variable-length tuple hint "typing.Tuple[object,
    # ...]". In this case, return the sign uniquely identifying these hints.
    if not hint_childs_len:
        return HintSignPep484585TupleVariadic
    # Else, this parent tuple hint is subscripted by one or more child hints.

    # ....................{ PEP 646                        }....................
    # For each child hint subscripting this parent tuple hint...
    for hint_child in hint_childs:
        # If this child hint is either...
        if (
            #FIXME: *NO*. Check signs instead, please. *sigh*
            # A PEP 646-compliant type variable tuple *OR*...
            isinstance(hint_child, HintPep646TypeVarTupleType) or
            # A PEP 646-compliant unpacked child tuple hint...
            is_pep646_hint_tuple_unpacked(hint_child)
        ):
            # Then this parent tuple hint is PEP 646-compliant. In this case,
            # return the sign uniquely identifying these hints.
            return HintSignPep646TupleFixedVariadic
        # Else, this child hint is PEP 484- or 585-compliant.
    # Else, all child hints subscripting this parent tuple hint are *ONLY* PEP
    # 484- or 585-compliant, implying this parent tuple hint to itself be PEP
    # 484- or 585-compliant.

    # ....................{ PEP (484|585) ~ variadic       }....................
    #FIXME: Move most of this into reduce_hint_pep646_tuple(), please. *sigh*
    # Return the sign uniquely identifying either...
    return (
        # Variable-length tuple hints if either...
        HintSignPep484585TupleVariadic
        if (
            # This parent tuple hint is subscripted by *NO* child hints
            # and is thus the unsubscripted "typing.Tuple" type hint factory
            # semantically equivalent to the variable-length tuple hint
            # "typing.Tuple[object, ...]" *OR*...
            hint_childs_len == 0 or
            (
                # This parent tuple hint is subscripted by exactly one child
                # hint *AND*...
                hint_childs_len == 1 and
                #FIXME: *NO*. Check signs instead, please. *sigh*
                # This child hint is a PEP 646-compliant type variable tuple
                # (e.g., the "*Ts" in "tuple[*Ts]"). The justification here is
                # somewhat subtle. @beartype ultimately silently ignores all
                # type hints resembling type variables. This includes type
                # variable tuples. Whereas a conventional type variable is
                # trivially reducible to the ignorable "typing.Any" singleton,
                # however, type variable tuples are only reducible to the less
                # ignorable PEP 646-compliant unpacked child tuple hint
                # "*tuple[typing.Any, ...]". Equivalently, type variable tuples
                # imply *VARIADICITY* (i.e., a requirement that zero or more
                # tuple items be matched). This requirement *CANNOT* be
                # trivially ignored. Ergo, any PEP 646-complaint parent tuple
                # hint of the form "tuple[*Ts]" for *ANY* type variable tuple
                # "*Ts" is reducible to the also PEP 646-compliant parent tuple
                # hint "tuple[*tuple[typing.Any, ...]]", which unpacks to the
                # PEP 646-*AGNOSTIC* parent tuple hint "tuple[typing.Any, ...]",
                # which then simply reduces to the builtin "tuple" type. Since
                # this PEP 646-compliant hint semantically reduces to the
                # simplest PEP 484- or 585-compliant variable-length hint,
                # treating PEP 646-compliant hints of this form as equivalent to
                # PEP 484- or 585-compliant variable-length hints is sensible.
                isinstance(hint_childs[0], HintPep646TypeVarTupleType)
            ) or
            (
                # This parent tuple hint is subscripted by exactly two child
                # hints *AND*...
                hint_childs_len == 2 and

                #FIXME: *NO*. Check signs instead, please. *sigh*
                #FIXME: Remove the "_HintPep484585TupleVariadicSecondItemTypes"
                #tuple global, please. Nice idea, but it simply doesn't work.
                #Instead, consider defining a new frozenset global
                #"HINT_SIGNS_PEP484585_TUPLE_VARIADIC_HINT_CHILD_LAST" somewhere
                #-- but only if we decide we actually still need this.

                # The second child hint is either:
                # * The PEP 484- or 585-compliant ellipsis singleton (e.g., the
                #   unquoted character sequence "..." in "tuple[str, ...]").
                # * A PEP 646-compliant type variable tuple (e.g., the "*Ts" in
                #   "tuple[float, *Ts]").
                #
                # The justification for the latter is similar to the prior
                # justification for the treatment of PEP 646-compliant tuple
                # type hints of the form "tuple[*Ts]" as equivalent to "tuple".
                # Recall that the PEP 646-complaint unpacked child tuple hint
                # "*tuple[typing.Any, ...]" conveys a requirement that zero or
                # more tuple items be matched. Then in this related case, a PEP
                # 646-compliant tuple type hint of the longer form
                # "tuple[hint_child, *Ts]" for *ANY* child hint "hint_child" and
                # type variable tuple "*Ts" is reducible by the same argument to
                # "tuple[hint_child, *tuple[typing.Any, ...]]", which unpacks to
                # the familiar PEP 484- or 585-compliant parent tuple hint
                # "tuple[hint_child, ...]". Again, this reduction is sensible.
                isinstance(
                    hint_childs[1], _HintPep484585TupleVariadicSecondItemTypes)
            )
        ) else
        #FIXME: Differentiate "HintSignPep484585TupleFixed"- from
        #"HintSignPep646TupleFixedVariadic"-style tuple type hints here, please.
        #The distinction here is as follows:
        #* If this parent tuple hint contains one or more child hints satisfying
        #  the following condition, return "HintSignPep646TupleFixedVariadic";
        #  else, return "HintSignPep484585TupleFixed": e.g.,
        #      hints_child = get_hint_pep_args(hint)
        #      for hint_child in hints_child:
        #          if (
        #              isinstance(child_hint, HintPep646TypeVarTupleType) or
        #              is_pep646_hint_tuple_unpacked(child_hint)
        #          ):
        #              return HintSignPep646TupleFixedVariadic
        #      return HintSignPep484585TupleFixed

        # Fixed-length tuple hints otherwise.
        HintSignPep484585TupleFixed
    )

# ....................{ FACTORIES                          }....................
#FIXME: Unit test us up, please.
def make_hint_pep484585646_tuple_fixed(hints: tuple) -> Hint:
    '''
    :pep:`484`- or :pep:`585`-compliant **fixed-length tuple type hint** of the
    form ``tuple[{hint_child1}, ???, {hint_childN}]`` subscripted by all
    PEP-compliant child type hints in the passed tuple.

    Parameters
    ----------
    hints : tuple
        Tuple of all child type hints to subscript this tuple type hint with.

    Returns
    -------
    Hint
        Fixed-length tuple type hint subscripted by these child type hints.
    '''
    assert isinstance(hints, tuple), f'{repr(hints)} not tuple.'

    # Return a fixed-length tuple type hint subscripted by these child type
    # hints, defined as either...
    return (
        #FIXME: Uncomment after dropping Python <= 3.10 support, which raises a
        #"SyntaxError" if we even try doing this. *SADNESS*
        # # If the active Python interpreter targets Python >= 3.11 and thus
        # # supports list unpacking in arbitrary expressions, prefer an efficient
        # # expression leveraging a list unpacking;
        # Tuple[*hints]
        # if IS_PYTHON_AT_LEAST_3_11 else
        # Else, the active Python interpreter targets Python <= 3.10.
        #
        # Dynamically subscript the builtin "tuple" type.
        Tuple.__class_getitem__(hints)  # type: ignore[attr-defined]
    )

# ....................{ PRIVATE                            }....................
_HintPep484585TupleVariadicSecondItemTypes = (
    # PEP 484- or 585-compliant ellipsis (e.g., the "..." in "tuple[str, ...]").
    EllipsisType,
    # PEP 646-compliant type variable tuple (e.g., the "*Ts" in
    # "tuple[float, *Ts]").
    HintPep646TypeVarTupleType,
)
'''
Tuple of all :pep:`484`- and :pep:`585`-compliant **purely variable-length tuple
type hint second item types** (i.e., types of all child hints permissible as the
second and final items subscripting purely variable-length tuple type hints).
'''
