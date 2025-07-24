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
from beartype._data.hint.sign.datahintsigns import (
    HintSignTypeVar,
    HintSignPep646UnpackedTypeVarTuple,
)
from beartype._data.typing.datatyping import (
    TuplePep484646TypeArgs,
)
from beartype._data.typing.datatypingport import (
    Hint,
    Pep484646TypeArgToHint,
    TupleHints,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.error.utilerrraise import reraise_exception_placeholder
from beartype._util.hint.pep.proposal.pep484.pep484typevar import (
    is_hint_pep484_typevar)
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
    #
    # If *NO* child hints were passed, raise an exception.
    elif not hints_child_len:
        raise BeartypeDecorHintPep484612646Exception(
            f'{EXCEPTION_PLACEHOLDER}type hint {repr(hint)} '
            f'subscripted by no child type hints.'
        )
    # Else, one or more child hints were passed.
    #
    # If more type hints than type parameters were passed, raise an exception.
    elif hints_child_len > hints_typearg_len:
        raise BeartypeDecorHintPep484612646Exception(
            f'{EXCEPTION_PLACEHOLDER}type hint {repr(hint)} '
            f'number of subscripted child hints {len(hints_child)} exceeds '
            f'number of parametrized type parameters {len(hints_typearg)} '
            f'(i.e., {len(hints_child)} > {len(hints_typearg)}).'
        )
    # Else, either the same number of type hints and type parameters were passed
    # *OR* more type parameters than type hints were passed.

    # ....................{ LOCALS                         }....................
    # Type parameter lookup table to be returned.
    typearg_to_hint: Pep484646TypeArgToHint = {}

    # 0-based index of the current type parameter *AND* corresponding child hint
    # of the passed tuples visited by the "while" loop below.
    hints_child_index_curr = 0

    # 0-based index of the last type parameter *AND* corresponding child hint of
    # the passed tuples to be visited by the "while" loop below, defined as the
    # minimum of the lengths of these tuples minus one. Two edge cases then
    # arise:
    # * If more type parameters than child hints were passed, this calculation
    #   induces the "while" loop below to silently ignore those trailing type
    #   parameters that lack corresponding trailing child hints -- exactly as
    #   required and documented by the above docstring. This case is valid! \o/
    # * If more child hints than type parameters were passed, validation above
    #   already detected this invalid edge case and raised an exception.
    hints_child_index_last = min(hints_typearg_len, hints_child_len) - 1

    # True only if one or more of the passed type parameters visited by the
    # "while" loop below are PEP 646-compliant unpacked type variable
    # parameters.
    is_hint_child_typearg_pep646 = False

    # ....................{ PHASE 1 ~ pep 484 : typevar    }....................
    # In this first phase, we map all leading PEP 484-compliant type variables
    # parametrizing the beginning of this parent subscripted hint until
    # discovering the first PEP 646-compliant type variable tuple (if any)
    # parametrizing the middle of this parent subscripted hint. Notably:
    # * Type variables only map to and thus "consume" a single child hint.
    #   Mapping leading type variables is trivial.
    # * Type variable tuples map to and thus "consume" zero or more child hints.
    #   Mapping both type variable tuples *AND* the trailing type variables that
    #   follow them is comparatively non-trivial. Special care is warranted.

    # While the 0-based index of the current type parameter does *NOT* exceed
    # that of the last type parameter to be visited by this loop, one or more
    # type parameters remain unvisited. In this case...
    while hints_child_index_curr <= hints_child_index_last:
        # Current type parameter and corresponding child hint.
        hint_child_typearg = hints_typearg[hints_child_index_curr]
        hint_child_hint = hints_child[hints_child_index_curr]
        # print(f'Mapping typearg {typearg} -> hint {hint}...')
        # print(f'is_hint_nonpep_type({hint})? {is_hint_nonpep_type(hint, False)}')

        # If this type parameter is *NOT* an unpacked type parameter, raise an
        # exception.
        #
        # Note that this should *NEVER* occur. Python itself syntactically
        # guarantees *ALL* child hints parametrizing a PEP-compliant subscripted
        # hint to be unpacked type parameters. Nonetheless, the caller is under
        # no such constraints. To guard against dev bitrot, we validate this.
        die_unless_hint_pep484646_typearg_unpacked(
            hint=hint_child_typearg, exception_prefix=EXCEPTION_PLACEHOLDER)  # pyright: ignore
        # Else, this type parameter is an unpacked type parameter.

        # Sign uniquely identifying this type parameter.
        hint_child_typearg_sign = get_hint_pep_sign_or_none(hint_child_typearg)  # pyright: ignore

        # If this type parameter is a PEP 484-compliant type variable...
        if hint_child_typearg_sign is HintSignTypeVar:
            # If this child hint violates this type variable's bounds and/or
            # constraints, raise an exception.
            die_if_hint_pep484_typevar_bound_unbearable(
                hint=hint_child_hint,
                typevar=hint_child_typearg,  # type: ignore[arg-type]
                exception_prefix=EXCEPTION_PLACEHOLDER,
            )
            # Else, this child hint satisfies this type variable's bounds and/or
            # constraints.
        # Else, this type parameter is *NOT* a PEP 484-compliant type variable.
        # By elimination, this type parameter *MUST* be a PEP 646-compliant
        # unpacked type variable tuple. Unlike type variables, type variable
        # tuples lack associated bounds and/or constraints.
        #
        # If this type parameter is a PEP 646-compliant unpacked type variable
        # tuple...
        elif hint_child_typearg_sign is HintSignPep646UnpackedTypeVarTuple:
            # Note that this kind of type parameter has now been discovered.
            is_hint_child_typearg_pep646 = True

            # Immediately halt all further visitation of type parameters and
            # child hints by this iteration.
            break
        # Else, this type parameter is *NOT* a PEP 646-compliant unpacked type
        # variable tuple. Ergo, this type parameter is *NOT* actually an
        # unpacked type parameter. By the above validation, however, this type
        # parameter is an unpacked type parameter. Raise us up the exception!
        #
        # Note that this should never happen. Mysteriously, this just happened.
        else:  # pragma: no cover
            raise BeartypeDecorHintPep484612646Exception(
                f'{EXCEPTION_PLACEHOLDER}type hint {repr(hint)} parametrized '
                f'by non-type parameter {repr(hint_child_typearg)}.'
            )

        # Map this type parameter to this hint with an optimally efficient
        # one-liner, silently overwriting any prior such mapping of this type
        # parameter by either this call or a prior call of this function.
        typearg_to_hint[hint_child_typearg] = hint_child_hint

        # Iterate the 0-based index of the current type parameter *AND*
        # corresponding child hint to be visited by the next loop iteration.
        hints_child_index_curr += 1

    # ....................{ PHASE 2 ~ pep 484 : typevar    }....................
    # In this first phase, we map all trailing PEP 484-compliant type variables
    # parametrizing the ending of this parent subscripted hint following the
    # first PEP 646-compliant type variable tuple (if any) parametrizing the
    # middle of this parent subscripted hint.
    if is_hint_child_typearg_pep646:
        #FIXME: Implement us up, please! Implement a similar "while" loop as
        #below, except beginning at the end and iterating *BACKWARDS*. We'll
        #thus want obscure initialization logic resembling...
        #
        #Oh - and note the intentional usage of new PEP 646-specific local loop
        #variables. Why? Debugging, maintainability, and readability purposes.
        hints_child_pep646_index_last = hints_child_index_curr + 1
        hints_child_pep646_index_curr = hints_child_index_last

    # ....................{ RETURN                         }....................
    # Return this table, coerced into an immutable frozen dictionary.
    return FrozenDict(typearg_to_hint)
