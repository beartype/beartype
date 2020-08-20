#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-agnostic type hint utilities.**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from typing import Any, Union
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.nonpep.utilhintnonpeptest import (
    die_unless_hint_nonpep, is_hint_nonpep)
from beartype._util.hint.pep.utilhintpeptest import (
    die_unless_hint_pep_supported, is_hint_pep, is_hint_pep_supported)

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
HINTS_IGNORABLE = {
    # Ignorable non-"typing" types.
    object,

    # Ignorable "typing" objects.
    Any,

    # Ignorable "typing" unions.
    Union,
    Union[Any],
    Union[object],
    Union[Any, object],
    Union[object, Any],
}
'''
Set of all annotation objects to be unconditionally ignored during
annotation-based type checking in the :func:`beartype` decorator regardless of
callable context (e.g., parameter, return value).

This includes:

* The PEP-noncompliant builtin :class:`object` type, syntactically synonymous
  with the :class:`beartype.cave.AnyType` type. Since :class:`object` is the
  transitive superclass of all classes, parameters and return values annotated
  as :class:`object` unconditionally match *all* objects under
  :func:`isinstance`-based type covariance and thus semantically reduce to
  unannotated parameters and return values.
* The PEP-compliant:

  * :data:`Any` singleton object, semantically synonymous with the
    :class:`AnyType` and hence :class:`object` types.
  * :data:`Union` singleton object. Since `PEP 484`_ stipulates that an
    unsubscripted subscriptable PEP-compliant object (e.g., ``Generic``,
    ``Iterable``) semantically expands to that object subscripted by an
    implicit :data:`Any` argument, :data:`Union` semantically expands to an
    implicit :data:`Union[Any]` singleton object. Despite their semantic
    equivalency, however, note that these objects remain syntactically distinct
    with respect to object identification (i.e., ``Union is not Union[Any]``).
    Ergo, this set necessarily lists both distinct singleton objects.
  * :data:`Union[Any]` and :data:`Union[object]` singleton objects. Since `PEP
    484`_ stipulates that a union of one type semantically reduces to merely
    that type, :data:`Union[Any]` semantically reduces to merely :data:`Any`
    and :data:`Union[object]` semantically reduces to merely :data:`object`.
  * :data:`Union[Any, object]` and :data:`Union[object, Any]` singleton
    objects. Since both :data:`Union[Any]` and :data:`Union[object]`
    semantically reduce to a noop, so too do all permutations of those unions.
    Ideally, :data:`Union[Any, object]` and :data:`Union[object, Any]` would be
    cached as the same singleton object. For unknown reasons (presumably,
    unintentional bugs), they currently are *not* under *all* current revisions
    of the :mod:`typing` module (namely, Python 3.5 through 3.8). Why? Because
    order is significant rather than insignificant in :data:`Union` arguments.
    Naturally, this is ludicrous -- but so is most of both `PEP 484`_ and its
    implementation in the :mod:`typing` module. A :data:`Union` is merely a set
    of PEP-compliant objects; sets are unordered; ergo, so should
    :data:`Union`. Since we have no say in the matter, we strenuously object in
    the only meaningful way we can: with a docstring rant no one will ever
    read. (This is that docstring rant, by the way.)

Although PEP-specific logic should typically be isolated to private
PEP-specific submodules for maintainability, defining this set here *improves*
maintainability by centralizing similar logic across the codebase.

Examples
----------
The :mod:`typing` module aggressively caches subscripted objects produced by
that module. Conveniently, this guarantees that subscripting the same objects
declared by that module by the same arguments again produces the same objects,
which also guarantees that external set membership tests against this set with
subscripted objects produced by that module behave as expected: e.g.,

    >>> from typing import Any, Union
    >>> Union is Union
    True
    >>> Union is Union[Any]
    False
    >>> Union[Any] is Union[Any]
    True
    >>> Union in HINTS_IGNORABLE
    True
    >>> Union[Any] in HINTS_IGNORABLE
    True

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ EXCEPTIONS                        }....................
def die_unless_hint(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Type hint',
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
        exception message raised by this function. Defaults to ``Type hint``.
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
    # only if this hint is also *NOT* PEP-noncompliant.
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

    This tester is memoized for efficiency.

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
