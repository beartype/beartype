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
        Fully-qualified classname referred to by this forward reference
        relative to this callable.

    Raises
    ----------
    BeartypeDecorHintForwardRefException
        If either:

        * This callable is *not* actually callable.
        * This forward reference is *not* actually a forward reference.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.utilhinttest import die_unless_hint_forwardref
    from beartype._util.hint.pep.proposal.utilhintpep484 import (
        get_hint_pep484_forwardref_classname_unqualified,
        is_hint_pep484_forwardref,
    )

    # If this is *NOT* a forward reference type hint, raise an exception.
    die_unless_hint_forwardref(hint)

    # Return either...
    return (
        # If this hint is a PEP 484-compliant forward reference, the
        # unqualified classname referred to by this reference.
        get_hint_pep484_forwardref_classname_unqualified(hint)
        if is_hint_pep484_forwardref(hint) else
        # Else, this hint is a string. In this case, return this string as is.
        hint
    )
