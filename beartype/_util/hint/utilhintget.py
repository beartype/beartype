#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-agnostic type hint getter utilities** (i.e., callables querying
arbitrary objects for attributes applicable to both PEP-compliant and
-noncompliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.mod.utilmodule import get_object_module_name

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS ~ forwardref              }....................
#FIXME: Unit test against nested classes.
def get_hint_forwardref_classname(hint: object) -> str:
    '''
    Possibly unqualified classname referred to by the passed **forward
    reference type hint** (i.e., object indirectly referring to a user-defined
    class that typically has yet to be defined).

    Specifically, this function returns:

    * If this hint is a :pep:`484`-compliant forward reference (i.e., instance
      of the :class:`typing.ForwardRef` class), the typically unqualified
      classname referred to by that reference. Although :pep:`484` only
      explicitly supports unqualified classnames as forward references, the
      :class:`typing.ForwardRef` class imposes *no* runtime constraints and
      thus implicitly supports both qualified and unqualified classnames.
    * If this hint is a string, the possibly unqualified classname.
      :mod:`beartype` itself intentionally imposes *no* runtime constraints and
      thus explicitly supports both qualified and unqualified classnames.

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Forward reference to be inspected.

    Returns
    ----------
    str
        Possibly unqualified classname referred to by this forward reference.

    Raises
    ----------
    BeartypeDecorHintForwardRefException
        If this forward reference is *not* actually a forward reference.

    See Also
    ----------
    :func:`get_hint_forwardref_classname_relative_to_object`
        Getter returning fully-qualified forward reference classnames.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.utilhinttest import die_unless_hint_forwardref
    from beartype._util.hint.pep.proposal.utilhintpep484 import (
        get_hint_pep484_forwardref_type_basename,
        is_hint_pep484_forwardref,
    )

    # If this is *NOT* a forward reference type hint, raise an exception.
    die_unless_hint_forwardref(hint)

    # Return either...
    return (
        # If this hint is a PEP 484-compliant forward reference, the typically
        # unqualified classname referred to by this reference.
        get_hint_pep484_forwardref_type_basename(hint)
        if is_hint_pep484_forwardref(hint) else
        # Else, this hint is a string. In this case, this string as is.
        hint
    )


#FIXME: Unit test against nested classes.
def get_hint_forwardref_classname_relative_to_object(
    hint: object, obj: object) -> str:
    '''
    Fully-qualified classname referred to by the passed **forward reference
    type hint** (i.e., object indirectly referring to a user-defined class that
    typically has yet to be defined) canonicalized if this hint is unqualified
    relative to the module declaring the passed object (e.g., callable, class).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Forward reference to be canonicalized.
    obj : object
        Object to canonicalize the classname referred to by this forward
        reference if that classname is unqualified (i.e., relative).

    Returns
    ----------
    str
        Fully-qualified classname referred to by this forward reference
        relative to this callable.

    Raises
    ----------
    BeartypeDecorHintForwardRefException
        If this forward reference is *not* actually a forward reference.
    _BeartypeUtilModuleException
        If ``module_obj`` does *not* define the ``__module__`` dunder instance
        variable.

    See Also
    ----------
    :func:`get_hint_forwardref_classname`
        Getter returning possibly unqualified forward reference classnames.
    '''

    # Possibly unqualified classname referred to by this forward reference.
    forwardref_classname = get_hint_forwardref_classname(hint)

    # Return either...
    return (
        # If this classname contains one or more "." characters and is thus
        # already hopefully fully-qualified, this classname as is;
        forwardref_classname
        if '.' in forwardref_classname else
        # Else, the "."-delimited concatenation of the fully-qualified name of
        # the module declaring this class with this unqualified classname.
        f'{get_object_module_name(obj)}.{forwardref_classname}'
    )
