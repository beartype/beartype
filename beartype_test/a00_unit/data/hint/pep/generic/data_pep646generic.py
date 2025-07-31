#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide :pep:`646`-compliant **generics** (i.e., subclasses of some
combination of the standard :pep:`484`-compliant :class:`typing.Generic`
superclass *and/or* a :pep:`585`-compliant type hint factory subscripted by one
or more type parameters such that one or more of these type parameters is a
:pep:`646`-compliant unpacked type variable tuple, exercising edge cases in unit
tests requiring non-trivial generics).

Caveats
-------
Whereas most PEP-compliant data submodules define type hints unique to this test
suite, this :pep:`646`-compliant data submodule mostly defines type hints
intentionally copy-pasted from :pep:`646` itself. Why? Non-triviality.
:pep:`646` is non-trivial, encompassing such a wide variety of edge cases that
:pep:`646` itself is currently Python's longest :mod:`typing` standard and
possibly Python's longest standard period. Taming the uncommon beast that is
:pep:`646` requires a slavish attention to detail best achieved by explicitly
supporting all type hints exhibited in :pep:`646` itself.

As an aid to readability and maintainability, most commented headings of this
submodule are directly taken from section headings of :pep:`646` itself.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Generic

# ....................{ "Summary Examples"                 }....................
# PEP 646's leading "Summary Examples" section defines the core PEP
# 646-compliant "Array" generic subsequently referenced throughout PEP 646. All
# following code is copy-pasted directly from that section.
from typing import TypeVar, TypeVarTuple

DType = TypeVar('DType')
Shape = TypeVarTuple('Shape')

class Array(Generic[DType, *Shape]):
    '''
    :pep:`646`-compliant generic subclassing the standard :pep:`484`-compliant
    :class:`typing.Generic` superclass parametrized by a single
    :pep:`646`-compliant unpacked type variable tuple.

    Note that this class declaration slightly varies from that specified in PEP
    646. Type hints annotating methods self-referencing this class have
    necessarily been stringified to enable their evaluation if the active Python
    interpreter targets Python < 3.14.
    '''

    def __abs__(self) -> 'Array[DType, *Shape]': ...

    def __add__(self, other: 'Array[DType, *Shape]') -> 'Array[DType, *Shape]': ...
