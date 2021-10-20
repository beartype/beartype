#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Type hint cache** (i.e., singleton dictionary mapping from the
machine-readable representations of all non-self-cached type hints to those
hints).**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.hint.utilhintconv import (
    coerce_hint,
    reduce_hint,
)
from beartype._util.hint.utilhinttest import die_unless_hint
from collections.abc import Callable
from typing import Any

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CACHERS                           }....................
#FIXME: Shift and rename this function to simply
#beartype._util.hint.pep.utilpepconv.coerce_hint().
def coerce_hint_pep(
    func: Callable,
    pith_name: str,
    hint: object,
    exception_prefix: str,
) -> object:
    '''
    Coerce the passed type hint annotating the parameter or return with the
    passed name of the passed callable into the corresponding PEP-compliant
    type hint if needed.

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
    func : Callable
        Callable to coerce this type hint of.
    pith_name : str
        Either:

        * If this hint annotates a parameter, the name of that parameter.
        * If this hint annotates the return, ``"return"``.
    hint : object
        Type hint to be rendered PEP-compliant.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    Returns
    ----------
    object
        Either:

        * If this hint is PEP-noncompliant, PEP-compliant type hint converted
          from this hint.
        * If this hint is PEP-compliant, hint unmodified as is.

    Raises
    ----------
    BeartypeDecorHintNonpepException
        If this object is neither:

        * A PEP-noncompliant type hint.
        * A supported PEP-compliant type hint.
    '''
    assert callable(func), f'{repr(func)} not callable.'
    assert isinstance(pith_name, str), f'{pith_name} not string.'

    # ..................{ COERCION                          }..................
    # Original instance of this hint *PRIOR* to being subsequently coerced.
    # PEP-compliant type hint coerced (i.e., permanently converted in the
    # ``__annotations__`` dunder dictionary of the passed callable) from the
    # passed possibly PEP-noncompliant type hint if this hint is coercible *or*
    # this hint as is otherwise (i.e., if this hint is irreducible).
    hint_coerced = coerce_hint(
        hint=hint,
        func=func,
        pith_name=pith_name,
        exception_prefix=exception_prefix,
    )

    # If this hint was coerced above into a different type hint, replace the
    # original instance of this hint in the annotations dunder dictionary
    # attached to the decorated callable with the new instance of this hint.
    if hint is not hint_coerced:
        hint = func.__annotations__[pith_name] = hint_coerced

    # ..................{ VALIDATION                        }..................
    # If this object is neither a PEP-noncompliant type hint *NOR* supported
    # PEP-compliant type hint, raise an exception.
    die_unless_hint(hint=hint, exception_prefix=exception_prefix)
    # Else, this object is either a PEP-noncompliant type hint *OR* supported
    # PEP-compliant type hint.

    # ..................{ REDUCTION                         }..................
    # Reduce this hint to a lower-level hint-like object associated with this
    # hint if this hint satisfies some condition, simplifying type-checking
    # generation logic elsewhere by transparently converting hints we'd rather
    # *NOT* explicitly support (e.g., "numpy.typing.NDArray" hints) into
    # semantically equivalent hints we would (e.g., beartype validators).
    #
    # Note that:
    # * We intentionally do *NOT* permanently coerce this reduction into this
    #   callable's type hints map above (i.e., "func.__annotations__"). Type
    #   hints explicitly coerced above are assumed to be either:
    #   * PEP-noncompliant and thus harmful (in a general sense).
    #   * PEP-compliant but semantically deficient and thus equally harmful (in
    #     a general sense).
    #   In either case, coerced type hints are generally harmful in *ALL*
    #   possible contexts for *ALL* possible consumers (including other
    #   competing runtime type-checkers). Reduced type hints, however, are
    #   *NOT* harmful in any sense whatsoever; they're simply non-trivial for
    #   @beartype to support in their current form and thus temporarily reduced
    #   in-memory into a more convenient form for beartype-specific
    #   type-checking purposes elsewhere.
    # * Parameters are intentionally passed positionally to both optimize
    #   memoization efficiency and circumvent memoization warnings.
    hint = reduce_hint(hint, exception_prefix)

    # Return this hint.
    return hint
