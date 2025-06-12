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
from beartype._data.hint.datahintpep import Hint
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignTuple,
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
#FIXME: *WEIRD API.* Why do we need the caller to explicitly pass "hint_sign".
#Shouldn't the caller only ever call this function when the caller knows that
#"hint_sign is HintSignTuple"? Ideally, the signature should be reduced to:
#    def get_hint_pep484585646_sign_tuple(hint: object) -> HintSign:
#FIXME: Detect "HintSignPep646TupleFixedVariadic"-style tuple type hints. *sigh*
#FIXME: Docstring us up, please.
#FIXME: Unit test us up, please.
def get_hint_pep484585646_sign_tuple(
    hint: Hint, hint_sign: HintSign) -> HintSign:
    '''
    The passed sign as is if this sign is other than the ambiguous
    :data:`.HintSignTuple` sign *or* the unambiguous
    :data:`.HintSignPep484585TupleFixed` sign if the passed hint is a
    fixed-length tuple hint.

    This low-level getter assists the higher-level
    :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_sign` getter to
    disambiguate the originally ambiguous :data:`.HintSignTuple` sign as
    follows. If this hint is a:

    * :pep:`484`- or :pep:`585`-compliant fixed-length tuple hint,
      :data:`.HintSignPep484585TupleFixed`.
    * :pep:`484`- or :pep:`585`-compliant variable-length tuple hint,
      :data:`.HintSignTuple`.
    * :pep:`646`-compliant mixed fixed-variable tuple hint,
      :data:`.HintSignPep646TupleFixedVariadic`.

    Parameters
    ----------
    hint : Hint
        Type hint to be inspected.
    hint_sign : HintSign
        Sign uniquely (but possibly ambiguously) identifying this hint.

    Returns
    -------
    HintSign
        Sign uniquely and unambiguously identifying this hint.
    '''
    assert isinstance(hint_sign, HintSign), f'{repr(hint_sign)} not sign.'

    # If this is a tuple hint, disambiguate between the following three
    # fundamentally distinct kinds of tuple hints:
    # * Fixed-length tuple type hints of the form
    #   "tuple[{hint_child_1}, ..., {hint_child_N}]", which this getter
    #   unambiguously reassigns the sign "HintSignPep484585TupleFixed".
    # * Variable-length tuple type hints of the form
    #   "tuple[{hint_child_1}, ...]", which this getter unambiguously
    #   preserves the sign "HintSignTuple".
    if hint_sign is HintSignTuple:
        # Avoid circular import dependencies.
        from beartype._util.hint.pep.utilpepget import get_hint_pep_args

        # Child hints subscripting this parent tuple hint.
        hint_childs = get_hint_pep_args(hint)
        # print(f'hint_childs: {hint_childs}')

        # Number of child hints subscripting this parent tuple hint.
        hint_childs_len = len(hint_childs)

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
                    # This parent tuple hint is subscripted by exactly two child
                    # hints *AND*...
                    hint_childs_len == 2 and
                    # The second child hint is the ellipsis singleton (i.e.,
                    # the unquoted character sequence "...")...
                    hint_childs[1] is Ellipsis
                )
            ) else
            # Fixed-length tuple hints otherwise.
            HintSignPep484585TupleFixed
        )
    # Else, this is *NOT* a tuple hint.

    # Return this sign.
    return hint_sign

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
