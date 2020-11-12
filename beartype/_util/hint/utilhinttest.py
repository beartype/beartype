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
from beartype.roar import (
    BeartypeDecorHintForwardRefException,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.nonpep.utilhintnonpeptest import (
    die_unless_hint_nonpep,
    is_hint_nonpep,
)
from beartype._util.hint.pep.utilhintpeptest import (
    die_if_hint_pep_unsupported,
    is_hint_pep,
    is_hint_pep_supported,
)
from beartype._util.hint.data.utilhintdata import (
    HINT_BASES_FORWARDREF,
    HINTS_IGNORABLE_SHALLOW,
)

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ EXCEPTIONS                        }....................
def die_unless_hint(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Annotated',
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
            hint=hint,
            hint_label=hint_label,
        )

    # Else, this hint is *NOT* PEP-compliant. In this case, raise an exception
    # only if this hint is also *NOT* PEP-noncompliant. By definition, all
    # PEP-noncompliant type hints are supported by @beartype.
    die_unless_hint_nonpep(
        hint=hint,
        hint_label=hint_label,
    )

# ....................{ EXCEPTIONS ~ forwardref           }....................
def die_unless_hint_forwardref(hint: object) -> None:
    '''
    Raise an exception unless the passed object is a **forward reference type
    hint** (i.e., object indirectly referring to a user-defined class that
    typically has yet to be defined).

    Parameters
    ----------
    hint : object
        Object to be validated.

    Raises
    ----------
    BeartypeDecorHintForwardRefException
        If this object is *not* a forward reference type hint.
    '''

    # If this is *NOT* a forward reference type hint, raise an exception.
    if not is_hint_forwardref(hint):
        raise BeartypeDecorHintForwardRefException(
            f'Type hint {repr(hint)} not forward reference.')

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
        is_hint_nonpep(hint)
    )

# ....................{ TESTERS ~ ignorable               }....................
@callable_cached
def is_hint_ignorable(hint: object) -> bool:
    '''
    ``True`` only if the passed object is an **ignorable type hint.**

    This tester function is memoized for efficiency.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is an ignorable type hint.

    Raises
    ----------
    TypeError
        If this object is **unhashable** (i.e., *not* hashable by the builtin
        :func:`hash` function and thus unusable in hash-based containers like
        dictionaries and sets). All supported type hints are hashable.
    '''

    # If this hint is shallowly ignorable, return true.
    if hint in HINTS_IGNORABLE_SHALLOW:
        return True
    # Else, this hint is *NOT* shallowly ignorable.

    # If this hint is PEP-compliant...
    if is_hint_pep(hint):
        # Avoid circular import dependencies.
        from beartype._util.hint.pep.utilhintpeptest import (
            is_hint_pep_ignorable)

        # Defer to the function testing whether this hint is an ignorable
        # PEP-compliant type hint.
        return is_hint_pep_ignorable(hint)

    # Else, this hint is PEP-noncompliant and thus *NOT* deeply ignorable.
    # Since this hint is also *NOT* shallowly ignorable, this hint is
    # unignorable. In this case, return false.
    return False

# ....................{ TESTERS ~ forwardref              }....................
def is_hint_forwardref(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a **forward reference type hint**
    (i.e., object indirectly referring to a user-defined class that typically
    has yet to be defined).

    Specifically, this tester returns ``True`` only if this object is either:

    * A string whose value is the syntactically valid name of a class.
    * An instance of the :class:`typing.ForwardRef` class. The :mod:`typing`
      module implicitly replaces all strings subscripting :mod:`typing` objects
      (e.g., the ``MuhType`` in ``List['MuhType']``) with
      :class:`typing.ForwardRef` instances containing those strings as instance
      variables, for nebulous reasons that make little justifiable sense but
      what you gonna do 'cause this is 2020. *Fight me.*

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a forward reference type hint.
    '''

    # Return true only if this hint is an instance of a PEP-compliant forward
    # reference superclass.
    return isinstance(hint, HINT_BASES_FORWARDREF)
