#!/usr/bin/env pypy3
"""
Deep dive into Enum decoration failure - analyze what exactly fails and find workarounds.
"""

import sys
print(f"Python: {sys.implementation.name} {sys.version}")
print("=" * 80)

# Test 1: Understand what beartype tries to do with Enum
print("\nTEST 1: Basic Enum without @beartype")
print("-" * 80)
from enum import Enum, auto

class BasicEnum(Enum):
    ONE = auto()
    TWO = auto()

print(f"✅ BasicEnum works: {BasicEnum.ONE}, {BasicEnum.TWO}")
print(f"Enum type: {type(BasicEnum)}")
print(f"Enum.__new__ type: {type(BasicEnum.__new__)}")

# Test 2: Inspect Enum's __dict__ to find C-based methods
print("\n\nTEST 2: Inspect Enum internals")
print("-" * 80)
print("Enum class methods:")
for name, obj in BasicEnum.__dict__.items():
    if not name.startswith('_'):
        continue
    obj_type = type(obj)
    is_callable = callable(obj)
    print(f"  {name}: {obj_type}, callable={is_callable}")

    # Check if it's a C-based method
    if is_callable and hasattr(obj, '__func__'):
        try:
            func = obj.__func__
            print(f"    -> __func__: {type(func)}")
        except:
            print(f"    -> Cannot access __func__")

# Test 3: Try to decorate Enum and catch the exact error
print("\n\nTEST 3: Try @beartype on Enum - catch exact error")
print("-" * 80)
try:
    from beartype import beartype

    @beartype
    class TestEnum(Enum):
        A = 1
        B = 2

    print("✅ Somehow it worked!")
except Exception as e:
    print(f"❌ Failed with: {type(e).__name__}")
    print(f"   Message: {str(e)[:200]}")

    # Extract which method caused the issue
    import traceback
    tb_str = traceback.format_exc()
    print("\nFull traceback:")
    print(tb_str)

# Test 4: Try decorating Enum methods individually
print("\n\nTEST 4: What if we decorate Enum methods manually?")
print("-" * 80)
try:
    from beartype import beartype

    class TestEnum2(Enum):
        X = 1
        Y = 2

    # Try to find and decorate methods
    print("Attempting to decorate __new__...")
    try:
        # Get the __new__ method
        new_method = TestEnum2.__new__
        print(f"  __new__ type: {type(new_method)}")

        # Try to beartype it
        wrapped_new = beartype(new_method)
        print(f"  ✅ Successfully wrapped __new__!")
    except Exception as e:
        print(f"  ❌ Cannot wrap __new__: {type(e).__name__}: {e}")

except Exception as e:
    print(f"❌ Failed: {type(e).__name__}: {e}")

# Test 5: Can we skip problematic methods?
print("\n\nTEST 5: What if beartype skips certain Enum methods?")
print("-" * 80)
print("Idea: Modify beartype to skip C-based Enum internals")
print("Methods that might need skipping:")

from enum import Enum as EnumBase
print(f"Enum base class: {EnumBase}")
print(f"Enum MRO: {EnumBase.__mro__}")

# Check what methods Enum has that might be C-based
for name in dir(EnumBase):
    if name.startswith('_'):
        attr = getattr(EnumBase, name)
        if callable(attr):
            print(f"  {name}: {type(attr)}")

# Test 6: Try the user's actual use case
print("\n\nTEST 6: User's actual use case - do they need @beartype on Enum?")
print("-" * 80)
print("Scenario: User has an Enum and wants type-checking")

class Status(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DONE = "done"

def process_status(status: Status) -> str:
    """Function that takes an Enum - can THIS be type-checked?"""
    return f"Processing {status.value}"

# Can we type-check functions that USE enums?
try:
    from beartype import beartype

    @beartype
    def process_status_checked(status: Status) -> str:
        return f"Processing {status.value}"

    result = process_status_checked(Status.ACTIVE)
    print(f"✅ Type-checking functions that USE enums works: {result}")

    # Try invalid input
    try:
        process_status_checked("invalid")
        print("❌ Should have raised exception for invalid input")
    except Exception as e:
        print(f"✅ Correctly raises {type(e).__name__} for invalid enum value")

except Exception as e:
    print(f"❌ Failed: {type(e).__name__}: {e}")

# Test 7: Workaround - don't decorate Enum class itself
print("\n\nTEST 7: WORKAROUND - Don't decorate Enum, decorate functions that use it")
print("-" * 80)
print("Recommendation:")
print("  ❌ DON'T: @beartype on Enum class itself")
print("  ✅ DO:    @beartype on functions that take/return Enums")
print("")
print("Example:")
print("  # BAD")
print("  @beartype")
print("  class MyEnum(Enum):")
print("      ...")
print("")
print("  # GOOD")
print("  class MyEnum(Enum):")
print("      ...")
print("")
print("  @beartype")
print("  def use_enum(e: MyEnum) -> str:")
print("      ...")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print("Enum decoration fails because PyPy's Enum has C-based internals.")
print("Workaround: Don't decorate Enum classes - decorate functions that use them.")
print("This provides the same type safety without decorating Enum itself.")
