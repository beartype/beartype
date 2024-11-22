#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **type variable utilities** (i.e.,
callables generically applicable to :pep:`484`-compliant type variables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep484Exception
from beartype.typing import TypeVar
from beartype._data.hint.datahintpep import (
    TupleHints,
    TypeVarToHint,
)
from beartype._data.hint.datahinttyping import TupleTypeVars
from beartype._util.cache.utilcachecall import callable_cached

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please.
def is_hint_pep484_typevar(hint: object) -> bool:
    '''
    :data:`True` only if the passed object is a :pep:`484`-compliant **type
    variable** (i.e., :class:`typing.TypeVar` instance).
    '''

    # Although this test currently reduces to a trivial one-liner, it's *NOT*
    # inconceivable that this test could become non-trivial under a subsequent
    # CPython version. *shrug*
    return isinstance(hint, TypeVar)

# ....................{ GETTERS                            }....................
@callable_cached
def get_hint_pep484_typevar_bound_or_none(
    hint: TypeVar, exception_prefix: str = '') -> object:
    '''
    PEP-compliant type hint synthesized from all bounded constraints
    parametrizing the passed :pep:`484`-compliant **type variable** (i.e.,
    :class:`typing.TypeVar` instance) if any *or* :data:`None` otherwise (i.e.,
    if this type variable was parametrized by *no* bounded constraints).

    Specifically, if this type variable was parametrized by:

    #. One or more **constraints** (i.e., positional arguments passed by the
       caller to the :meth:`typing.TypeVar.__init__` call initializing this
       type variable), this getter returns a new **PEP-compliant union type
       hint** (i.e., :attr:`typing.Union` subscription) of those constraints.
    #. One **upper bound** (i.e., ``bound`` keyword argument passed by the
       caller to the :meth:`typing.TypeVar.__init__` call initializing this
       type variable), this getter returns that bound as is.
    #. Else, this getter returns the :data:`None` singleton.

    Caveats
    -------
    **This getter treats constraints and upper bounds as semantically
    equivalent,** preventing callers from distinguishing between these two
    technically distinct variants of type variable metadata.

    For runtime type-checking purposes, type variable constraints and bounds
    are sufficiently similar as to be semantically equivalent for all intents
    and purposes. To simplify handling of type variables, this getter
    ambiguously aggregates both into the same tuple.

    For static type-checking purposes, type variable constraints and bounds
    are *still* sufficiently similar as to be semantically equivalent for all
    intents and purposes. Any theoretical distinction between the two is likely
    to be lost on *most* engineers, who tend to treat the two interchangeably.
    To quote :pep:`484`:

        ...type constraints cause the inferred type to be _exactly_ one of the
        constraint types, while an upper bound just requires that the actual
        type is a subtype of the boundary type.

    Inferred types are largely only applicable to static type-checkers, which
    internally assign type variables contextual types inferred from set and
    graph theoretic operations on the network of all objects (nodes) and
    callables (edges) relating those objects. Runtime type-checkers have *no*
    analogous operations, due to runtime space and time constraints.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator). If this type variable was parametrized
    by one or more constraints, the :attr:`typing.Union` type hint factory
    already caches these constraints; else, this getter performs no work. In
    any case, this getter effectively performs to work.

    Parameters
    ----------
    hint : object
        :pep:`484`-compliant type variable to be inspected.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    -------
    object
        Either:

        * If this type variable was parametrized by one or more constraints, a
          new PEP-compliant union type hint aggregating those constraints.
        * If this type variable was parametrized by an upper bound, that bound.
        * Else, :data:`None`.

    Raises
    ------
    BeartypeDecorHintPep484Exception
        if this object is *not* a :pep:`484`-compliant type variable.
    '''

    # If this hint is *NOT* a type variable, raise an exception.
    if not is_hint_pep484_typevar(hint):
        raise BeartypeDecorHintPep484Exception(
            f'{exception_prefix}type hint {repr(hint)} '
            f'not PEP 484 type variable.'
        )
    # Else, this hint is a type variable.

    # If this type variable was parametrized by one or more constraints...
    if hint.__constraints__:
        # Avoid circular import dependencies.
        from beartype._util.hint.pep.proposal.pep484.pep484union import (
            make_hint_pep484_union)

        # Create and return the PEP 484-compliant union of these constraints.
        return make_hint_pep484_union(hint.__constraints__)
    # Else, this type variable was parametrized by *NO* constraints.
    #
    # If this type variable was parametrized by an upper bound, return that
    # bound as is.
    elif hint.__bound__ is not None:
        return hint.__bound__
    # Else, this type variable was parametrized by neither constraints *NOR* an
    # upper bound.

    # Return "None".
    return None

# ....................{ MAPPERS                            }....................
def map_pep484_typevars_to_hints(
    # Mandatory parameters.
    typevar_to_hint: TypeVarToHint,
    typevars: TupleTypeVars,
    hints: TupleHints,

    # Optional parameters.
    exception_message: str = '',
) -> None:
    '''
    Add mappings from the passed :pep:`484`-compliant **type variables** (i.e.,
    :class:`.TypeVar` objects) to the associated passed type hints as new
    key-value pairs of the passed **type variable lookup table** (i.e.,
    immutable dictionary mapping from these type variables to these type hints).

    Specifically, this function efficiently adds one or more key-value pairs to
    this dictionary mapping each type variable in the passed tuple of type
    variables to the associated type hint in the passed tuple of type hints with
    the same 0-based tuple index as that type variable.

    Caveats
    -------
    If a previous call to this function already added one or more of these type
    variables to this dictionary, this function **silently replaces the type
    hints those type variables previously mapped to with the corresponding type
    hints of the passed tuple.** Doing so intentionally mimics the behaviour of
    type variables in *most* real-world use cases.

    This function does *not* validate these type variables to actually be type
    variables. Instead, this function defers that validation to the caller. Why?
    Efficiency, mostly. Avoiding the need to explicitly validate these type
    variables reduces the underlying mapping operation to a fast one-liner.

    This function *does* validate the sizes of these two tuples, which are are
    constrained as follows:

    .. code-block:: python

       len(typevars) >= len(hints) > 0

    Informally, at least one type hint *must* be passed. For each passed type
    hint, there *must* exist a corresponding type variable to map that type hint
    to. The converse is *not* the case, as:

    * For the first passed type variable, there also *must* exist a
      corresponding type hint mapped to that type variable.
    * For *all* type variables following the first, there need *not* exist a
      corresponding type hint mapped to that type variable. Type variables with
      *no* corresponding type hints are simply silently ignored (i.e., preserved
      as type variables rather than mapped to other type hints).

    Equivalently:

    * Both of these tuples *must* be **non-empty** (i.e., contain one or more
      items).
    * This tuple of type variables *must* contain at least as many items as this
      tuple of type hints. Therefore:

      * This tuple of type variables *may* contain exactly as many items as this
        tuple of type hints.
      * This tuple of type variables *may* contain strictly more items than this
        tuple of type hints.
      * This tuple of type variables must *not* contain fewer items than this
        tuple of type hints.

    Parameters
    ----------
    typevar_to_hint : TypeVarToHint
        **Type variable lookup table** (i.e., dictionary mapping from type
        variables to the arbitrary type hints those type variables map to).
    typevars : TupleTypeVars
        Tuple of one or more type variables.
    hints : TupleHints
        Tuple of one or more type hints those type variables map to.
    exception_message: str, optional
        Human-readable substring prefixing the exception message in the event of
        a fatal error. Defaults to the empty string.

    Raises
    ------
    BeartypeDecorHintPep484Exception
        If either:

        * This tuple of type variables is empty.
        * This tuple of type hints is empty.
        * This tuple of type hints contains more items than this tuple of type
          variables.
    '''
    assert isinstance(typevar_to_hint, dict), (
        f'{repr(typevar_to_hint)} not dictionary.')
    assert isinstance(typevars, tuple), f'{repr(typevars)} not tuple.'
    assert isinstance(hints, tuple), f'{repr(hints)} not tuple.'
    assert isinstance(exception_message, str), (
        f'{repr(exception_message)} not string.')

    # If *NO* type variables were passed, raise an exception.
    if not typevars:
        raise BeartypeDecorHintPep484Exception(
            f'{exception_message}parametrized by no PEP 484 type variables.')
    # Else, one or more type variables were passed.
    #
    # If *NO* type hints were passed, raise an exception.
    elif not hints:
        raise BeartypeDecorHintPep484Exception(
            f'{exception_message}subscripted by no type hints.')
    # Else, one or more type hints were passed.
    #
    # If more type hints than type variables were passed, raise an exception.
    elif len(hints) > len(typevars):
        raise BeartypeDecorHintPep484Exception(
            f'{exception_message}'
            f'number of subscripted type hints {len(hints)} exceeds '
            f'number of parametrized type variables {len(typevars)} '
            f'(i.e., {len(hints)} > {len(typevars)}).'
        )
    # Else, either the same number of type hints and type variables were passed
    # *OR* more type variables than type hints were passed.

    # Add a key-value pair to the passed dictionary mapping each of these type
    # variables to the corresponding type hint with an optimally efficient
    # one-liner. Although alternative approaches exist, this one-liner is
    # well-known to be the most efficient means of effecting this.
    #
    # Note that:
    # * The C-based zip() builtin has been profiled to be the fastest means of
    #   iterating pairs in pure-Python, interestingly.
    # * If more type variables than type hints were passed, zip() silently
    #   ignores type variables with *NO* corresponding type hints -- exactly as
    #   required and documented by the above docstring.
    # * If this type variable has already been mapped to some type hint by
    #   either this call or a prior call of this function, this mapping is
    #   silently overwritten by mapping this type variable to a new type hint.
    typevar_to_hint.update(zip(typevars, hints))

# ....................{ REDUCERS                           }....................
#FIXME: Remove this function *AFTER* deeply type-checking type variables.
def reduce_hint_pep484_typevar(
    hint: TypeVar, exception_prefix: str, *args, **kwargs) -> object:
    '''
    Reduce the passed :pep:`484`-compliant **type variable** (i.e.,
    :class:`typing.TypedDict` instance) to a lower-level type hint currently
    supported by :mod:`beartype`.

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Type variable to be reduced.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    All remaining passed arguments are silently ignored.

    Returns
    -------
    object
        Lower-level type hint currently supported by :mod:`beartype`.
    '''

    # PEP-compliant type hint synthesized from all bounded constraints
    # parametrizing this type variable if any *OR* "None" otherwise.
    #
    # Note that this function call is intentionally passed positional rather
    # positional keywords for efficiency with respect to @callable_cached.
    hint_bound = get_hint_pep484_typevar_bound_or_none(hint, exception_prefix)
    # print(f'Reducing PEP 484 type variable {repr(hint)} to {repr(hint_bound)}...')
    # print(f'Reducing non-beartype PEP 593 type hint {repr(hint)}...')

    # Return either...
    return (
        # If this type variable was parametrized by *NO* bounded constraints,
        # this type variable preserved as is;
        hint
        if hint_bound is None else
        # Else, this type variable was parametrized by one or more bounded
        # constraints. In this case, these constraints.
        hint_bound
    )
