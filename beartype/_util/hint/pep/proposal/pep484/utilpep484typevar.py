#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **type variable utilities** (i.e.,
callables generically applicable to :pep:`484`-compliant type variables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorHintPep484Exception
# from beartype._util.cache.utilcachecall import callable_cached
from typing import TypeVar

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS                           }....................
#FIXME: Unuseful. Refactor this to return a single composite type hint that we
#can actually feed directly into a reduction algorithm. Notably:
#* The upper bound case is fine.
#* The constraints case *MUST* be refactored to return a "typing.Union" of all
#  constraints. We already perform similar logic when reducing tuple unions to
#  "typing.Union"; so, find and reuse that logic here. Do *NOT* simply return a
#  tuple, as that may *NOT* actually be a valid tuple union, which only support
#  isinstanceable classes. Type variable constraints may be arbitrary
#  PEP-compliant type hints.
#FIXME: Rename to:
#    def get_hint_pep484_typevar_arg_or_none(hint: TypeVar) -> object:
#FIXME: Unit test us up.
#FIXME: Consider memoizing if we end up calling this getter frequently.
#Currently, we only call this getter once during type hint reduction.
# @callable_cached
def get_hint_pep484_typevar_args(hint: TypeVar) -> tuple:
    '''
    Tuple of the zero or more **arguments** (i.e., possibly PEP-noncompliant
    child type hints) parametrizing the passed :pep:`484`-compliant **type
    variable** (i.e., :mod:`typing.TypeVar` instance).

    Specifically, this getter returns a possibly empty tuple containing (in
    order):

    #. Zero or more **type variable constraints** (i.e., positional arguments
       originally passed by the caller to the :meth:`typing.TypeVar.__init__`
       constructor call initializing this type variable). These constraints
       effectively form the union of child type hints to which this type
       variable is covariantly constrained.
    #. One **type variable upper bound** (i.e., ``bound`` keyword argument
       originally passed by the caller to the :meth:`typing.TypeVar.__init__`
       constructor call initializing this type variable). This upper bound is
       yet another child type hint to which this type variable is covariantly
       constrained.

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
    :func:`callable_cached` decorator), as this getter is only infrequently
    called in the codebase.

    Parameters
    ----------
    hint : object
        :pep:`484`-compliant type variable to be inspected.

    Returns
    ----------
    tuple
        Erased superclass originating this :pep:`484`-compliant unerased
        pseudo-superclass.

    Raises
    ----------
    BeartypeDecorHintPep484Exception
        if this object is *not* a :pep:`484`-compliant unerased
        pseudo-superclass.
    '''

    # If this hint is *NOT* a type variable, raise an exception.
    if not isinstance(hint, TypeVar):
        raise BeartypeDecorHintPep484Exception(
            f'{repr(hint)} not PEP 484 type variable.')
    # Else, this hint is a type variable.

    # Return either...
    #
    # Note that constraints and upper bounds are mutually exclusive; the
    # TypeVar.__init__() constructor prevents both from being concurrently
    # passed and thus forces either one, the other, or neither to be passed.
    # This enables us to optimize our detection routine below, as we need *NOT*
    # handle the case in which both are passed.
    return (
        # If this type variable was parametrized by one or more constraints,
        # the tuple of these constraints.
        hint.__constraints__
        if hint.__constraints__ else
        # Else, this type variable was parametrized by *NO* constraints.
        #
        # If this type variable was parametrized by an upper bound, the 1-tuple
        # containing *ONLY* that bound.,
        (hint.__bound__,)
        if hint.__bound__ is not None else
        # Else, this type variable was parametrized by neither constraints
        # *NOR* an upper bound. In this case, return the empty tuple.
        ()
    )
