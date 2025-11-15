import pytest
from typing import Union

async def test_simple_async():
    """Simple async test."""
    from beartype import beartype

    @beartype
    async def func(x: Union[str, int]) -> str:
        return str(x)

    result = await func("hello")
    assert result == "hello"
