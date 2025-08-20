#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide :pep:`484`- and :pep:`585`-compliant **generics** (i.e., subclasses of
both the standard :pep:`484`-compliant :class:`typing.Generic` superclass *and*
a :pep:`585`-compliant type hint factory subscripted by one or more type
parameters, exercising edge cases in unit tests requiring non-trivial generics).
'''

# ....................{ IMPORTS                            }....................
# Defer fixture-specific imports.
from beartype_test.a00_unit.data.pep.generic.data_pep484generic import (
    Nongeneric,
    Pep484GenericST,
)
from beartype_test.a00_unit.data.pep.generic.data_pep585generic import (
    Pep585SequenceU,
)
from beartype_test.a00_unit.data.pep.data_pep484 import (
    T,
    U,
)

# ....................{ PEP (484|585) ~ S, T               }....................
class Pep484585GenericSTSequenceU(
    # Order is *EXTREMELY* significant. Avoid modifying, please.
    list[bool],
    Pep484GenericST[int, T],
    Nongeneric,
    Pep585SequenceU,
):
    '''
    :pep:`484`- or :pep:`585`-compliant generic list parametrized by three
    unconstrained type variables.
    '''

    pass

# ....................{ PEP (484|585) ~ S, T, U            }....................
class Pep484585GenericIntTSequenceU(Pep484585GenericSTSequenceU[float]):
    '''
    :pep:`484`- or :pep:`585`-compliant generic list parametrized by two
    unconstrained type variables.
    '''

    pass


# Subclassing order is *EXTREMELY* significant. Avoid modifying, please.
class Pep484585GenericUUST(Pep585SequenceU, Pep484GenericST, list[U]):
    '''
    :pep:`484`- or :pep:`585`-compliant generic list parametrized by three
    unconstrained type variables, one of which is repeated twice across two
    different pseudo-superclasses at different hierarchical nesting levels.
    '''

    pass


class Pep484585GenericUIntT(Pep484585GenericUUST[U, int, T]):
    '''
    :pep:`585`-compliant generic list parametrized by two unconstrained type
    variables, one of which is repeated twice across two different
    pseudo-superclasses at different hierarchical nesting levels.
    '''

    pass
