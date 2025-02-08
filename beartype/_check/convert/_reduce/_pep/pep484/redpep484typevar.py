#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **type variable reducers** (i.e., low-level
callables converting :pep:`484`-compliant type variables to lower-level type
hints more readily consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeDecorHintPep484TypeVarException,
    BeartypeDecorHintPep484TypeVarViolation,
)
from beartype.typing import (
    Any,
    Optional,
    TypeVar,
)
from beartype._check.metadata.metasane import (
    HintOrHintSanifiedData,
    HintSanifiedData,
)
from beartype._data.hint.datahintpep import (
    Hint,
    TupleHints,
    TypeVarToHint,
)
from beartype._data.hint.datahinttyping import (
    TupleTypeVars,
    TypeException,
)
from beartype._util.cls.pep.utilpep3119 import is_object_issubclassable
from beartype._util.hint.nonpep.utilnonpeptest import is_hint_nonpep_type
from beartype._util.hint.pep.proposal.pep484.pep484typevar import (
    get_hint_pep484_typevar_bound_or_none,
    is_hint_pep484_typevar,
)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_args,
    get_hint_pep_origin,
    get_hint_pep_typevars,
)
from beartype._util.kind.map.utilmapfrozen import FrozenDict
# from beartype._util.utilobject import SENTINEL

# ....................{ REDUCERS                           }....................
def reduce_hint_pep484_typevar(
    hint: Hint,
    typevar_to_hint: TypeVarToHint,
    exception_prefix: str,
    **kwargs
) -> Hint:
    '''
    Reduce the passed :pep:`484`-compliant **type variable** (i.e.,
    :class:`typing.TypedDict` instance) to a lower-level type hint currently
    supported by :mod:`beartype`.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : Hint
        Type variable to be reduced.
    typevar_to_hint : TypeVarToHint
        **Type variable lookup table** (i.e., dictionary mapping from type
        variables to the arbitrary type hints those type variables map to).
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    All remaining passed arguments are silently ignored.

    Returns
    -------
    Hint
        Lower-level type hint currently supported by :mod:`beartype`.
    '''
    # print(f'Reducing PEP 484 type variable {repr(hint)} by type variable lookup table {repr(typevar_to_hint)}...')

    # If a parent hint of this type variable maps one or more type variables...
    if typevar_to_hint:
        # If a parent hint of this type variable maps exactly one type
        # variables, prefer a dramatically faster and simpler approach.
        if len(typevar_to_hint) == 1:
            # Hint mapped to by this type variable if one or more parent hints
            # previously mapped this type variable to a hint *OR* this hint as
            # is otherwise (i.e., if this type variable is unmapped).
            #
            # Note that this one-liner looks ridiculous, but actually works.
            # More importantly, this is the fastest way to accomplish this.
            hint = typevar_to_hint.get(hint, hint)  # pyright: ignore
        # Else, a parent hint of this type variable mapped two or more type
        # variables. In this case, fallback to a slower and more complicated
        # approach that avoids worst-case edge cases. This includes recursion in
        # type variable mappings, which arises in non-trivial class hierarchies
        # involving two or more generics subscripted by two or more type
        # variables that circularly cycle between one another: e.g.,
        #     from typing import Generic
        #     class GenericRoot[T](Generic[T]): pass
        #
        #     # This directly maps {T: S}.
        #     class GenericLeaf[S](GenericStem[S]): pass
        #
        #     # This directly maps {S: T}, which then combines with the above
        #     # mapping to indirectly map {S: T, T: S}. Clearly, this indirect
        #     # mapping provokes infinite recursion unless explicitly handled.
        #     GenericLeaf[T]
        else:
            # Shallow copy of this type variable lookup table, coerced from an
            # immutable frozen dictionary into a mutable standard dictionary.
            # This enables type variables reduced by the iteration below to be
            # popped off this copy as a simple (but effective) recursion guard.
            typevar_to_hint_stack = typevar_to_hint.copy()

            # While...
            while (
                # This stack still contains one or more type variables that have
                # yet to be reduced by this iteration *AND*...
                typevar_to_hint_stack and
                # This hint is still a type variable...
                isinstance(hint, TypeVar)
            ):
                # Hint mapped to by this type variable if one or more parent
                # hints previously mapped this type variable to a hint *OR* this
                # hint as is otherwise (i.e., if this type variable is
                # unmapped).
                #
                # Note that this one-liner destructively pops this type variable
                # off this stack to prevent this type variable from being
                # reduced more than once by an otherwise recursive mapping.
                hint_reduced: Hint = typevar_to_hint_stack.pop(hint, hint)  # pyright: ignore

                # If this type variable maps to itself, this mapping is both
                # ignorable *AND* terminates this reduction.
                if hint_reduced is hint:
                    break
                # Else, this type variable does *NOT* map to itself.

                # Map this type variable to this hint.
                hint = hint_reduced
    # Else, this type variable is unmapped.

    # If this hint is still a type variable (e.g., due to either not being
    # mapped by this lookup table *OR* being mapped to another type variable)...
    if isinstance(hint, TypeVar):
        # PEP-compliant hint synthesized from all bounded constraints
        # parametrizing this type variable if any *OR* "None" otherwise (i.e.,
        # if this type variable is both unbounded *AND* unconstrained).
        #
        # Note this call is passed positional parameters due to memoization
        hint = get_hint_pep484_typevar_bound_or_none(hint, exception_prefix)  # pyright: ignore

        # If this type variable is both unbounded *AND* unconstrained, this type
        # variable is currently *NOT* type-checkable and is thus ignorable.
        # Reduce this type variable to the ignorable "typing.Any" singleton.
        if hint is None:
            hint = Any
        # Else, this type variable is either bounded *OR* constrained. In either
        # case, preserve this newly synthesized hint.
        # print(f'Reducing PEP 484 type variable {repr(hint)} to {repr(hint_bound)}...')
        # print(f'Reducing non-beartype PEP 593 type hint {repr(hint)}...')
    # Else, one or more transitive parent hints previously mapped this type
    # variable to another hint.

    # Return this reduced hint.
    return hint


def reduce_hint_pep484_subscripted_typevar_to_hint(
    hint: Hint, exception_prefix: str = '', **kwargs) -> HintOrHintSanifiedData:
    '''
    Reduce the passed :pep:`484`-compliant **subscripted hint** (i.e., object
    produced by subscripting an unsubscripted hint originally parametrized by
    one or more :pep:`484`-compliant type variables by one or more child hints)
    to that unsubscripted hint and corresponding **type variable lookup table**
    (i.e., immutable dictionary mapping from those same type variables to those
    same child hints).

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Caveats
    -------
    This reducer does *not* validate these type variables to actually be type
    variables. Instead, this function defers that validation to the caller. Why?
    Efficiency, mostly. Avoiding the need to explicitly validate these type
    variables reduces the underlying mapping operation to a fast one-liner.

    This reducer validates the sizes of these two tuples to be constrained as:

    .. code-block:: python

       len(typevars) >= len(hints) > 0

    Informally, the passed hint *must* be subscripted by at least one child
    hint. For each such child hint, the unsubscripted hint originating this
    subscripted hint *must* be parametrized by a corresponding type variable.
    The converse is *not* the case, as:

    * For the first type variable, there also *must* exist a corresponding child
      hint to map to that type variable.
    * For *all* type variables following the first, there need *not* exist a
      corresponding child hint to map to that type variable. Type variables with
      *no* corresponding child hints are simply silently ignored (i.e.,
      preserved as type variables rather than mapped to other type hints).

    Equivalently:

    * Both of these tuples *must* be **non-empty** (i.e., contain one or more
      items).
    * This tuple of type variables *must* contain at least as many items as this
      tuple of child hints. Therefore:

      * This tuple of type variables *may* contain exactly as many items as this
        tuple of child hints.
      * This tuple of type variables *may* contain strictly more items than this
        tuple of child hints.
      * This tuple of type variables must *not* contain fewer items than this
        tuple of child hints.

    Parameters
    ----------
    hint : Hint
        Subscripted hint to be inspected.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    -------
    HintOrHintSanifiedData
        Either:

        * If the unsubscripted hint (e.g., :class:`typing.Generic`) originating
          this subscripted hint (e.g., ``typing.Generic[S, T]``) is
          unparametrized by type variables, that unsubscripted hint as is.
        * Else, that unsubscripted hint is parametrized by one or more type
          variables. In this case, the **sanified type hint metadata** (i.e.,
          :class:`.HintSanifiedData` object) describing this reduction.

    Raises
    ------
    exception_cls
        If this type hint is unsubscripted.
    BeartypeDecorHintPep484TypeVarViolation
        If one of these type hints violates the bounds or constraints of one of
        these type variables.
    '''

    # Unsubscripted type alias originating this subscripted hint.
    hint_unsubscripted = get_hint_pep_origin(
        hint=hint,
        exception_cls=BeartypeDecorHintPep484TypeVarException,
        exception_prefix=exception_prefix,
    )

    # Tuple of all type variables parametrizing this unsubscripted hint.
    #
    # Note that PEP 695-compliant "type" syntax superficially appears to
    # erroneously permit type aliases to be parametrized by non-type variables.
    # In truth, "type" syntax simply permits type aliases to be parametrized by
    # type variables that ambiguously share the same names as builtin types --
    # which then silently shadow those types for the duration of those aliases:
    #     >>> type muh_alias[int] = float | complex  # <-- *gulp*
    #     >>> muh_alias.__parameters__
    #     (int,)  # <-- doesn't look good so far
    #     >>> muh_alias.__parameters__[0] is int
    #     False  # <-- something good finally happened
    hint_unsubscripted_typevars = get_hint_pep_typevars(hint_unsubscripted)

    # Tuple of all child hints subscripting this subscripted hint.
    hint_args = get_hint_pep_args(hint)
    # print(f'hint_args: {repr(hint_args)}')

    # If either...
    if (
        # This unsubscripted hint is parametrized by *NO* type variables, *NO*
        # type variable lookup table can be produced by this reduction.
        #
        # Note this this is an uncommon edge case. Examples include:
        # * Parametrizations of the PEP 484-compliant "typing.Generic"
        #   superclass (e.g., "typing.Generic[S, T]"). In this case, the
        #   original unsubscripted "typing.Generic" superclass remains
        #   unparametrized despite that superclass later being parametrized.
        not hint_unsubscripted_typevars or
        # This unsubscripted hint is parametrized by the exact same type
        # variables as this subscripted hint is subscripted by, in which case
        # the resulting type variable lookup table would uselessly be the
        # identity mapping from each of these type variables to itself. While an
        # identity type variable lookup table could trivially be produced, doing
        # so would convey *NO* meaningful semantics and thus be pointless.
        hint_args == hint_unsubscripted_typevars
    # Then reduce this subscripted hint to simply this unsubscripted hint, as
    # type variable lookup tables are then irrelevent.
    ):
        return hint_unsubscripted
    # Else, this unsubscripted hint is parametrized by one or more type
    # variables. In this case, produce a type variable lookup table mapping
    # these type variables to child hints subscripting this subscripted hint.

    # Type variable lookup table mapping from each of these type variables to
    # each of these corresponding child hints.
    typevar_to_hint = _get_hint_pep484_typevars_to_hints(
        hint_parent=hint,
        hints=hint_args,
        typevars=hint_unsubscripted_typevars,
        exception_cls=BeartypeDecorHintPep484TypeVarException,
        exception_prefix=exception_prefix,
    )

    # Metadata encapsulating this hint and type variable lookup table.
    hint_or_sane = HintSanifiedData(
        hint=hint_unsubscripted, typevar_to_hint=typevar_to_hint)
    # print(f'Reduced subscripted hint {repr(hint)} to unsubscripted hint {repr(hint_unsubscripted)} and...')
    # print(f'...type variable lookup table {repr(typevar_to_hint)}.')

    # Return this metadata.
    return hint_or_sane

# ....................{ PRIVATE ~ getters                  }....................
def _get_hint_pep484_typevars_to_hints(
    # Mandatory parameters.
    typevars: TupleTypeVars,
    hints: TupleHints,

    # Optional parameters.
    hint_parent: Optional[Hint] = None,
    exception_cls: TypeException = BeartypeDecorHintPep484TypeVarException,
    exception_prefix: str = '',
) -> TypeVarToHint:
    '''
    Type variable lookup table mapping from the passed :pep:`484`-compliant
    **type variables** (i.e., :class:`.TypeVar` objects) to the associated
    passed type hints as key-value pairs of this table.

    Specifically, this function efficiently adds one or more key-value pairs to
    this dictionary mapping each type variable in the passed tuple of type
    variables to the associated type hint in the passed tuple of type hints with
    the same 0-based tuple index as that type variable.

    Parameters
    ----------
    typevars : TupleTypeVars
        Tuple of one or more type variables.
    hints : TupleHints
        Tuple of one or more type hints those type variables map to.
    hint_parent: Optional[Hint]
        Parent type hint presumably both subscripted by these ``hints`` if any
        *or* :data:`None` otherwise. This hint is *only* embedded in the
        exception message in the event of a fatal error and thus technically
        optional, albeit strongly advised. Defaults to :data:`None`.
    exception_cls : TypeException, optional
        Type of exception to be raised in the event of fatal error. Defaults to
        :exc:`.BeartypeDecorHintPep484TypeVarException`.
    exception_prefix: str, optional
        Human-readable substring prefixing the exception message in the event of
        a fatal error. Defaults to the empty string.

    Returns
    -------
    TypeVarToHint
        Type variable lookup table mapping these type variables to hints.

    Raises
    ------
    exception_cls
        If either:

        * This tuple of type variables is empty.
        * This tuple of type hints is empty.
        * This tuple of type hints contains more items than this tuple of type
          variables.
    BeartypeDecorHintPep484TypeVarViolation
        If one of these type hints violates the bounds or constraints of one of
        these type variables.
    '''
    assert isinstance(typevars, tuple), f'{repr(typevars)} not tuple.'
    assert isinstance(hints, tuple), f'{repr(hints)} not tuple.'
    assert isinstance(exception_prefix, str), (
        f'{repr(exception_prefix)} not string.')

    # ....................{ PREAMBLE                       }....................
    # If *NO* type variables were passed, raise an exception.
    if not typevars:
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint_parent)} '
            f'parametrized by no PEP 484 type variables.'
        )
    # Else, one or more type variables were passed.
    #
    # If *NO* type hints were passed, raise an exception.
    elif not hints:
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint_parent)} '
            f'subscripted by no type hints.'
        )
    # Else, one or more type hints were passed.
    #
    # If more type hints than type variables were passed, raise an exception.
    elif len(hints) > len(typevars):
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint_parent)} '
            f'number of subscripted type hints {len(hints)} exceeds '
            f'number of parametrized type variables {len(typevars)} '
            f'(i.e., {len(hints)} > {len(typevars)}).'
        )
    # Else, either the same number of type hints and type variables were passed
    # *OR* more type variables than type hints were passed.

    # ....................{ MAP                            }....................
    # Type variable lookup table to be returned.
    typevar_to_hint: TypeVarToHint = {}

    #FIXME: Optimize into a "while" loop at some point. *sigh*
    # For each passed type variable and corresponding type hint...
    #
    # Note that:
    # * The C-based zip() builtin has been profiled to be the fastest means of
    #   iterating pairs in pure-Python, interestingly.
    # * If more type variables than type hints were passed, zip() silently
    #   ignores type variables with *NO* corresponding type hints -- exactly as
    #   required and documented by the above docstring.
    # print(f'Mapping typevars {typevars} -> hints {hints}...')
    for typevar, hint in zip(typevars, hints):
        # print(f'Mapping typevar {typevar} -> hint {hint}...')
        # print(f'is_hint_nonpep_type({hint})? {is_hint_nonpep_type(hint, False)}')

        # If this is *NOT* actually a type variable, raise an exception.
        #
        # Note that Python itself typically fails to validate this constraint,
        # thus requiring that we do so explicitly. For example:
        # * Ideally, *ALL* child hints parametrizing a PEP 695-compliant
        #   subscripted type alias would actually be type variables. Sadly, the
        #   "type" statement is excessively permissive under at least Python <=
        #   3.13 (and possibly newer Python releases as well): e.g.,
        #       >>> type muh_alias[int] = float | complex
        #       >>> muh_alias.__parameters__
        #       (int,)  # <-- pretty sure that's *NOT* a parameter, Python
        if not is_hint_pep484_typevar(typevar):
            raise exception_cls(
                f'{exception_prefix}type hint {repr(hint_parent)} '
                f'parametrization {repr(typevar)} not '
                f'PEP 484 type variable (i.e., "typing.TypeVar" object).'
            )
        # Else, this is actually a type variable.

        #FIXME: Insufficient. Ideally, we would also validate this hint to be a
        #*SUBHINT* of this type variable. Specifically, if this type variable is
        #bounded by one or more bounded constraints, then we should validate
        #this hint to be a *SUBHINT* of those constraints: e.g.,
        #    class MuhClass(object): pass
        #
        #    # PEP 695 type alias parametrized by a type variable bound to a
        #    # subclass of the "MuhClass" type.
        #    type muh_alias[T: MuhClass] = T | int
        #
        #    # *INVALID.* Ideally, @beartype should reject this, as "int" is
        #    # *NOT* a subhint of "MuhClass".
        #    def muh_func(muh_arg: muh_alias[int]) -> None: pass
        #
        #Doing so is complicated, however, by forward reference proxies. For
        #obvious reasons, forward reference proxies are *NOT* safely resolvable
        #at this early decoration time that this function is typically called
        #at. If this hint either:
        #* Is itself a forward reference proxy, ignore rather than validate this
        #  hint as a subhint of these bounded constraints. Doing so is trivial
        #  by simply calling "is_beartype_forwardref(hint)" here.
        #* Is *NOT* itself a forward reference proxy but is transitively
        #  subscripted by one or more forward reference proxies, ignore rather
        #  than validate this hint as a subhint of these bounded constraints.
        #  Doing so is *EXTREMELY NON-TRIVIAL.* Indeed, there's *NO* reasonable
        #  way to do so directly here. Rather, we'd probably have to embrace an
        #  EAFP approach: that is, just crudely try to:
        #  * Detect whether this hint is a subhint of these bounded constraints.
        #  * If doing so raises an exception indicative of a forward reference
        #    issue, silently ignore that exception.
        #
        #  Of course, we're unclear what exception type that would even be. Does
        #  the beartype.door.is_subhint() tester even explicitly detect forward
        #  reference issues and raise an appropriate exception type? No idea.
        #  Probably *NOT*, honestly. Interestingly, is_subhint() currently even
        #  fails to support standard PEP 484-compliant forward references:
        #      >>> is_subhint('int', int)
        #      beartype.roar.BeartypeDoorNonpepException: Type hint 'int'
        #      currently unsupported by "beartype.door.TypeHint".
        #
        #Due to these (and probably more) issues, we currently *ONLY* validate
        #this hint to be a subhint of these bounded constraints...

        # If this hint is a PEP-noncompliant isinstanceable type (and thus *NOT*
        # an unresolvable forward reference proxy, which by definition is *NOT*
        # isinstanceable)...
        elif is_hint_nonpep_type(hint=hint, is_forwardref_valid=False):
            # PEP-compliant type hint synthesized from all bounded constraints
            # parametrizing this type variable if any *OR* "None" otherwise.
            #
            # Note that this call is intentionally passed positional rather
            # positional keywords due to memoization.
            typevar_bound = get_hint_pep484_typevar_bound_or_none(
                typevar, exception_prefix)
            # print(f'[{typevar}] is_object_issubclassable({typevar_bound})? ...')
            # print(f'{is_object_issubclassable(typevar_bound, False)}')

            # If...
            if (
                # This type variable was bounded or constrained *AND*...
                typevar_bound is not None and
                # These bounded constraints are issubclassable (i.e., an object
                # safely passable as the second parameter to the issubclass()
                # builtin) *AND*...
                #
                # Note that this function is memoized and thus permits *ONLY*
                # positional parameters.
                is_object_issubclassable(
                    typevar_bound,
                    # Ignore unresolvable forward reference proxies (i.e.,
                    # beartype-specific objects referring to user-defined
                    # external types that have yet to be defined).
                    False,
                ) and
                # This PEP-noncompliant isinstanceable type hint is *NOT* a
                # subclass of these bounded constraints...
                not issubclass(hint, typevar_bound)  # type: ignore[arg-type]
            ):
                # Raise a type-checking violation.
                raise BeartypeDecorHintPep484TypeVarViolation(
                    message=(
                        f'{exception_prefix}type hint {repr(hint_parent)} '
                        f'originally parametrized by '
                        f'PEP 484 type variable {repr(typevar)} '
                        f'subsequently subscripted by '
                        f'child type hint {repr(hint)} violating '
                        f"this type variable's bounds or constraints "
                        f'{repr(typevar_bound)}.'
                    ),
                    culprits=(hint,),
                )
            # Else, this type variable was either:
            # * Unbounded and unconstrained.
            # * Bounded or constrained by a hint that is *NOT* issubclassable.
            # * Bounded or constrained by an issubclassable object that is the
            #   superclass of this corresponding hint, which thus satisfies
            #   these bounded constraints.
        # Else, this hint is *NOT* a PEP-noncompliant isinstanceable type.

        # Map this type variable to this hint with an optimally efficient
        # one-liner, silently overwriting any prior such mapping of this type
        # variable by either this call or a prior call of this function.
        typevar_to_hint[typevar] = hint

    # ....................{ RETURN                         }....................
    # Return this table, coerced into an immutable frozen dictionary.
    return FrozenDict(typevar_to_hint)
