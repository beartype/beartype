#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-agnostic type hint getter utilities** (i.e., callables querying
arbitrary objects for attributes specific to PEP-agnostic type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.hint.pep.utilhintpepdata import (
    TYPING_ATTR_ARGLESS_TO_TYPE_GET)

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ IMPORTS                           }....................
def get_hint_isinstanceable_type_or_none(hint: object) -> '(type, None)':
    '''
    Non-:mod:`typing` superclass suitable for shallowly type-checking all
    parameters and return values annotated by the passed PEP-agnostic type hint
    by calling the :func:`isinstance` builtin with those parameters or return
    values and that superclass if this hint is associated with such a
    superclass *or* ``None`` otherwise (i.e., if this hint is associated with
    no such superclass).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient series of simple tests.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    (type, None)
        Either:

        * If this object is:

          * A non-:mod:`typing` class (e.g., :class:`str`), this object is
            returned as is.
          * An argumentless :mod:`typing` object associated with a
            non-:mod:`typing` superclass (e.g., :attr:`typing.Dict`, associated
            with :class:`dict`), that superclass is returned.

        * Else, ``None``.

    Raises
    ----------
    TypeError
        If this object is **unhashable** (i.e., *not* hashable by the builtin
        :func:`hash` function and thus unusable in hash-based containers like
        dictionaries and sets). All supported type hints are hashable.
    '''

    # Return either...
    return TYPING_ATTR_ARGLESS_TO_TYPE_GET(
        # If this hint is an argumentless "typing" attribute associated with
        # a non-"typing" superclass, that superclass.
        hint,
        # Else if this hint is a standard class, that class as is.
        hint if isinstance(hint, type) else
        # Else, "None".
        None
    )
