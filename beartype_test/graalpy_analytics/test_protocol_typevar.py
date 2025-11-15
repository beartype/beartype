#!/usr/bin/env python3
"""Test protocol with TypeVar."""

from abc import abstractmethod
from beartype import beartype
from beartype.typing import (
    Any,
    Protocol,
    TypeVar,
    runtime_checkable,
)

# Arbitrary type variable.
_T_co = TypeVar('_T_co', covariant=True)

# Arbitrary direct protocol subscripted by this type variable.
@runtime_checkable
class SupportsAbsToo(Protocol[_T_co]):
    __slots__: Any = ()

    @abstractmethod
    def __abs__(self) -> _T_co:
        pass

# Test isinstance
print(f"isinstance(-1, SupportsAbsToo): {isinstance(-1, SupportsAbsToo)}")
print(f"hasattr(-1, '__abs__'): {hasattr(-1, '__abs__')}")

# Test with beartype decorator
@beartype
def myabs(arg: SupportsAbsToo[_T_co]) -> _T_co:
    return abs(arg)

try:
    result = myabs(-1)
    print(f"\nmyabs(-1) = {result}")
    print("TEST PASSED!")
except Exception as e:
    print(f"\nERROR: {e}")
    print("TEST FAILED!")
