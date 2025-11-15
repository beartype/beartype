#!/usr/bin/env python3
"""Test protocol metaclass issue on GraalPy."""

def test_typingpep544_metaclass() -> None:
    '''Test protocol metaclass.'''

    from abc import abstractmethod
    from beartype.typing import (
        Any,
        Protocol,
        TypeVar,
        runtime_checkable,
    )
    from beartype.typing._typingpep544 import _CachingProtocolMeta

    _T_co = TypeVar('_T_co', covariant=True)

    @runtime_checkable
    class SupportsRoundFromScratch(Protocol[_T_co]):
        __slots__: Any = ()
        @abstractmethod
        def __round__(self, ndigits: int = 0) -> _T_co:
            pass

    supports_round: SupportsRoundFromScratch = 0

    print(f"isinstance(0, SupportsRoundFromScratch): {isinstance(supports_round, SupportsRoundFromScratch)}")
    print(f"hasattr(0, '__round__'): {hasattr(supports_round, '__round__')}")

    assert isinstance(supports_round, SupportsRoundFromScratch)
    assert issubclass(type(SupportsRoundFromScratch), _CachingProtocolMeta)

if __name__ == "__main__":
    test_typingpep544_metaclass()
    print("Test passed!")
