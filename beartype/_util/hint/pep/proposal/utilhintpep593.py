#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 593`_**-compliant type hint utilities.**

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 593:
    https://www.python.org/dev/peps/pep-0593
'''

# ....................{ IMPORTS                           }....................
# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ TESTERS                           }....................
def is_hint_pep593(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a `PEP 593`_**-compliant user-defined
    type hint hint** (i.e., subscription of the :attr:`typing.Annotated`
    singleton).

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
        ``True`` only if this object is a `PEP 593`_-compliant user-defined
        type hint hint.

    .. _PEP 593:
       https://www.python.org/dev/peps/pep-0593
    '''

    # Return true only if the machine-readable representation of this object
    # implies this object to be a PEP 593-compliant type hint hint.
    #
    # Note that this approach has been intentionally designed to apply to
    # arbitrary and hence possibly PEP-noncompliant type hints. Notably, this
    # approach avoids the following equally applicable but considerably less
    # efficient heuristic:
    #    return (
    #        is_hint_pep(hint) and get_hint_pep_typing_attr(hint) is Annotated)
    return repr(hint).startswith('typing.Annotated[')
