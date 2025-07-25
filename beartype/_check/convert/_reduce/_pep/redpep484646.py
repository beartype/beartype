#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- or :pep:`646`-compliant **type parameter reducers**
(i.e., low-level callables converting arbitrary hints parametrized by zero or
more :pep:`484`-compliant type variables and/or :pep:`646`-compliant type
variable tuples to lower-level type hints more readily consumable by
:mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: [PEP 696] Handle "PEP 696 – Type Defaults for Type Parameters" under
#Python >= 3.13:
#    https://peps.python.org/pep-0696
#
#This PEP induces edge cases in _make_hint_pep484646_typeargs_to_hints().
#Notably, when the caller passes more type parameters than child hints to that
#factory, we currently silently ignore and thus preserve those "excess" type
#parameters. Under Python >= 3.13, however, we *MUST* instead now:
#* Manually iterate over those any excess *LEADING* type parameters in
#  left-to-right parametrization order. For each such parameter:
#  * If that type parameter defines a default, map that parameter to that
#    default.
#  * Else, halt this iteration immediately.
#
#Note that:
#* This does apply to both PEP 484-compliant type variables *AND* PEP
#  646-compliant unpacked type variable tuples. Both can be defaulted.
#* This does *NOT* apply to *TRAILING* type parameters. PEP 696 mandates that
#  @beartype should raise an exception if *ANY* trailing type parameter
#  following an unpacked type variable tuple has a default. Just "Ugh!"

#FIXME: [PEP 612] *WOOPS.* Generics can be subscripted by PEP 612-compliant
#parameter specifications: e.g.,
#    # This example literally appears in PEP 696.
#    Ts = TypeVarTuple("Ts")
#    P = ParamSpec("P", default=[float, bool])
#    class Foo(Generic[Ts, P]): ...  # Valid
#
#Brutal. Welp. Let's implement that if somebody actually complains about that,
#please. Doing so will warrant renaming this reducer to "redpep484612646" and
#generalizing everything below. Pretty annoying, but... what can you do? *sigh*

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep484612646Exception
from beartype.typing import Optional
from beartype._check.metadata.hint.hintsane import (
    HintOrSane,
    HintSane,
)
from beartype._check.pep.checkpep484typevar import (
    die_if_hint_pep484_typevar_bound_unbearable)
from beartype._data.error.dataerrmagic import EXCEPTION_PLACEHOLDER
from beartype._data.hint.sign.datahintsigncls import HintSign
from beartype._data.hint.sign.datahintsigns import (
    HintSignTypeVar,
    HintSignPep646UnpackedTypeVarTuple,
)
from beartype._data.typing.datatyping import (
    Pep484646TypeArg,
    TuplePep484646TypeArgs,
)
from beartype._data.typing.datatypingport import (
    Hint,
    Pep484646TypeArgToHint,
    TupleHints,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.error.utilerrraise import reraise_exception_placeholder
from beartype._util.hint.pep.proposal.pep484612646 import (
    die_unless_hint_pep484646_typearg_unpacked)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_args,
    get_hint_pep_origin,
    get_hint_pep_typeargs,
)
from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign_or_none
from beartype._util.kind.map.utilmapfrozen import FrozenDict

# ....................{ REDUCERS                           }....................
#FIXME: Unit test that this reducer reduces PEP 646-compliant unpacked type
#variable tuples, please. *sigh*
#
#Begin by testing these new edge cases:
#    _make_hint_pep484646_typeargs_to_hints(
#        hint=...,  # <-- who cares
#        hints_typearg=(S, T, U, *Ts,),
#        hints_child=(int,),
#    ) -> Pep484646TypeArgToHint:
#
#More type parameters than child hints were passed, but that's a valid edge
#case. Callers expect this factory to return "{S: int}". All remaining type
#parameters should remain unassigned, including "*Ts". Why? Because the
#"*Ts" is preceded by one or more unassigned type variables. Since those
#type variables are themselves unassigned, by orthogonality all type
#parameters following those unassigned type variables (notably, the "*Ts")
#must themselves also be unassigned.
#
#Now consider another call that superficially appears similar yet is
#ultimately quite different:
#    _make_hint_pep484646_typeargs_to_hints(
#        hint=...,  # <-- who cares
#        hints_typearg=(S, *Ts,),
#        hints_child=(int,),
#    ) -> Pep484646TypeArgToHint:
#
#Callers expect this factory to return "{S: int, *Ts: ()}". All type
#parameters are assigned, including "*Ts". Why? Because unpacked type
#variables consume zero or more child hints. Since the type parameter "S"
#preceding this "*Ts" was assigned, this "*Ts" must necessarily also be
#assigned the fallback tuple "()". Fascinating, huh?
#FIXME: Document how PEP 646-compliant unpacked type variable tuples intersect
#with the "Caveats" in the docstring below, please. *megasigh*
def reduce_hint_pep484646_subbed_typeargs_to_hints(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    hint_parent_sane: Optional[HintSane] = None,
    exception_prefix: str = '',
) -> HintOrSane:
    '''
    Reduce the passed **subscripted hint** (i.e., derivative hint produced by
    subscripting an unsubscripted hint originally parametrized by one or more
    **type parameters** (i.e., :pep:`484`-compliant type variables or
    :pep:`646`-compliant type variable tuples) with one or more child hints) to
    that unsubscripted hint and corresponding **type parameter lookup table**
    (i.e., immutable dictionary mapping from those same type parameters to those
    same child hints).

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Caveats
    -------
    This reducer does *not* validate these type parameters to actually be type
    parameters. Instead, this function defers that validation to the caller.
    Why? Efficiency, mostly. Avoiding the need to explicitly validate these type
    parameters reduces the underlying mapping operation to a fast one-liner.

    Let:

    * ``hints_typearg`` be the tuple of the zero or more type parameters
      parametrizing the unsubscripted hint underlying the passed subscripted
      hint.
    * ``hints_child`` be the tuple of the zero or more child hints subscripting
      the passed subscripted hint.

    Then this reducer validates the sizes of these tuple to be constrained as:

    .. code-block:: python

       len(hints_typearg) >= len(hints_child) > 0

    Equally, the passed hint *must* be subscripted by at least one child hint.
    For each such child hint, the unsubscripted hint originating this
    subscripted hint *must* be parametrized by a corresponding type parameter.
    The converse is *not* the case, as:

    * For the first type parameter, there also *must* exist a corresponding
      child hint to map to that type parameter.
    * For *all* type parameters following the first, there need *not* exist a
      corresponding child hint to map to that type parameter. Type parameters
      with *no* corresponding child hints are simply silently ignored (i.e.,
      preserved as type parameters rather than mapped to other hints).

    Equivalently:

    * Both of these tuples *must* be **non-empty** (i.e., contain one or more
      items).
    * This tuple of type parameters *must* contain at least as many items as
      this tuple of child hints. Therefore:

      * This tuple of type parameters *may* contain exactly as many items as
        this tuple of child hints.
      * This tuple of type parameters *may* contain strictly more items than
        this tuple of child hints.
      * This tuple of type parameters must *not* contain fewer items than this
        tuple of child hints.

    Parameters
    ----------
    hint : Hint
        Subscripted hint to be inspected.
    hint_parent_sane : Optional[HintSane]
        Either:

        * If the passed hint is a **root** (i.e., top-most parent hint of a tree
          of child hints), :data:`None`.
        * Else, the passed hint is a **child** of some parent hint. In this
          case, the **sanified parent type hint metadata** (i.e., immutable and
          thus hashable object encapsulating *all* metadata previously returned
          by :mod:`beartype._check.convert.convmain` sanifiers after
          sanitizing the possibly PEP-noncompliant parent hint of this child
          hint into a fully PEP-compliant parent hint).

        Defaults to :data:`None`.
    exception_prefix : str, optional
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    HintOrSane
        Either:

        * If the unsubscripted hint (e.g., :class:`typing.Generic`) originating
          this subscripted hint (e.g., ``typing.Generic[S, T]``) is
          unparametrized by type parameters, that unsubscripted hint as is.
        * Else, that unsubscripted hint is parametrized by one or more type
          parameters. In this case, the **sanified type hint metadata** (i.e.,
          :class:`.HintSane` object) describing this reduction.

    Raises
    ------
    exception_cls
        If this type hint is unsubscripted.
    BeartypeDecorHintPep484TypeVarViolation
        If one of these type hints violates the bounds or constraints of one of
        these type parameters.
    '''

    # ....................{ LOCALS                         }....................
    # Unsubscripted type alias originating this subscripted hint.
    hint_unsubbed = get_hint_pep_origin(
        hint=hint,
        exception_cls=BeartypeDecorHintPep484612646Exception,
        exception_prefix=exception_prefix,
    )

    # Tuple of all type parameters parametrizing this unsubscripted hint.
    #
    # Note that PEP 695-compliant "type" alias syntax superficially appears to
    # erroneously permit type aliases to be parametrized by non-type parameters.
    # In truth, "type" syntax simply permits type aliases to be parametrized by
    # type parameters that ambiguously share the same names as builtin types --
    # which then silently shadow those types for the duration of those aliases:
    #     >>> type muh_alias[int] = float | complex  # <-- *gulp*
    #     >>> muh_alias.__parameters__
    #     (int,)  # <-- doesn't look good so far
    #     >>> muh_alias.__parameters__[0] is int
    #     False  # <-- something good finally happened
    hints_typearg = get_hint_pep_typeargs(hint_unsubbed)

    # Tuple of all child hints subscripting this subscripted hint.
    hints_child = get_hint_pep_args(hint)
    # print(f'hints_child: {repr(hints_child)}')

    # ....................{ REDUCE                         }....................
    # Decide the type parameter lookup table for this hint. Specifically, reduce
    # this subscripted hint to:
    # * The semantically useful unsubscripted hint originating this semantically
    #   useless subscripted hint.
    # * The type parameter lookup table mapping all type parameters parametrizing
    #   this unsubscripted hint to all non-type parameter hints subscripting
    #   this subscripted hint.

    # ....................{ REDUCE ~ noop                  }....................
    # If either...
    if (
        # This unsubscripted hint is parametrized by no type parameters *OR*...
        #
        # In this case, *NO* type parameter lookup table can be produced by this
        # reduction. Note this is an uncommon edge case. Examples include:
        # * Parametrizations of the PEP 484-compliant "typing.Generic"
        #   superclass (e.g., "typing.Generic[S, T]"). In this case, the
        #   original unsubscripted "typing.Generic" superclass remains
        #   unparametrized despite that superclass later being parametrized.
        not hints_typearg or
        # This unsubscripted hint is parametrized by the exact same type
        # parameters as this subscripted hint is subscripted by, in which case
        # the resulting type parameter lookup table would uselessly be the
        # identity mapping from each of these type parameters to itself. While
        # an identity type parameter lookup table could trivially be produced,
        # doing so would convey *NO* meaningful semantics and thus be pointless.
        hints_child == hints_typearg
    # Then reduce this subscripted hint to simply this unsubscripted hint, as
    # type parameter lookup tables are then irrelevant.
    ):
        return hint_unsubbed
    # Else, this unsubscripted hint is parametrized by one or more type
    # parameters. In this case, produce a type parameter lookup table mapping
    # these type parameters to child hints subscripting this subscripted hint.

    # ....................{ REDUCE ~ map                   }....................
    # Attempt to...
    try:
        # Type parameter lookup table mapping from each of these type parameters
        # to each of these corresponding child hints.
        #
        # Note that we pass parameters positionally due to memoization.
        typearg_to_hint = _make_hint_pep484646_typeargs_to_hints(
            hint, hints_typearg, hints_child)
    # print(f'Mapped hint {hint} to type parameter lookup table {typearg_to_hint}!')
    # If doing so raises *ANY* exception, reraise this exception with each
    # placeholder substring (i.e., "EXCEPTION_PLACEHOLDER" instance) replaced by
    # an explanatory prefix.
    except Exception as exception:
        reraise_exception_placeholder(
            exception=exception, target_str=exception_prefix)

    # ....................{ REDUCE ~ composite             }....................
    # Sanified metadata to be returned.
    hint_sane: HintSane = None  # type: ignore[assignment]

    # If this hint has *NO* parent, this is a root hint. In this case...
    if hint_parent_sane is None:
        # Metadata encapsulating this hint and type parameter lookup table.
        hint_sane = HintSane(
            hint=hint_unsubbed, typearg_to_hint=typearg_to_hint)
    # Else, this hint has a parent. In this case...
    else:
        # If the parent hint is also associated with a type parameter lookup
        # table...
        if hint_parent_sane.typearg_to_hint:
            # Full type parameter lookup table merging the table associated this
            # parent hint with the table just decided above for this child hint,
            # efficiently defined as...
            typearg_to_hint = (
                # The type parameter lookup table describing all transitive
                # parent hints of this hint with...
                hint_parent_sane.typearg_to_hint |  # type: ignore[operator]
                # The type parameter lookup table describing this hint.
                #
                # Note that this table is intentionally the second rather than
                # first operand of this "|" operation, efficiently ensuring that
                # type parameters mapped by this hint take precedence over type
                # parameters mapped by transitive parent hints of this hint.
                typearg_to_hint
            )
        # Else, the parent hint is associated with *NO* such table.

        # Metadata encapsulating this hint and type parameter lookup table,
        # while "cascading" any other metadata associated with this parent hint
        # (e.g., recursable hint IDs) down onto this child hint as well.
        hint_sane = hint_parent_sane.permute_sane(
            hint=hint_unsubbed, typearg_to_hint=typearg_to_hint)

    # ....................{ RETURN                         }....................
    # print(f'Reduced subscripted hint {repr(hint)} to unsubscripted hint metadata {repr(hint_sane)}.')

    # Return this metadata.
    return hint_sane

# ....................{ PRIVATE ~ factories                }....................
#FIXME: Unit test that this reducer reduces PEP 646-compliant unpacked type
#variable tuples, please. *sigh*
@callable_cached
def _make_hint_pep484646_typeargs_to_hints(
    hint: Hint,
    hints_typearg: TuplePep484646TypeArgs,
    hints_child: TupleHints,
) -> Pep484646TypeArgToHint:
    '''
    Type parameter lookup table mapping from the passed :pep:`484`- or
    :pep:`646`-compliant **type parameters** (i.e., :pep:`484`-compliant type
    variables or :pep:`646`-compliant type variable tuples) to the associated
    passed type hints as key-value pairs of this table.

    This getter is memoized for efficiency. Notably, this getter creates and
    returns a dictionary mapping each type parameter in the passed tuple of type
    parameters to the associated type hint in the passed tuple of type hints
    with the same 0-based tuple index as that type parameter.

    Parameters
    ----------
    hint: Hint
        Parent hint presumably both subscripted by these child hints. This
        parent hint is currently only used to generate human-readable exception
        messages in the event of fatal errors.
    hints_typearg : TuplePep484646TypeArgs
        Tuple of one or more child type parameters originally subscripting the
        origin underlying this parent hint.
    hints_child : TupleHints
        Tuple of one or more child type hints subscripting this parent hint,
        which those type parameters map to.

    Returns
    -------
    Pep484646TypeArgToHint
        Type parameter lookup table mapping these type parameters to these child
        hints.

    Raises
    ------
    BeartypeDecorHintPep484646TypeArgException
        If either:

        * This tuple of type parameters is empty.
        * This tuple of type hints is empty.
        * This tuple of type hints contains more items than this tuple of type
          parameters.
    BeartypeDecorHintPep484TypeVarViolation
        If one of these type hints violates the bounds or constraints of one of
        these type parameters.
    '''
    assert isinstance(hints_typearg, tuple), (
        f'{repr(hints_typearg)} not tuple.')
    assert isinstance(hints_child, tuple), (
        f'{repr(hints_child)} not tuple.')

    # ....................{ PREAMBLE                       }....................
    # Number of passed type parameters and child hints respectively.
    hints_typearg_len = len(hints_typearg)
    hints_child_len = len(hints_child)

    # If *NO* type parameters were passed, raise an exception.
    if not hints_typearg_len:
        raise BeartypeDecorHintPep484612646Exception(
            f'{EXCEPTION_PLACEHOLDER}type hint {repr(hint)} '
            f'parametrized by no type parameters (i.e., '
            f'PEP 484 type variables, '
            f'PEP 612 unpacked parameter specifications, or '
            f'PEP 646 unpacked type variable tuples).'
        )
    # Else, one or more type parameters were passed.

    # ....................{ LOCALS                         }....................
    # Type parameter lookup table to be returned.
    typearg_to_hint: Pep484646TypeArgToHint = {}

    # 0-based index of the current type parameter *AND* corresponding child hint
    # of the passed tuples visited by the "while" loop below.
    hints_index_curr = 0

    # 0-based index of the last type parameter *AND* corresponding child hint of
    # the passed tuples to be visited by the "while" loop below, intentionally
    # defined as the maximum number of type parameters or child hints. Why?
    # Because two relevant edge cases then arise:
    # * If more type parameters than child hints were passed, this calculation
    #   induces the "while" loop below to silently ignore those trailing type
    #   parameters that lack corresponding trailing child hints -- exactly as
    #   required and documented by the above docstring. This case is valid! \o/
    # * If more child hints than type parameters were passed, two sub-edge cases
    #   now arise:
    #   * If one of these type parameters is a PEP 646-compliant unpacked type
    #     variable tuple, this parent edge case is valid. Although more child
    #     hints than type parameters were passed, a single unpacked type
    #     variable tuple consumes zero or more excess child hints (i.e., child
    #     hints *NOT* already consumed by one or more trailing PEP 484-compliant
    #     type variables).
    #   * If none of these type parameters is a PEP 646-compliant unpacked type
    #     variable tuple, this parent edge case is invalid. Validation below
    #     will subsequently detect this invalid case and raise an exception.
    hints_index_last = max(hints_typearg_len, hints_child_len) - 1

    # True only if one or more of the passed type parameters visited by the
    # "while" loop below are PEP 646-compliant unpacked type variable
    # parameters.
    is_hint_typearg_pep646 = False

    # ....................{ PHASE 1 ~ pep 484 : typevar    }....................
    # In this first phase, we map all *LEADING* PEP 484-compliant type variables
    # parametrizing the beginning of this parent subscripted hint until
    # discovering the first PEP 646-compliant type variable tuple (if any)
    # parametrizing the middle of this parent subscripted hint. Notably:
    # * Type variables only map to and thus "consume" a single child hint.
    #   Mapping leading type variables is trivial.
    # * Type variable tuples map to and thus "consume" zero or more child hints.
    #   Mapping both type variable tuples *AND* the trailing type variables that
    #   follow them is comparatively non-trivial. Special care is warranted.

    # While the 0-based index of the current leading type variable does *NOT*
    # exceed that of the last child hint to be visited by this loop, one or
    # more leading type variables remain unvisited. In this case...
    while hints_index_curr <= hints_index_last:
        # If the 0-based index of this leading type variable exceeds that of the
        # last type variable, more child hints than type parameters were passed.
        # Why? Because, if fewer or the same number of child hints as type
        # parameters were passed, then this index would *NEVER* exceed that of
        # the last type variable. But this index exceeded that of the last type
        # variable! The converse must thus be true. Raise an exception.
        #
        # Note that it is conditionally valid for the caller to pass more child
        # hints than type parameters if one of the previously visited type
        # parameters is a PEP 646-compliant unpacked type variable tuple, which
        # would have then consumed all excess child hints. However, one of these
        # type parameters is *NOT* an unpacked type variable tuple. Why? Because
        # if one of these type parameters was such a tuple, then this "while"
        # loop would have already been prematurely terminated by the "break"
        # statement below. Clearly, though, this "while" loop is still
        # iterating! Ergo, the converse must yet again be true.
        if hints_index_curr >= hints_typearg_len:
            raise BeartypeDecorHintPep484612646Exception(
                f'{EXCEPTION_PLACEHOLDER}type hint {repr(hint)} '
                f'number of subscripted child hints {hints_child_len} exceeds '
                f'number of parametrized type parameters {hints_typearg_len} '
                f'(i.e., {hints_child_len} > {hints_typearg_len}).'
            )
        # Else, the 0-based index of this type variable does *NOT* exceed that
        # of the last child hint.

        # Current leading type parameter.
        hint_typearg = hints_typearg[hints_index_curr]

        # Sign uniquely identifying this type parameter.
        hint_typearg_sign = get_hint_pep_sign_or_none(hint_typearg)  # pyright: ignore

        # If this type parameter is a PEP 646-compliant unpacked type variable
        # tuple...
        if hint_typearg_sign is HintSignPep646UnpackedTypeVarTuple:
            # Note that this kind of type parameter has now been discovered.
            is_hint_typearg_pep646 = True

            # Immediately halt all further visitation of type parameters and
            # child hints by this iteration. Unpacked type variable tuples
            # greedily consume all remaining child hints and thus warrant
            # special handling below.
            break
        # Else, this type parameter is *NOT* an unpacked type variable tuple.
        #
        # If the 0-based index of this trailing child hint exceeds that of the
        # last child hint, more type parameters than child hints were passed by
        # similar logic as above. In this case...
        #
        # Note that this condition is intentionally tested here *AFTER* ensuring
        # that this parent hint is parametrized by *NO* unpacked type variable
        # tuple. Why? Because it is conditionally valid for the caller to pass
        # exactly *ONE* more type parameter than child hints if one of those
        # type parameters is an unpacked type variable tuple, which would have
        # then consumed *ZERO* child hints and thus effectively *NOT* have been
        # passed at all. Testing this condition *AFTER* detecting an unpacked
        # type variable tuple enables that type parameter to be correctly mapped
        # to the empty tuple below.
        elif hints_index_curr >= hints_child_len:
            # If *NO* child hints were passed, raise an exception.
            #
            # Note that this condition is intentionally tested here *AFTER*
            # ensuring that this parent hint is parametrized by *NO* unpacked
            # type variable tuple. Why? Because it is conditionally valid for
            # the caller to pass exactly *ZERO* child hints and *ONE* unpacked
            # type variable tuple, which would have then consumed *ZERO* child
            # hints and thus effectively *NOT* have been passed at all.
            if not hints_child_len:
                raise BeartypeDecorHintPep484612646Exception(
                    f'{EXCEPTION_PLACEHOLDER}type hint {repr(hint)} '
                    f'subscripted by no child type hints but '
                    f'parametrized by PEP 484 type variables '
                    f'{repr(hints_typearg)} necessarily matching '
                    f'at least one child hint.'
                )
            # Else, one or more child hints were passed.

            # Immediately halt all further visitation of type parameters and
            # child hints by this iteration. All remaining type variables will
            # be silently ignored and thus preserved as is *WITHOUT* being
            # mapped -- a valid edge case.
            break
        # Else, the 0-based index of this child hint does *NOT* exceed that
        # of the last child hint.

        # Current leading child hint.
        hint_child = hints_child[hints_index_curr]
        # print(f'Mapping typearg {typearg} -> hint {hint}...')
        # print(f'is_hint_nonpep_type({hint})? {is_hint_nonpep_type(hint, False)}')

        # Raise an exception if either:
        # * This type parameter is a PEP 484-compliant type variable *AND*
        #   this child hint violates this type variable's bounded constraints.
        # * This type parameter is *NOT* a PEP 484-compliant type variable.
        _die_if_hint_pep484_typevar_bound_unbearable(
            hint_child=hint_child,
            hint_typearg=hint_typearg,
            hint_typearg_sign=hint_typearg_sign,
        )
        # Else, this type parameter is a PEP 484-compliant type variable *AND*
        # this child hint satisfies this type variable's bounded constraints.

        # Map this type variable to this hint with an optimally efficient
        # one-liner, silently overwriting any prior such mapping of this type
        # variable by either this call or a prior call of this function.
        typearg_to_hint[hint_typearg] = hint_child

        # Iterate the 0-based index of the current type parameter *AND*
        # corresponding child hint to be visited by the next loop iteration.
        hints_index_curr += 1

    # If a PEP 646-compliant unpacked type variable tuple was visited by the
    # "while" loop above...
    if is_hint_typearg_pep646:
        # ....................{ PHASE 2 ~ pep 484 : typevar}....................
        # In this next phase, we map all *TRAILING* PEP 484-compliant type
        # variables parametrizing the ending of this parent subscripted hint.
        # These variables follow the first (and ideally only) PEP 646-compliant
        # type variable tuple parametrizing the middle of this parent
        # subscripted hint.
        #
        # The "while" loop above iterates forward over type variables starting
        # at the first type variable, as is customary for most iteration. In
        # contrast, the "while" loop below iterates backward over type variables
        # starting at the last type variable. Why? Because type variable tuples
        # greedily consume all remaining child hints that have yet to be
        # consumed by a trailing type variable. To decide which child hints
        # remain to be consumed by a type variable tuple requires that we first
        # consume as many trailing child hints as possible by as many trailing
        # type variables exist. Whatever child hints remain are then apportioned
        # to the type variable tuple.

        # 0-based index of the current trailing type parameter visited by the
        # "while" loop below, initialized to that of the last type parameter.
        hints_pep646_typearg_index_curr = hints_typearg_len - 1

        # 0-based index of the current trailing child hint visited by the
        # "while" loop below, initialized to that of the last child hint.
        hints_pep646_child_index_curr = hints_child_len - 1

        # 0-based index of this unpacked type variable tuple.
        hints_pep646_typevartuple_index = hints_index_curr

        # This unpacked type variable tuple.
        hint_pep646_typevartuple = hints_typearg[
            hints_pep646_typevartuple_index]

        # 0-based index of the first trailing type variable *AND* corresponding
        # child hint to be visited by the "while" loop below. Both this type
        # variable and child hint follow this unpacked type variable tuple.
        hints_pep646_index_first = hints_pep646_typevartuple_index + 1

        # While the 0-based index of the current trailing type variable still
        # follows that of the unpacked type variable tuple to *NOT* be visited
        # by this loop, one or more trailing type variables remain unvisited. In
        # this case...
        while hints_pep646_typearg_index_curr >= hints_pep646_index_first:
            # Current trailing type parameter.
            hint_typearg = hints_typearg[hints_pep646_typearg_index_curr]

            # Sign uniquely identifying this type parameter.
            hint_typearg_sign = get_hint_pep_sign_or_none(hint_typearg)  # pyright: ignore

            # If this type parameter is a second PEP 646-compliant unpacked type
            # variable tuple, raise an exception. PEP 646 mandates that generics
            # be parametrized by at most one unpacked type variable tuple.
            if hint_typearg_sign is HintSignPep646UnpackedTypeVarTuple:
                raise BeartypeDecorHintPep484612646Exception(
                    f'{EXCEPTION_PLACEHOLDER}type hint {repr(hint)} '
                    f'parametrized by PEP 646-noncompliant type parameters '
                    f'{repr(hints_typearg)} containing two or more PEP 646 '
                    f'unpacked type variable tuples, including:\n'
                    f'* {repr(hint_pep646_typevartuple)} at index '
                    f'{hints_pep646_typevartuple_index}.\n'
                    f'* {repr(hint_typearg)} at index '
                    f'{hints_pep646_typearg_index_curr}.\n'
                )
            # Else, this type parameter is *NOT* a second PEP 646-compliant
            # unpacked type variable tuple.
            #
            # If the 0-based index of this trailing child hint precedes that of
            # the first trailing child hint, more type parameters than child
            # hints were passed by similar logic as above. In this case,
            # immediately halt all further visitation of type parameters and
            # child hints by this iteration. All remaining type variables will
            # be silently ignored and thus preserved as is *WITHOUT* being
            # mapped -- a valid edge case.
            #
            # Note that, unlike above, it is valid for *NO* child hints to be
            # passed. Why? Because this parent hint is parametrized by an
            # unpacked type variable tuple, which will then consume *ZERO* child
            # hints below.
            elif hints_pep646_child_index_curr >= hints_pep646_index_first:
                break
            # Else, the 0-based index of this trailing child hint exceeds or is
            # equal to that of the first trailing child hint.

            # Current trailing child hint.
            hint_child = hints_child[hints_pep646_child_index_curr]

            # Raise an exception if either:
            # * This type parameter is a PEP 484-compliant type variable *AND*
            #   this child hint violates this type variable's bounds.
            # * This type parameter is *NOT* a PEP 484-compliant type variable.
            _die_if_hint_pep484_typevar_bound_unbearable(
                hint_child=hint_child,
                hint_typearg=hint_typearg,
                hint_typearg_sign=hint_typearg_sign,
            )
            # Else, this type parameter is a PEP 484-compliant type variable
            # *AND* this child hint satisfies this type variable's bounds.

            # Map this type variable to this hint with an optimally efficient
            # one-liner, overwriting any prior such mapping of this type
            # variable by either this call or a prior call of this function.
            typearg_to_hint[hint_typearg] = hint_child

            # Iterate the 0-based indices of the current type parameter *AND*
            # corresponding child hint to be visited by the next loop iteration.
            hints_pep646_typearg_index_curr -= 1
            hints_pep646_child_index_curr -= 1

        # ....................{ PHASE 3 ~ pep 646 : tuple  }....................
        # In this next phase, we map the sole PEP 646-compliant unpacked type
        # variable tuple parametrizing the middle of this parent subscripted
        # hint. This unpacked type variable tuple:
        # * Follows the leading PEP 484-compliant type variables mapped by the
        #   first phase above.
        # * Precedes the trailing PEP 484-compliant type variables mapped by the
        #   second phase above.

        #FIXME: Implement us up yo! "But how, @leycec!?", you may be cogitating.
        #Simple. So, not simple. We map this unpacked type variable to a new
        #dynamically fabricated type hint
        #"typing.Unpack[tuple[{*hints_child_excess}]]", where
        #"{*hints_child_excess}" is the slice of "hints_child" yielding all
        #remaining excess child hints to be greedily consumed by this type
        #variable tuple.
    # Else, a PEP 646-compliant unpacked type variable tuple was *NOT* visited
    # by the "while" loop above. In this case, that loop has already
    # successfully visited all PEP 484-compliant type variables and thus all
    # type parameters parametrizing this parent subscripted hint. We are done!

    # ....................{ RETURN                         }....................
    # Return this table, coerced into an immutable frozen dictionary.
    return FrozenDict(typearg_to_hint)

# ....................{ PRIVATE ~ raisers                  }....................
def _die_if_hint_pep484_typevar_bound_unbearable(
    hint_child: Hint,
    hint_typearg: Pep484646TypeArg,
    hint_typearg_sign: Optional[HintSign],
) -> None:
    '''
    Raise an exception if either:

    * The passed type parameter is a :pep:`484`-compliant type variable *and*
      the passed child hint violates this type variable's bounds and/or
      constraints.
    * The passed type parameter is *not* a :pep:`484`-compliant type variable.

    Parameters
    ----------
    hint_child : Hint
        Child hint to be inspected.
    hint_typearg : Pep484646TypeArg
        Type parameter to be inspected.
    hint_typearg_sign : Optional[HintSign]
        Sign uniquely identifying this type parameter.

    Raises
    ------
    BeartypeDecorHintPep484612646Exception
        If this type parameter is *not* a :pep:`484`-compliant type variable.
    BeartypeDecorHintPep484TypeVarViolation
        If this type parameter is a :pep:`484`-compliant type variable *and*
        this child hint violates this type variable's bounds and/or constraints.
    '''

    # If this type parameter is a PEP 484-compliant type variable...
    if hint_typearg_sign is HintSignTypeVar:
        # If this child hint violates this type variable's bounds and/or
        # constraints, raise an exception.
        die_if_hint_pep484_typevar_bound_unbearable(
            hint=hint_child,
            typevar=hint_typearg,  # type: ignore[arg-type]
            exception_prefix=EXCEPTION_PLACEHOLDER,
        )
        # Else, this child hint satisfies this type variable's bounds and/or
        # constraints.
    # Else, this type parameter is *NOT* a PEP 484-compliant type variable.
    # Ergo, this type parameter is *NOT* an unpacked type parameter! *ROAR*.
    #
    # Note that this should *NEVER* occur. Python itself syntactically
    # guarantees *ALL* child hints parametrizing a PEP-compliant subscripted
    # hint to be unpacked type parameters. Nonetheless, the caller is under
    # no such constraints. To guard against dev bitrot, we validate this.
    else:
        die_unless_hint_pep484646_typearg_unpacked(
            hint=hint_typearg, exception_prefix=EXCEPTION_PLACEHOLDER)  # pyright: ignore
