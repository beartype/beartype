#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`563` **resolver data submodule.**

This submodule defines callables annotated by :pep:`563`-postponed type hints
under the ``from __future__ import annotations`` pragma, intended to be
externally imported and called from unit tests elsewhere in this test suite.
'''

# ....................{ IMPORTS                            }....................
from __future__ import annotations
from beartype.door import die_if_unbearable
from beartype.typing import (
    Generic,
    TypeVar,
)

# ....................{ GLOBALS                            }....................
T = TypeVar('T')
'''
Arbitrary type variable.
'''

# ....................{ CLASSES                            }....................
class ToAvariceOrPride(Generic[T]):
    '''
    Arbitrary generic.
    '''

    pass

# ....................{ FUNCTIONS                          }....................
def their_starry_domes(of_diamond_and_of_gold: ExpandAbove) -> ExpandAbove:
    '''
    Arbitrary function both accepting and returning a value annotated as a
    **subscripted generic type alias forward reference** (i.e.,
    :pep:`563`-postponed type hint referring to a global attribute that has yet
    to be defined whose value is a subscripted generic that *has* been defined),
    exercising an edge case in the :func:`beartype.peps.resolve_pep563`
    resolver.

    Raises
    ----------
    '''

    # Subscripted generic type alias, resolved to this global attribute that has
    # yet to be defined by the resolve_pep563() function called by the caller.
    ExpandAbove_resolved = their_starry_domes.__annotations__[
        'of_diamond_and_of_gold']

    # If this parameter violates this subscripted generic, raise an exception.
    die_if_unbearable(of_diamond_and_of_gold, ExpandAbove_resolved)

    # Return this parameter as is.
    return of_diamond_and_of_gold


ExpandAbove = ToAvariceOrPride[str]
'''
Arbitrary **subscripted generic type alias forward reference** (i.e.,
:pep:`563`-postponed type hint referring to a global attribute that has yet to
be defined whose value is a subscripted generic that *has* been defined),
'''
