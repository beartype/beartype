#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-agnostic type hint tester utilities** (i.e., callables
validating arbitrary objects to be PEP-agnostic type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.nonpep.utilhintnonpeptest import (
    die_unless_hint_nonpep, is_hint_nonpep)
from beartype._util.hint.pep.utilhintpepget import get_hint_pep_typing_attr
from beartype._util.hint.pep.utilhintpeptest import (
    die_unless_hint_pep_supported, is_hint_pep, is_hint_pep_supported)
from beartype._util.hint.utilhintdata import HINTS_SHALLOW_IGNORABLE
from typing import Union

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ EXCEPTIONS                        }....................
def die_unless_hint(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Annotated',
    is_str_valid: bool = True,
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
    passed ``hint_label`` parameter is typically unique to each call to this
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
    hint_label : Optional[str]
        Human-readable label prefixing this object's representation in the
        exception message raised by this function. Defaults to ``"Annotated"``.
    is_str_valid : Optional[bool]
        ``True`` only if this function permits this object to be a string.
        Defaults to ``True``. If this boolean is:

        * ``True``, this object is valid only if this object is either a class,
          classname, or tuple of classes and/or classnames.
        * ``False``, this object is valid only if this object is either a class
          or tuple of classes.

    Raises
    ----------
    TypeError
        If this object is **unhashable** (i.e., *not* hashable by the builtin
        :func:`hash` function and thus unusable in hash-based containers like
        dictionaries and sets). All supported type hints are hashable.
    BeartypeDecorHintPepUnsupportedException
        If this object is hashable but is a PEP-compliant type hint currently
        unsupported by the :func:`beartype.beartype` decorator.
    BeartypeDecorHintNonPepException
        If this object is hashable but is neither a supported PEP-compliant nor
        -noncompliant type hint.
    '''

    # If this object is a supported type hint, reduce to a noop.
    #
    # Note that this memoized call is intentionally passed positional rather
    # than keyword parameters to maximize efficiency.
    if is_hint(hint, is_str_valid):
        return
    # Else, this object is *NOT* a supported type hint. In this case,
    # subsequent logic raises an exception specific to the passed parameters.

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with is_hint() below.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # If this hint is PEP-compliant, raise an exception only if this hint is
    # currently unsupported by @beartype.
    if is_hint_pep(hint):
        die_unless_hint_pep_supported(
            hint=hint,
            hint_label=hint_label,
        )

    # Else, this hint is *NOT* PEP-compliant. In this case, raise an exception
    # only if this hint is also *NOT* PEP-noncompliant. By design, all
    # PEP-noncompliant type hints are supported by @beartype.
    die_unless_hint_nonpep(
        hint=hint,
        hint_label=hint_label,
        is_str_valid=is_str_valid,
    )

# ....................{ TESTERS                           }....................
@callable_cached
def is_hint(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    is_str_valid: bool = True,
) -> bool:
    '''
    ``True`` only if the passed object is a **supported type hint** (i.e.,
    object supported by the :func:`beartype.beartype` decorator as a valid type
    hint annotating callable parameters and return values).

    This tester function is memoized for efficiency.

    Parameters
    ----------
    hint : object
        Object to be validated.
    is_str_valid : Optional[bool]
        ``True`` only if this function permits this object to be a string.
        Defaults to ``True``. If this boolean is:

        * ``True``, this object is valid only if this object is either a class,
          classname, or tuple of classes and/or classnames.
        * ``False``, this object is valid only if this object is either a class
          or tuple of classes.

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
        #
        # Note that this memoized call is intentionally passed positional
        # rather than keyword parameters to maximize efficiency.
        is_hint_nonpep(hint, is_str_valid)
    )


@callable_cached
def is_hint_ignorable(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a **deeply ignorable type hint.**

    Specifically, this tester function returns ``True`` only if this object is
    either:

    * In the finite set of shallowly ignorable type hints defined by the
      low-level :data:`HINTS_SHALLOW_IGNORABLE` frozenset.
    * The :data:`Union` singleton subscripted by one or more ignorable type
      hints contained in that set (e.g., ``typing.Union[typing.Any, bool]``).
      Why? Because unions are by definition only as narrow as their widest
      child hint. However, shallowly ignorable type hints are ignorable
      precisely because they are the widest possible hints (e.g.,
      :class:`object`, :attr:`typing.Any`), which are so wide as to constrain
      nothing and convey no meaningful semantics. A union of one or more
      shallowly ignorable child hints is thus the widest possible union, which
      is so wide as to constrain nothing and convey no meaningful semantics.
      Since there exist a countably infinite number of possible :data:`Union`
      subscriptions by one or more shallowly ignorable type hints, these
      subscriptions *cannot* be explicitly listed in the
      :data:`HINTS_SHALLOW_IGNORABLE` frozenset. Instead, these subscriptions
      are dynamically detected by this tester at runtime and thus referred to
      as **deeply ignorable type hints.**

    This tester function is memoized for efficiency.

    Parameters
    ----------
    hint : object
        Object to be validated.

    Returns
    ----------
    bool
        ``True`` only if this object is a deeply ignorable type hint.

    Raises
    ----------
    TypeError
        If this object is **unhashable** (i.e., *not* hashable by the builtin
        :func:`hash` function and thus unusable in hash-based containers like
        dictionaries and sets). All supported type hints are hashable.
    '''

    # If this hint is shallowly ignorable, return true.
    if hint in HINTS_SHALLOW_IGNORABLE:
        return True
    # Else, this hint is *NOT* shallowly ignorable.

    # If this is a PEP-compliant type hint...
    if is_hint_pep(hint):
        # Argumentless typing attribute uniquely identifying this hint.
        hint_attr = get_hint_pep_typing_attr(hint)

        # If this hint is a union, return true only if...
        if hint_attr is Union:
            # Any...
            return any(
                # Child hint of this union is shallowly ignorable. See the
                # function docstring for an explanatory justification.
                #
                # Note that the "__args__" dunder attribute is *NOT* generally
                # guaranteed to exist for arbitrary PEP-compliant type hints
                # but is guaranteed to exist for all unions other than the
                # shallowly ignorable argumentless "typing.Optional" and
                # "typing.Union" attributes, which are guaranteed to be
                # shallowly ignorable and thus already handled above.
                hint_child in HINTS_SHALLOW_IGNORABLE
                for hint_child in hint.__args__
            )
        # Else, this hint is *NOT* a union and thus *NOT* deeply ignorable.
    # Else, this is a PEP-noncompliant type hint and thus *NOT* deeply
    # ignorable.

    # Else, this hint is neither shallowly nor deeply ignorable. In this case,
    # return false.
    return False
