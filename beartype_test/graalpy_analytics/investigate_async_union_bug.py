#!/usr/bin/env python3
"""Deep investigation: Why does Union fail in async functions with pytest?"""

import sys
print(f"Python: {sys.version}")
print(f"Implementation: {sys.implementation.name}")
print()

# Test 1: Can we use Union normally?
print("1. UNION TYPE HINT TEST:")
print("-" * 80)

from typing import Union
print(f"Union: {Union}")
print(f"Union[str, int]: {Union[str, int]}")

# Can we subscript Union?
try:
    hint = Union[str, int]
    print(f"✓ Union subscripting works: {hint}")
except Exception as e:
    print(f"✗ Union subscripting failed: {e}")

print()

# Test 2: Can we use Union in function signature?
print("2. UNION IN FUNCTION SIGNATURE:")
print("-" * 80)

def sync_func(x: Union[str, int]) -> Union[str, float]:
    return x

print(f"✓ Sync function with Union defined: {sync_func}")
print(f"  Annotations: {sync_func.__annotations__}")

print()

# Test 3: Can we use Union in ASYNC function signature?
print("3. UNION IN ASYNC FUNCTION SIGNATURE:")
print("-" * 80)

try:
    async def async_func(x: Union[str, int]) -> Union[str, float]:
        return x

    print(f"✓ Async function with Union defined: {async_func}")
    print(f"  Annotations: {async_func.__annotations__}")
except Exception as e:
    print(f"✗ Async function with Union failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 4: Can we use @beartype with Union in sync function?
print("4. BEARTYPE + UNION IN SYNC FUNCTION:")
print("-" * 80)

from beartype import beartype

try:
    @beartype
    def beartype_sync(x: Union[str, int]) -> Union[str, float]:
        return x

    print(f"✓ Beartype sync function defined: {beartype_sync}")
    result = beartype_sync("test")
    print(f"✓ Beartype sync function called: {result}")
except Exception as e:
    print(f"✗ Beartype sync function failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 5: Can we use @beartype with Union in ASYNC function?
print("5. BEARTYPE + UNION IN ASYNC FUNCTION:")
print("-" * 80)

try:
    @beartype
    async def beartype_async(x: Union[str, int]) -> Union[str, float]:
        return x

    print(f"✓ Beartype async function defined: {beartype_async}")

    import asyncio
    result = asyncio.run(beartype_async("test"))
    print(f"✓ Beartype async function called: {result}")
except Exception as e:
    print(f"✗ Beartype async function failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 6: Check typing module state
print("6. TYPING MODULE INSPECTION:")
print("-" * 80)

import typing
print(f"typing.Union: {typing.Union}")
print(f"typing.get_origin(Union[str, int]): {typing.get_origin(Union[str, int])}")
print(f"typing.get_args(Union[str, int]): {typing.get_args(Union[str, int])}")

# Check for None values
none_attrs = []
for attr in ['Union', 'Optional', 'Coroutine', 'AsyncGenerator']:
    val = getattr(typing, attr, 'MISSING')
    print(f"typing.{attr}: {val}")
    if val is None:
        none_attrs.append(attr)

if none_attrs:
    print(f"\n✗ WARNING: These typing attributes are None: {none_attrs}")
else:
    print(f"\n✓ All critical typing attributes are not None")

print()

# Test 7: The actual test pattern
print("7. REPRODUCING ACTUAL TEST PATTERN:")
print("-" * 80)

try:
    print("Defining async function with @beartype and Union...")

    @beartype
    async def control_the_car(
        said_the: Union[str, int],
        biggest_greenest_bat: Union[str, float],
    ) -> Union[str, float]:
        return said_the

    print(f"✓ Function defined: {control_the_car}")

    result = asyncio.run(control_the_car("test", 1.0))
    print(f"✓ Function executed: {result}")

except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print()

print("=" * 80)
print("CONCLUSION:")
print("=" * 80)
print("If this script passes when run directly but fails with pytest,")
print("then pytest is doing something to the typing module or beartype")
print("that causes Union subscripting to fail in async function definitions.")
print()
print("Run with pytest to see failure:")
print("  graalpy -m pytest beartype_test/graalpy_analytics/investigate_async_union_bug.py -xvs")
