#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide :pep:`695`-compliant **generics** (i.e., subclasses of another
PEP-compliant generic superclass, implicitly parametrized by one or more
PEP-compliant type parameters declared with :pep:`695`-compliant type parameter
syntax, validating edge cases in unit tests requiring these generics).
'''

# ....................{ PEP 695 : S, T                     }....................
class Pep695GenericST[S, T]:
    '''
    :pep:`695`-compliant generic implicitly subclassing the root
    :class:`typing.Generic` superclass implicitly parametrized by two type
    variables, declared with :pep:`695`-compliant syntax.
    '''

    pass

# ....................{ PEP 695 : S, T, U                  }....................
class Pep695GenericSTToUU[S, T, U](Pep695GenericST[S, U]):
    '''
    :pep:`695`-compliant generic subclass implicitly parametrized by three type
    variables declared with :pep:`695`-compliant syntax, but inheriting a
    :pep:`484`-compliant generic superclass subscripted by only two of those
    type variables **non-sequentially** (i.e., only the first type variable
    ``S`` and third type variable ``U`` parametrizing this subclass, thus
    excluding the second type variable ``T`` also parametrizing this subclass).

    See Also
    --------
    :class:`.beartype_test.a00_unit.data.pep.generic.data_pep484generic.Pep484GenericSTToUU`
        Further details.
    '''

    pass
