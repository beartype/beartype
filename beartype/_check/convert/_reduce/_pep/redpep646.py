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

#FIXME: [PEP 692] *LOL*. "Tuple[*Ts] == Tuple[Unpack[Ts]] == Tuple[object]"
#after reduction, a fixed-length tuple hint. Clearly, however,
#"Tuple[Unpack[Ts]]" should instead be semantically equivalent to a variadic
#tuple hint: e.g.,
#    # This is what we want! Tuple[*Ts] == Tuple[Unpack[Ts]] ==
#    Tuple[Any, ...]
#
#See commentary in "data_pep646" for how to address this. *sigh*

#FIXME: [PEP 692] Actually implement deep type-checking support for PEP
#692-compliant unpack type hints of the form "**kwargs:
#typing.Unpack[UserTypedDict]". Doing so will *ALMOST CERTAINLY* necessitate a
#new logic pathway for dynamically generating type-checking code efficiently
#type-checking the passed variadic keyword argument dictionary "**kwargs"
#against that user-defined "UserTypedDict". Feasible, but non-trivial. *sigh*

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep646Exception
# from beartype.typing import Optional
from beartype._data.hint.datahintpep import Hint
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignTypeVarTuple,
)
from beartype._util.hint.pep.utilpepget import get_hint_pep_args
from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign_or_none

# ....................{ REDUCERS                           }....................
#FIXME: Map this in "_redmap", please. *sigh*
#FIXME: Raise an exception if a tuple hint contains two or more:
#* Type variable tuples.
#* Unpacked child tuple hints.
def reduce_hint_pep646_tuple(
    hint: Hint,
    exception_prefix: str,
    **kwargs
) -> Hint:
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

    Raises
    ------
    BeartypeDecorHintPep646Exception
        If this tuple hint is subscripted by either:

        * Two or more :pep:`646`-compliant type variable tuples.
        * Two or more :pep:`646`-compliant unpacked child tuple hints.
        * Two or more :pep:`646`-compliant type variable tuples.
        * A :pep:`646`-compliant type variable tuple *and* an unpacked child
          tuple hint.
    '''

    # ....................{ LOCALS                         }....................
    # Tuple of the one or more child hints subscripting this parent tuple hint.
    # Note that the previously called
    # get_hint_pep484585646_tuple_sign_unambiguous() getter responsible for
    # disambiguating PEP 484- and 585-compliant tuple hints from this PEP
    # 646-compliant tuple hint has already pre-validated this tuple hint to be
    # subscripted by two or more child hints.
    hints_child = get_hint_pep_args(hint)

    # # ....................{ PEP 646                        }....................
    # # If this child hint is *NOT* a PEP 646-compliant "typing.TypeVarTuple"
    # # object, raise an exception.
    # if hint_child_sign is not HintSignTypeVarTuple:
    #     raise BeartypeDecorHintPep646Exception(
    #         f'{exception_prefix}PEP 646 unpack type hint {repr(hint)} '
    #         f'child type hint {repr(hint_child)} not '
    #         f'PEP 646 type variable tuple '
    #         f'(i.e., "typing.TypeVarTuple" object).'
    #     )
    # # Else, this child hint is a PEP 646-compliant "typing.TypeVarTuple" object.

    # Reduce this non-trivial PEP 646-compliant tuple hint to the builtin
    # "tuple" type as a temporary means of shallowly ignoring *ALL* child hints
    # subscripting this hint. Although obviously non-ideal, this simplistic
    # approach does have the benefit of actually working -- an improvement over
    # our prior approach of raising fatal exceptions for these hints.
    return tuple
