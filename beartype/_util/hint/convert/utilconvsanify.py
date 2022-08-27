#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-agnostic type hint sanitizers** (i.e., high-level callables
converting type hints from one format into another, either permanently or
temporarily and either losslessly or in a lossy manner).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Any
from beartype._util.cache.map.utilmapbig import CacheUnboundedStrong
from beartype._util.hint.convert.utilconvcoerce import (
    coerce_func_hint_root,
    coerce_hint_any,
    coerce_hint_root,
)
from beartype._util.hint.convert.utilconvreduce import reduce_hint
from beartype._util.hint.utilhinttest import die_unless_hint
from collections.abc import Callable

# ....................{ PRIVATE ~ mappings                 }....................
_HINT_REPR_TO_HINT = CacheUnboundedStrong()
'''
**Type hint cache** (i.e., thread-safe cache mapping from the machine-readable
representations of all non-self-cached type hints to those hints).**

This cache caches:

* :pep:`585`-compliant type hints, which do *not* cache themselves.

This cache does *not* cache:

* Type hints declared by the :mod:`typing` module, which implicitly cache
  themselves on subscription thanks to inscrutable metaclass magic.
* :pep:`563`-compliant **deferred type hints** (i.e., type hints persisted as
  evaluable strings rather than actual type hints). Ideally, this cache would
  cache the evaluations of *all* deferred type hints. Sadly, doing so is
  infeasible in the general case due to global and local namespace lookups
  (e.g., ``Dict[str, int]`` only means what you think it means if an
  importation resembling ``from typing import Dict`` preceded that type hint).

Design
--------------
**This dictionary is intentionally thread-safe.** Why? Because this dictionary
is used to modify the ``__attributes__`` dunder variable of arbitrary callables.
Since most of those callables are either module- or class-scoped, that variable
is effectively global. To prevent race conditions between competing threads
contending over that global variable, this dictionary *must* be thread-safe.

This dictionary is intentionally designed as a naive dictionary rather than a
robust LRU cache, for the same reasons that callables accepting hints are
memoized by the :func:`beartype._util.cache.utilcachecall.callable_cached`
rather than the :func:`functools.lru_cache` decorator. Why? Because:

* The number of different type hints instantiated across even worst-case
  codebases is negligible in comparison to the space consumed by those hints.
* The :attr:`sys.modules` dictionary persists strong references to all
  callables declared by previously imported modules. In turn, the
  ``func.__annotations__`` dunder dictionary of each such callable persists
  strong references to all type hints annotating that callable. In turn, these
  two statements imply that type hints are *never* garbage collected but
  instead persisted for the lifetime of the active Python process. Ergo,
  temporarily caching hints in an LRU cache is pointless, as there are *no*
  space savings in dropping stale references to unused hints.
'''

# ....................{ SANIFIERS ~ root                   }....................
#FIXME: Unit test us up, please.
#FIXME: Revise docstring in accordance with recent dramatic improvements.
def sanify_func_hint_root(
    hint: object,
    func: Callable,
    pith_name: str,
    exception_prefix: str,
) -> object:
    '''
    PEP-compliant type hint sanified (i.e., sanitized) from the passed **root
    type hint** (i.e., possibly PEP-noncompliant type hint annotating the
    parameter or return with the passed name of the passed callable) if this
    hint is reducible *or* this hint as is otherwise (i.e., if this hint is
    irreducible).

    Specifically, this function:

    * If this hint is a **PEP-noncompliant tuple union** (i.e., tuple of one or
      more standard classes and forward references to standard classes):

      * Coerces this tuple union into the equivalent :pep:`484`-compliant
        union.
      * Replaces this tuple union in the ``__annotations__`` dunder tuple of
        this callable with this :pep:`484`-compliant union.
      * Returns this :pep:`484`-compliant union.

    * Else if this hint is already PEP-compliant, preserves and returns this
      hint unmodified as is.
    * Else (i.e., if this hint is neither PEP-compliant nor -noncompliant and
      thus invalid as a type hint), raise an exception.

    Caveats
    ----------
    This function *cannot* be meaningfully memoized, since the passed type hint
    is *not* guaranteed to be cached somewhere. Only functions passed cached
    type hints can be meaningfully memoized. Even if this function *could* be
    meaningfully memoized, there would be no benefit; this function is only
    called once per parameter or return of the currently decorated callable.

    This function is intended to be called *after* all possibly
    :pep:`563`-compliant **deferred type hints** (i.e., type hints persisted as
    evaluatable strings rather than actual type hints) annotating this callable
    if any have been evaluated into actual type hints.

    Parameters
    ----------
    hint : object
        Possibly PEP-noncompliant root type hint to be sanified.
    func : Callable
        Callable that this hint directly annotates a parameter or return of.
    pith_name : str
        Either:

        * If this hint annotates a parameter, the name of that parameter.
        * If this hint annotates the return, ``"return"``.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    Returns
    ----------
    object
        Either:

        * If this hint is PEP-noncompliant, a PEP-compliant type hint converted
          from this hint.
        * If this hint is PEP-compliant, this hint unmodified as is.

    Raises
    ----------
    BeartypeDecorHintNonpepException
        If this object is neither:

        * A PEP-noncompliant type hint.
        * A supported PEP-compliant type hint.
    '''

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize with the sanify_hint_root() sanitizer, please.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # PEP-compliant type hint coerced (i.e., permanently converted in the
    # annotations dunder dictionary of the passed callable) from this possibly
    # PEP-noncompliant type hint if this hint is coercible *OR* this hint as is
    # otherwise. Since the passed hint is *NOT* necessarily PEP-compliant,
    # perform this coercion *BEFORE* validating this hint to be PEP-compliant.
    hint = func.__annotations__[pith_name] = coerce_func_hint_root(
        hint=hint,
        func=func,
        pith_name=pith_name,
        exception_prefix=exception_prefix,
    )

    # If this object is neither a PEP-noncompliant type hint *NOR* supported
    # PEP-compliant type hint, raise an exception.
    #
    # Note that this function call is effectively memoized and thus efficient.
    die_unless_hint(hint=hint, exception_prefix=exception_prefix)
    # Else, this object is a supported PEP-compliant type hint.

    # Reduce this hint to a lower-level PEP-compliant type hint if this hint is
    # reducible *OR* this hint as is otherwise. Reductions simplify subsequent
    # logic elsewhere by transparently converting non-trivial hints (e.g.,
    # numpy.typing.NDArray[...]) into semantically equivalent trivial hints
    # (e.g., beartype validators).
    #
    # Whereas the above coercion permanently persists for the duration of the
    # active Python process (i.e., by replacing the original type hint in the
    # annotations dunder dictionary of this callable), this reduction only
    # temporarily persists for the duration of the current call stack. Why?
    # Because hints explicitly coerced above are assumed to be either:
    # * PEP-noncompliant and thus harmful (in the general sense).
    # * PEP-compliant but semantically deficient and thus equally harmful (in
    #   the general sense).
    #
    # In either case, coerced type hints are generally harmful in *ALL*
    # possible contexts for *ALL* possible consumers (including other competing
    # runtime type-checkers). Reduced type hints, however, are *NOT* harmful in
    # any sense whatsoever; they're simply non-trivial for @beartype to support
    # in their current form and thus temporarily reduced in-memory into a more
    # convenient form for beartype-specific type-checking purposes elsewhere.
    #
    # Note that parameters are intentionally passed positionally to both
    # optimize memoization efficiency and circumvent memoization warnings.
    hint = reduce_hint(hint, exception_prefix)

    # Return this sanified hint.
    return hint


#FIXME: Unit test us up, please.
#FIXME: Revise docstring in accordance with recent dramatic improvements.
def sanify_hint_root(hint: object, exception_prefix: str) -> object:
    '''
    PEP-compliant type hint sanified (i.e., sanitized) from the passed **root
    type hint** (i.e., possibly PEP-noncompliant type hint that has *no* parent
    type hint) if this hint is reducible *or* this hint as is otherwise (i.e.,
    if this hint is irreducible).

    Specifically, this function:

    * If this hint is a **PEP-noncompliant tuple union** (i.e., tuple of one or
      more standard classes and forward references to standard classes):

      * Coerces this tuple union into the equivalent :pep:`484`-compliant
        union.
      * Replaces this tuple union in the ``__annotations__`` dunder tuple of
        this callable with this :pep:`484`-compliant union.
      * Returns this :pep:`484`-compliant union.

    * Else if this hint is already PEP-compliant, preserves and returns this
      hint unmodified as is.
    * Else (i.e., if this hint is neither PEP-compliant nor -noncompliant and
      thus invalid as a type hint), raise an exception.

    Caveats
    ----------
    This function *cannot* be meaningfully memoized, since the passed type hint
    is *not* guaranteed to be cached somewhere. Only functions passed cached
    type hints can be meaningfully memoized. Even if this function *could* be
    meaningfully memoized, there would be no benefit; this function is only
    called once per parameter or return of the currently decorated callable.

    This function is intended to be called *after* all possibly
    :pep:`563`-compliant **deferred type hints** (i.e., type hints persisted as
    evaluatable strings rather than actual type hints) annotating this callable
    if any have been evaluated into actual type hints.

    Parameters
    ----------
    hint : object
        Possibly PEP-noncompliant root type hint to be sanified.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    Returns
    ----------
    object
        Either:

        * If this hint is PEP-noncompliant, a PEP-compliant type hint converted
          from this hint.
        * If this hint is PEP-compliant, this hint unmodified as is.

    Raises
    ----------
    BeartypeDecorHintNonpepException
        If this object is neither:

        * A PEP-noncompliant type hint.
        * A supported PEP-compliant type hint.
    '''

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize with the sanify_func_hint_root() sanitizer, please.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # PEP-compliant type hint coerced from this possibly PEP-noncompliant type
    # hint if this hint is coercible *OR* this hint as is otherwise. Since the
    # passed hint is *NOT* necessarily PEP-compliant, perform this coercion
    # *BEFORE* validating this hint to be PEP-compliant.
    hint = coerce_hint_root(hint=hint, exception_prefix=exception_prefix)

    # If this object is neither a PEP-noncompliant type hint *NOR* supported
    # PEP-compliant type hint, raise an exception.
    #
    # Note that this function call is effectively memoized and thus efficient.
    die_unless_hint(hint=hint, exception_prefix=exception_prefix)
    # Else, this object is a supported PEP-compliant type hint.

    # Reduce this hint to a lower-level PEP-compliant type hint if this hint is
    # reducible *OR* this hint as is otherwise. See
    # sanify_func_hint_root() for further commentary.
    hint = reduce_hint(hint, exception_prefix)

    # Return this sanified hint.
    return hint

# ....................{ SANIFIERS ~ child                  }....................
def sanify_hint_child(hint: object, exception_prefix: str) -> Any:
    '''
    PEP-compliant type hint sanified (i.e., sanitized) from the passed
    **PEP-compliant child type hint** (i.e., hint transitively subscripting the
    root type hint annotating a parameter or return of the currently decorated
    callable) if this hint is reducible *or* this hint as is otherwise (i.e., if
    this hint is *not* irreducible).

    Parameters
    ----------
    hint : object
        PEP-compliant type hint to be sanified.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    Returns
    ----------
    object
        PEP-compliant type hint sanified from this hint.
    '''

    # This sanifier covers the proper subset of logic performed by the
    # sanify_hint_root() sanifier applicable to child type hints.

    # PEP-compliant type hint coerced (i.e., permanently converted in the
    # annotations dunder dictionary of the passed callable) from this possibly
    # PEP-noncompliant type hint if this hint is coercible *OR* this hint as is
    # otherwise. Since the passed hint is *NOT* necessarily PEP-compliant,
    # perform this coercion *BEFORE* validating this hint to be PEP-compliant.
    hint = coerce_hint_any(hint)

    # Return this hint reduced.
    return reduce_hint(hint, exception_prefix)
