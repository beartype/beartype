#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR)** :pep:`646`
**reducers** (i.e., low-level callables reducing :pep:`646`-compliant type hints
to semantically equivalent type hints already supported by the
:class:`beartype.door.TypeHint` superclass).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDoorPepUnsupportedException
from beartype._check.convert.convmain import sanify_hint_any
from beartype._data.typing.datatypingport import Hint
from beartype._util.hint.pep.proposal.pep646.pep484585646tuple import (
    get_hint_pep484585646_tuple_args_unpacked_if_needed)

# ....................{ REDUCERS                           }....................
def reduce_hint_door_pep646_tuple(hint: Hint) -> Hint:
    '''
    Semantically equivalent type hint already supported by the
    :class:`beartype.door.TypeHint` superclass to which the passed
    :pep:`646`-compliant **fixed-variadic tuple hint** (e.g.,
    ``tuple[int, *tuple[str, ...]]``) reduces if this reduction preserves the
    semantics of this hint *or* raise an exception otherwise.

    Motivation
    ----------
    :pep:`646`-compliant fixed-variadic tuple hints admit three kinds of
    reduction, only the first two of which preserve semantics:

    #. **Exact reduction to a tuple hint.** Unpacking an unpacked child tuple
       hint into its parent tuple hint yields a :pep:`484`- or
       :pep:`585`-compliant tuple hint conveying exactly the same semantics:
       e.g., ``tuple[*tuple[int]]`` is merely a longhand notation for
       ``tuple[int]``, as is ``tuple[int, *tuple[str]]`` for
       ``tuple[int, str]``.
    #. **Exact reduction to the builtin** :class:`tuple` **type.** A tuple hint
       subscripted by *only* an unpacked type variable tuple (e.g.,
       ``tuple[*Ts]``) matches tuples of any length whose items are of any type
       and thus conveys exactly the same semantics as :class:`tuple`.
    #. **Lossy reduction to the builtin** :class:`tuple` **type.** A tuple hint
       subscripted by *both* an unpacked variadic child hint *and* one or more
       other child hints (e.g., ``tuple[int, *tuple[str, ...]]``) constrains the
       items of the tuples it matches. :mod:`beartype` currently type-checks
       such hints only shallowly -- as merely :class:`tuple`. Silently reducing
       such a hint here would thus publish a semantics-eroding reduction
       through the equality and subhint testers of this API, implying (e.g.)
       that ``tuple[int, *Ts]`` is equal to ``tuple[str, *Ts]``. It is not.

    This reducer performs the first two reductions and raises an exception on
    the third, deferring support for the third until :mod:`beartype` deeply
    type-checks these hints.

    Parameters
    ----------
    hint : Hint
        Fixed-variadic tuple hint to be reduced.

    Returns
    -------
    Hint
        Semantically equivalent hint to which this hint reduces.

    Raises
    ------
    BeartypeDoorPepUnsupportedException
        If this hint only reduces to a semantics-eroding hint.
    '''

    # ....................{ REDUCE                         }....................
    # Hint to which this hint reduces, as decided by the same reducers driving
    # the @beartype decorator. Deferring to those reducers guarantees that this
    # API and that decorator agree on the meaning of this hint.
    hint_reduced = sanify_hint_any(hint=hint).hint

    # If this hint reduces to anything other than the builtin "tuple" type, this
    # reduction preserved the child hints subscripting this hint and is thus
    # exact. Return this reduction.
    if hint_reduced is not tuple:
        return hint_reduced  # type: ignore[return-value]
    # Else, this hint reduces to the builtin "tuple" type, discarding *ALL*
    # child hints subscripting this hint.

    # Child hints subscripting this hint, with any unpacked child tuple hint
    # unpacked into this tuple.
    hint_childs = get_hint_pep484585646_tuple_args_unpacked_if_needed(hint)

    # If this hint is subscripted by exactly one child hint, that child hint
    # *MUST* be an unpacked type variable tuple (e.g., "tuple[*Ts]"). Why?
    # Because had that child hint instead been an unpacked child tuple hint,
    # the reduction above would have preserved the child hints subscripting
    # that unpacked child tuple hint. Since an unbound type variable tuple
    # matches any number of arbitrary objects, this reduction is exact. Return
    # this reduction.
    if len(hint_childs) == 1:
        return hint_reduced  # type: ignore[return-value]
    # Else, this hint is subscripted by two or more child hints, at least one of
    # which is an unpacked variadic child hint. This reduction thus erodes the
    # semantics of the remaining child hints.

    # ....................{ RAISE                          }....................
    # Raise a human-readable exception.
    raise BeartypeDoorPepUnsupportedException(
        f'Type hint {repr(hint)} currently unsupported by '
        f'"beartype.door.TypeHint". PEP 646-compliant tuple hints subscripted '
        f'by both an unpacked variadic child hint and one or more other child '
        f'hints are currently type-checked only shallowly (i.e., as merely '
        f'"tuple"). Wrapping this hint would thus imply that (e.g.) '
        f'"tuple[int, *Ts]" is equal to "tuple[str, *Ts]", which is false. '
        f'Consider a PEP 646-compliant tuple hint that preserves its semantics '
        f'when reduced: e.g.,\n'
        f'    # Instead of a mixed fixed-variadic tuple hint...\n'
        f'    tuple[int, *tuple[str, ...]]\n'
        f'\n'
        f'    # Prefer either an unpacked child tuple hint...\n'
        f'    tuple[int, *tuple[str]]\n'
        f'\n'
        f'    # ...or a variadic tuple hint.\n'
        f'    tuple[str, ...]'
    )
