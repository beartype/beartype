#!/usr/bin/env python3
"""Test async function decoration with beartype on GraalPy."""

import asyncio
from typing import Union
from beartype import beartype

async def main():
    """Main async test function."""

    @beartype
    async def control_the_car(
        said_the: Union[str, int],
        biggest_greenest_bat: Union[str, float],
    ) -> Union[str, float]:
        '''Test async function with Union annotations.'''
        await asyncio.sleep(0)
        return said_the + biggest_greenest_bat

    result = await control_the_car("Hello ", "World")
    print(f"Result: {result}")
    assert result == "Hello World"
    print("Test passed!")

if __name__ == "__main__":
    asyncio.run(main())
