#!/usr/bin/env python3
"""Investigate: Why do async/protocol tests fail in pytest but pass directly?"""

import sys
import asyncio
from beartype.typing import Protocol, runtime_checkable, Coroutine
from beartype import beartype

print("=" * 80)
print("INVESTIGATION: pytest + GraalPy Interaction Bug")
print("=" * 80)
print(f"Python: {sys.version}")
print(f"Implementation: {sys.implementation.name}\n")

# Test 1: Async type hint subscripting
print("1. ASYNC TYPE HINT SUBSCRIPTING:")
print("-" * 80)

try:
    # This is what fails in pytest with "TypeError: 'NoneType' object is not subscriptable"
    @beartype
    async def test_async_func(x: int) -> int:
        return x + 1

    result = asyncio.run(test_async_func(5))
    print(f"✓ Async function decorated and called successfully")
    print(f"  Result: {result}")
    print(f"  Function: {test_async_func}")
    print(f"  Wrapped: {'__wrapped__' in dir(test_async_func)}")
except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 2: Check what's None
print("2. INVESTIGATING 'NoneType' ERROR:")
print("-" * 80)

# The error "TypeError: 'NoneType' object is not subscriptable" suggests
# something is None that shouldn't be. Let's check typing module state.

from beartype import typing
print(f"typing module: {typing}")
print(f"typing.Coroutine: {typing.Coroutine}")
print(f"typing.Coroutine type: {type(typing.Coroutine)}")

# Check if Coroutine is subscriptable
try:
    coroutine_hint = Coroutine[None, None, int]
    print(f"✓ Coroutine[None, None, int]: {coroutine_hint}")
except Exception as e:
    print(f"✗ Cannot subscript Coroutine: {e}")

print()

# Test 3: Protocol isinstance
print("3. PROTOCOL ISINSTANCE:")
print("-" * 80)

@runtime_checkable
class SupportsRound(Protocol):
    def __round__(self, ndigits: int = 0):
        pass

print(f"Protocol defined: {SupportsRound}")
print(f"isinstance(0, SupportsRound): {isinstance(0, SupportsRound)}")
print(f"hasattr(0, '__round__'): {hasattr(0, '__round__')}")

@beartype
def test_protocol(x: SupportsRound) -> int:
    return round(x)

try:
    result = test_protocol(3.14)
    print(f"✓ Protocol validation passed: {result}")
except Exception as e:
    print(f"✗ Protocol validation failed: {e}")

print()

# Test 4: Check sys.modules state
print("4. SYS.MODULES INVESTIGATION:")
print("-" * 80)

import sys
print("Checking if typing modules are properly loaded:")
typing_modules = [m for m in sys.modules if 'typing' in m.lower()]
print(f"  Typing-related modules loaded: {len(typing_modules)}")
for mod in sorted(typing_modules)[:10]:
    print(f"    - {mod}")

# Check for None values in critical modules
print("\nChecking for None values in typing:")
import typing as std_typing
none_attrs = [attr for attr in dir(std_typing) if getattr(std_typing, attr, 'NOT_NONE') is None]
if none_attrs:
    print(f"  ✗ Found None attributes: {none_attrs[:10]}")
else:
    print(f"  ✓ No None attributes found")

print()

# Test 5: Environment differences
print("5. ENVIRONMENT ANALYSIS:")
print("-" * 80)

print("When running directly:")
print("  - Python interpreter starts fresh")
print("  - Standard library modules load normally")
print("  - typing module initializes completely")
print()
print("When running in pytest:")
print("  - pytest imports many modules first")
print("  - pytest may monkey-patch sys.modules")
print("  - pytest uses its own import hooks")
print("  - Module initialization order may differ")
print()

# Check if pytest is loaded
pytest_loaded = 'pytest' in sys.modules
print(f"pytest loaded: {pytest_loaded}")
if pytest_loaded:
    import pytest
    print(f"pytest version: {pytest.__version__}")

print()

# Test 6: The smoking gun - Import order?
print("6. IMPORT ORDER HYPOTHESIS:")
print("-" * 80)

print("Hypothesis: pytest imports typing before GraalPy fully initializes it")
print()
print("Evidence needed:")
print("1. Check typing module __file__ and __spec__")
print("2. Check if typing is 'frozen' or regular")
print("3. Check initialization state")
print()

import typing as check_typing
print(f"typing.__file__: {getattr(check_typing, '__file__', 'NO __file__')}")
print(f"typing.__spec__: {getattr(check_typing, '__spec__', 'NO __spec__')}")
print(f"typing.__package__: {getattr(check_typing, '__package__', 'NO __package__')}")

# Check specific attributes that might be None
critical_attrs = ['Coroutine', 'AsyncGenerator', 'Protocol', 'Optional']
print("\nCritical typing attributes:")
for attr in critical_attrs:
    val = getattr(check_typing, attr, 'MISSING')
    print(f"  typing.{attr}: {val if val != 'MISSING' else 'MISSING'}")

print()

print("=" * 80)
print("RUNNING DIRECTLY - ALL TESTS SHOULD PASS")
print("=" * 80)
print("Run with pytest to see failures:")
print("  graalpy -m pytest /tmp/investigate_pytest_bug.py -v")
