#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-agnostic type hint tester utilities** (i.e., callables
validating arbitrary objects to be type hints supported by :mod:`beartype`,
regardless of whether those hints comply with PEP standards or not).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._data.hint.pep.datapeprepr import HINTS_REPR_IGNORABLE_SHALLOW
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.nonpep.utilnonpeptest import (
    die_unless_hint_nonpep,
    is_hint_nonpep,
)
from beartype._util.hint.pep.utilpeptest import (
    die_if_hint_pep_unsupported,
    is_hint_pep,
    is_hint_pep_supported,
)

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ VALIDATORS                        }....................
def die_unless_hint(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed object is a **supported type hint**
    (i.e., object supported by the :func:`beartype.beartype` decorator as a
    valid type hint annotating callable parameters and return values).

    Specifically, this function raises an exception if this object is neither:

    * A **supported PEP-compliant type hint** (i.e., :mod:`beartype`-agnostic
      annotation compliant with annotation-centric PEPs currently supported
      by the :func:`beartype.beartype` decorator).
    * A **PEP-noncompliant type hint** (i.e., :mod:`beartype`-specific
      annotation intentionally *not* compliant with annotation-centric PEPs).

    Efficiency
    ----------
    This validator is effectively (but technically *not*) memoized. Since the
    passed ``exception_prefix`` parameter is typically unique to each call to this
    validator, memoizing this validator would uselessly consume excess space
    *without* improving time efficiency. Instead, this validator first calls
    the memoized :func:`is_hint_pep` tester. If that tester returns ``True``,
    this validator immediately returns ``True`` and is thus effectively
    memoized; else, this validator inefficiently raises a human-readable
    exception without memoization. Since efficiency is largely irrelevant in
    exception handling, this validator thus remains effectively memoized.

    Parameters
    ----------
    hint : object
        Object to be validated.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ----------
    :exc:`BeartypeDecorHintPepUnsupportedException`
        If this object is a PEP-compliant type hint currently unsupported by
        the :func:`beartype.beartype` decorator.
    :exc:`BeartypeDecorHintNonpepException`
        If this object is neither a:

        * Supported PEP-compliant type hint.
        * Supported PEP-noncompliant type hint.
    '''

    # If this object is a supported type hint, reduce to a noop.
    if is_hint(hint):
        return
    # Else, this object is *NOT* a supported type hint. In this case,
    # subsequent logic raises an exception specific to the passed parameters.

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with is_hint() below.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # If this hint is PEP-compliant, raise an exception only if this hint is
    # currently unsupported by @beartype.
    if is_hint_pep(hint):
        die_if_hint_pep_unsupported(
            hint=hint, exception_prefix=exception_prefix)
    # Else, this hint is *NOT* PEP-compliant. In this case...

    # Raise an exception only if this hint is also *NOT* PEP-noncompliant. By
    # definition, all PEP-noncompliant type hints are supported by @beartype.
    die_unless_hint_nonpep(hint=hint, exception_prefix=exception_prefix)

# ....................{ TESTERS                           }....................
@callable_cached
def is_hint(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a **supported type hint** (i.e.,
    object supported by the :func:`beartype.beartype` decorator as a valid type
    hint annotating callable parameters and return values).

    This tester function is memoized for efficiency.

    Parameters
    ----------
    hint : object
        Object to be validated.

    Returns
    ----------
    bool
        ``True`` only if this object is either:

        * A **PEP-compliant type hint** (i.e., :mod:`beartype`-agnostic
          annotation compliant with annotation-centric PEPs).
        * A **PEP-noncompliant type hint** (i.e., :mod:`beartype`-specific
          annotation intentionally *not* compliant with annotation-centric
          PEPs).

    Raises
    ----------
    TypeError
        If this object is **unhashable** (i.e., *not* hashable by the builtin
        :func:`hash` function and thus unusable in hash-based containers like
        dictionaries and sets). All supported type hints are hashable.
    '''

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with die_unless_hint() above.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Return true only if...
    return (
        # This is a PEP-compliant type hint supported by @beartype *OR*...
        is_hint_pep_supported(hint) if is_hint_pep(hint) else
        # This is a PEP-noncompliant type hint, which by definition is
        # necessarily supported by @beartype.
        is_hint_nonpep(hint=hint, is_str_valid=True)
    )

# ....................{ TESTERS ~ ignorable               }....................
@callable_cached
def is_hint_ignorable(hint: object) -> bool:
    '''
    ``True`` only if the passed type hint is **ignorable.**

    This tester function is memoized for efficiency.

    Parameters
    ----------
    hint : object
        Type hint to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this type hint is ignorable.
    '''

    # If this hint is shallowly ignorable, return true.
    if repr(hint) in HINTS_REPR_IGNORABLE_SHALLOW:
        return True
    # Else, this hint is *NOT* shallowly ignorable.

    # If this hint is PEP-compliant...
    if is_hint_pep(hint):
        # Avoid circular import dependencies.
        from beartype._util.hint.pep.utilpeptest import (
            is_hint_pep_ignorable)

        # Defer to the function testing whether this hint is an ignorable
        # PEP-compliant type hint.
        return is_hint_pep_ignorable(hint)

    # Else, this hint is PEP-noncompliant and thus *NOT* deeply ignorable.
    # Since this hint is also *NOT* shallowly ignorable, this hint is
    # unignorable. In this case, return false.
    return False
