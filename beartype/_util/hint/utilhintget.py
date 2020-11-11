#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-agnostic type hint getter utilities** (i.e., callables querying
arbitrary objects for attributes applicable to both PEP-compliant and
-noncompliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.py.utilpymodule import get_module_attr_name_relative_to_obj

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS ~ forwardref              }....................
def get_hint_forwardref_classname(hint: object) -> str:
    '''
    Possibly unqualified classname referred to by the passed **forward
    reference type hint** (i.e., object indirectly referring to a user-defined
    class that typically has yet to be defined).

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
    :func:`get_hint_forwardref_classname_qualified`
        Getter returning fully-qualified forward reference classnames.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.utilhinttest import die_unless_hint_forwardref
    from beartype._util.hint.pep.proposal.utilhintpep484 import (
        get_hint_pep484_forwardref_class_basename,
        is_hint_pep484_forwardref,
    )

    # If this is *NOT* a forward reference type hint, raise an exception.
    die_unless_hint_forwardref(hint)

    # Return either...
    return (
        # If this hint is a PEP 484-compliant forward reference, the
        # unqualified classname referred to by this reference.
        get_hint_pep484_forwardref_class_basename(hint)
        if is_hint_pep484_forwardref(hint) else
        # Else, this hint is a string. In this case, return this string as is.
        hint
    )


def get_hint_forwardref_classname_relative_to_obj(
    obj: object, hint: object) -> str:
    '''
    Fully-unqualified classname referred to by the passed **forward
    reference type hint** (i.e., object indirectly referring to a user-defined
    class that typically has yet to be defined) canonicalized if this hint is
    unqualified relative to the module declaring the passed object (e.g.,
    callable, class).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    obj : object
        Object to canonicalize the classname referred to by this forward
        reference if that classname is unqualified (i.e., relative).
    hint : object
        Forward reference to be canonicalized.

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
    :func:`get_hint_forwardref_classname_qualified`
        Getter returning fully-qualified forward reference classnames.
    '''

    # Return the fully-unqualified classname referred to by this forward
    # reference canonicalized relative to the module declaring this object.
    return get_module_attr_name_relative_to_obj(
        obj=obj,
        module_attr_name=get_hint_forwardref_classname(hint),
    )
