#!/usr/bin/env pypy3
"""
Deep dive into functools.wraps on builtin types - find workarounds.
"""

import sys
print(f"Python: {sys.implementation.name} {sys.version}")
print("=" * 80)

# Test 1: Understand what functools.wraps does
print("\nTEST 1: functools.wraps on a regular function")
print("-" * 80)
from functools import wraps

def original_func():
    """Original function"""
    return "original"

@wraps(original_func)
def wrapper_func():
    return "wrapped"

print(f"✅ Wrapping regular function works")
print(f"   wrapper_func.__name__ = {wrapper_func.__name__}")
print(f"   wrapper_func.__doc__ = {wrapper_func.__doc__}")

# Test 2: functools.wraps on builtin type
print("\n\nTEST 2: functools.wraps on builtin type (list)")
print("-" * 80)

@wraps(list)
def wrapped_list(*args, **kwargs):
    """Wrapper for list"""
    return list(*args, **kwargs)

print(f"wrapped_list type: {type(wrapped_list)}")
print(f"wrapped_list.__wrapped__: {getattr(wrapped_list, '__wrapped__', 'N/A')}")

# Check if it has __code__
if hasattr(wrapped_list, '__code__'):
    print(f"✅ Has __code__: {wrapped_list.__code__}")
else:
    print(f"❌ No __code__ attribute")

# Test 3: Try @beartype on functools.wraps(builtin)
print("\n\nTEST 3: @beartype on functools.wraps(builtin)")
print("-" * 80)
try:
    from beartype import beartype
    from beartype.typing import Any

    @beartype
    @wraps(list)
    def wrapped_list_beartype(*args: Any, **kwargs: Any):
        return list(*args, **kwargs)

    result = wrapped_list_beartype((1, 2, 3))
    print(f"✅ Somehow it worked: {result}")

except Exception as e:
    print(f"❌ Failed: {type(e).__name__}")
    print(f"   Message: {str(e)[:200]}")

# Test 4: What does beartype see?
print("\n\nTEST 4: What does beartype try to introspect?")
print("-" * 80)

@wraps(list)
def test_func(*args, **kwargs):
    return list(*args, **kwargs)

print(f"Function type: {type(test_func)}")
print(f"Has __code__: {hasattr(test_func, '__code__')}")
print(f"Has __wrapped__: {hasattr(test_func, '__wrapped__')}")

if hasattr(test_func, '__wrapped__'):
    wrapped = test_func.__wrapped__
    print(f"__wrapped__ type: {type(wrapped)}")
    print(f"__wrapped__ has __code__: {hasattr(wrapped, '__code__')}")

    # This is probably where beartype fails - it unwraps to 'list'
    # which is a C-based builtin

# Test 5: Can we intercept before beartype unwraps?
print("\n\nTEST 5: Prevent beartype from unwrapping to builtin")
print("-" * 80)
print("Idea: Remove __wrapped__ attribute before beartype sees it")

@wraps(list)
def test_func2(*args, **kwargs):
    return list(*args, **kwargs)

# Remove __wrapped__ to prevent beartype from unwrapping to C code
if hasattr(test_func2, '__wrapped__'):
    print(f"Original __wrapped__: {test_func2.__wrapped__}")
    delattr(test_func2, '__wrapped__')
    print("✅ Removed __wrapped__ attribute")

try:
    from beartype import beartype
    decorated = beartype(test_func2)
    result = decorated((1, 2, 3))
    print(f"✅ Works without __wrapped__: {result}")
except Exception as e:
    print(f"❌ Still fails: {type(e).__name__}: {e}")

# Test 6: Alternative - custom wrapper class
print("\n\nTEST 6: Alternative approach - custom wrapper class")
print("-" * 80)

class ListWrapper:
    """Custom wrapper for list that beartype can handle"""

    def __call__(self, *args, **kwargs):
        return list(*args, **kwargs)

try:
    from beartype import beartype

    wrapper = ListWrapper()

    @beartype
    def use_wrapper(*args: tuple):
        return wrapper(*args)

    result = use_wrapper((1, 2, 3))
    print(f"✅ Custom wrapper works: {result}")

except Exception as e:
    print(f"❌ Failed: {type(e).__name__}: {e}")

# Test 7: Real-world use case analysis
print("\n\nTEST 7: Real-world use case - why wrap builtin types?")
print("-" * 80)
print("Question: When do users actually need to wrap builtin types?")
print("")
print("Common scenarios:")
print("  1. Adding logging/instrumentation - Can use custom class instead")
print("  2. Modifying behavior - Should use subclass or custom class")
print("  3. Documentation/type hints - Just use type hints directly")
print("")
print("Conclusion: Wrapping builtin types with functools.wraps is rare")
print("and there are better patterns (subclassing, custom classes).")

# Test 8: Workaround recommendation
print("\n\nTEST 8: WORKAROUND - Use custom class instead of wraps(builtin)")
print("-" * 80)

from beartype import beartype
from typing import Any

# BAD: Don't wrap builtin types
print("❌ BAD:")
print("  @beartype")
print("  @wraps(list)")
print("  def my_list(*args, **kwargs):")
print("      return list(*args, **kwargs)")
print("")

# GOOD: Use custom class or just use the builtin
print("✅ GOOD Option 1 - Custom class:")

@beartype
class MyList:
    """Custom list-like class that can be type-checked"""

    def __init__(self, items: Any = None):
        self._list = list(items) if items else []

    def append(self, item: Any) -> None:
        self._list.append(item)

my_list = MyList([1, 2, 3])
print(f"   Works: {my_list._list}")

print("")
print("✅ GOOD Option 2 - Just use the builtin:")
print("  # No wrapper needed - just use list() directly")
print("  @beartype")
print("  def process_items(items: list) -> list:")
print("      return sorted(items)")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print("functools.wraps on builtin types fails because beartype unwraps to C code.")
print("Workaround: Use custom classes or subclasses instead of wrapping builtins.")
print("This pattern is rare in practice and alternatives exist.")
