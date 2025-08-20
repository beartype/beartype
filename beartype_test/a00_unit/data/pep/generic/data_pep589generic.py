#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide :pep:`589`-compliant **typed dictionary generics** (i.e., user-defined
types subclassing both the :pep:`589`-compliant :obj:`typing.TypedDict`
pseudo-superclass *and* the :pep:`484`-compliant :obj:`typing.Generic`
superclass, exercising edge cases in unit tests requiring non-trivial generics).
'''

# ....................{ IMPORTS                            }....................
# Defer fixture-specific imports.
from beartype.typing import (
    Generic,
    TypedDict,
)
from beartype_test.a00_unit.data.pep.data_pep484 import T

# ....................{ PEP 484 ~ usable : T               }....................
# Generics that are actually instantiable and usable as valid objects.

class Pep589484TypedDictT(TypedDict, Generic[T]):
    '''
    :pep:`589`-compliant **typed dictionary generic** (i.e., user-defined
    type subclassing both the :pep:`589`-compliant :obj:`typing.TypedDict`
    pseudo-superclass *and* the :pep:`484`-compliant :obj:`typing.Generic`
    superclass).
    '''

    # ....................{ FIELDS                         }....................
    key: T
    '''
    Arbitrary :pep:`589`-compliant typed dictionary key annotated by the same
    :pep:`484`-compliant type variable parametrizing this typed dictionary.
    '''
