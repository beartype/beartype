"""Test async with pytest to trigger the bug."""

import asyncio
from beartype import beartype

def test_async_in_pytest():
    """This should fail with 'NoneType' object is not subscriptable."""

    @beartype
    async def async_func(x: int) -> int:
        return x + 1

    result = asyncio.run(async_func(5))
    assert result == 6
