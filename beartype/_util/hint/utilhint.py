#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-agnostic type hint utilities.**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorHintValueUnhashableException
from beartype._util.hint.utilhintnonpep import die_unless_hint_nonpep
from beartype._util.hint.utilhintpep import die_unless_hint_pep, is_hint_pep
from beartype._util.utilobj import is_object_hashable
# from beartype._util.utilcache import callable_cached

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ EXCEPTIONS                        }....................
#FIXME: Memoize this function with @callable_cached, as the tuple iteration
#performed by the die_unless_hint_nonpep() validator called by this function is
#particularly costly. However, note that doing so will require generalizing the
#@callable_cached decorator to memoize not merely return values but *RAISED
#EXCEPTIONS* as well. This shouldn't be terribly arduous and has
#general-purpose merit beyond merely this function.

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

    * A **PEP-compliant type hint** (i.e., :mod:`beartype`-agnostic annotation
      compliant with annotation-centric PEPs).
    * A **PEP-noncompliant type hint** (i.e., :mod:`beartype`-specific
      annotation intentionally *not* compliant with annotation-centric PEPs).

    Parameters
    ----------
    hint : object
        Object to be validated.
    hint_label : Optional[str]
        Human-readable noun prefixing this object's representation in the
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
    BeartypeDecorHintValueUnhashableException
        If this object is **unhashable** (i.e., *not* hashable by the builtin
        :func:`hash` function and thus unusable in hash-based containers like
        dictionaries and sets). All supported type hints are hashable.
    BeartypeDecorHintValueNonPepException
        If this object is hashable but is neither a PEP-compliant nor
        -noncompliant type hint.
    '''

    # If this hint is unhashable, this hint is unsupported. In this case, raise
    # an exception.
    if not is_object_hashable(hint):
        raise BeartypeDecorHintValueUnhashableException(
            '{} {!r} unhashable.'.format(hint_label, hint))
    # Else, this object is hashable.

    # If this hint is PEP-compliant, raise an exception only if this hint is
    # currently unsupported by @beartype.
    if is_hint_pep(hint):
        die_unless_hint_pep(
            hint=hint,
            hint_label=hint_label,
            # is_str_valid=is_str_valid,
        )
    # Else, this hint is *NOT* PEP-compliant. In this case, raise an exception
    # only if this hint is also *NOT* PEP-noncompliant.
    else:
        die_unless_hint_nonpep(
            hint=hint,
            hint_label=hint_label,
            is_str_valid=is_str_valid,
        )
