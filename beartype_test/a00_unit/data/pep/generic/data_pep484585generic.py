#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
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
    Pep585SequenceU)
from beartype_test.a00_unit.data.pep.pep484.data_pep484 import (
    T,
    U,
)

# ....................{ PEP (484|585) ~ T, U               }....................
class Pep484585GenericIntTSequenceU(
    # Order is *EXTREMELY* significant. Avoid modifying, please.
    list[bool],
    Pep484GenericST[int, T],
    Nongeneric,
    Pep585SequenceU,
):
    '''
    :pep:`484`- and :pep:`585`-compliant generic list parametrized by two
    unconstrained type variables:

    * :data:`.T`, parametrizing the :pep:`484`-compliant
      ``Pep484GenericST[int, T]`` subscripted generic pseudo-superclass.
    * :data:`.U`, parametrizing the :pep:`585`-compliant
      :class:`.Pep585SequenceU` unsubscripted generic superclass.
    '''

    pass


class Pep484585GenericIntFloatSequenceU(Pep484585GenericIntTSequenceU[float]):
    '''
    :pep:`484`- and :pep:`585`-compliant generic list parametrized by one
    unconstrained type variable: :data:`.U`, parametrizing the
    :pep:`585`-compliant :class:`.Pep585SequenceU` unsubscripted generic
    superclass.
    '''

    pass

# ....................{ PEP (484|585) ~ S, T, U            }....................
# Subclassing order is *EXTREMELY* significant. Avoid modifying, please.
class Pep484585SequenceUGenericSTListU(
    Pep585SequenceU, Pep484GenericST, list[U]):
    '''
    :pep:`484`- or :pep:`585`-compliant generic list parametrized by three
    unconstrained type variables, one of which is repeated twice across two
    different pseudo-superclasses at different hierarchical nesting levels.
    '''

    pass


class Pep484585SequenceUGenericIntTListU(
    Pep484585SequenceUGenericSTListU[U, int, T]):
    '''
    :pep:`585`-compliant generic list parametrized by two unbound type variables
    (i.e., :data:`.U` and :data:`.T`), one of which (i.e., :data:`.T`) is
    repeated twice across these two different pseudo-superclasses at different
    hierarchical nesting levels:

    * The :pep:`484`-compliant unsubscripted pseudo-superclass
      :class:`.Pep484GenericST`, where only the leading type variable :data:`.S`
      is bound to the concrete child hint :class:`int` subscripting the single
      pseudo-superclass subclassed by this generic list. The trailing type
      variable :data:`.T` remains unbound and thus free for subscripting by
      external subscriptions of this generic list.
    * The :pep:`585`-compliant subscripted pseudo-superclass ``list[U]``, where
      the type variable :data:`.U` subscripting that pseudo-superclass is bound
      to the type variable :data:`.T` subscripting the single pseudo-superclass
      subclassed by this generic list.
    '''

    pass
