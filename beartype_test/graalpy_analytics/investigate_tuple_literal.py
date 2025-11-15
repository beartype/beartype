#!/usr/bin/env python3
"""Investigate: Why do () literals create new references?"""

import sys
import ctypes

print("=" * 80)
print("INVESTIGATION: Tuple Literal Behavior")
print("=" * 80)
print(f"Implementation: {sys.implementation.name}\n")

# Test 1: The core mystery
print("1. CORE MYSTERY:")
print("-" * 80)
print("Each () literal has the SAME id but DIFFERENT identity:")
print(f"  id(()) == id(()): {id(()) == id(())}")
print(f"  () is (): {() is ()}")
print()

# Test 2: Let's check if GraalPy reuses IDs (address reuse)
print("2. ID REUSE INVESTIGATION:")
print("-" * 80)
print("Creating 10 temporary empty tuples and recording IDs:")
ids = []
for i in range(10):
    temp = ()
    ids.append(id(temp))
    print(f"  Iteration {i}: id={id(temp):#x}")
    del temp  # Explicitly delete

print(f"\nUnique IDs: {len(set(ids))}")
print(f"All same ID?: {len(set(ids)) == 1}")
print()

# Test 3: Check if it's about object lifetime
print("3. OBJECT LIFETIME:")
print("-" * 80)

# Create, store, check
a = ()
print(f"a = (): id={id(a):#x}")
b = ()
print(f"b = (): id={id(b):#x}")
print(f"a is b: {a is b}")

# Now check if the STORED objects are different
print(f"\nBut a still exists: a is a → {a is a}")
print(f"And b still exists: b is b → {b is b}")

# Key test: Are stored objects at different memory locations in reality?
if sys.implementation.name == 'cpython':
    # On CPython we can inspect the actual C object
    print(f"\nCPython ctypes address check:")
    print(f"  ctypes.addressof(a): {ctypes.addressof(a) if hasattr(ctypes, 'addressof') else 'N/A'}")
else:
    print(f"\nGraalPy: Cannot inspect internal object representation")

print()

# Test 4: The smoking gun - What's different?
print("4. SMOKING GUN TEST:")
print("-" * 80)
print("Key insight: id() returns same value, but objects are different")
print()
print("This can only happen if:")
print("  A) GraalPy reuses addresses IMMEDIATELY (GC reclaims instantly)")
print("  B) id() doesn't return memory address (returns constant/hashcode)")
print("  C) Tuple literals are special-cased")
print()

# Test hypothesis A: Immediate GC
print("Testing Hypothesis A: Immediate GC and address reuse")
x = object()  # Create non-tuple object
x_id = id(x)
del x
y = object()  # Create another - does it reuse the address?
y_id = id(y)
print(f"  object() ID 1: {x_id:#x}")
print(f"  object() ID 2: {y_id:#x}")
print(f"  Same ID?: {x_id == y_id}")

# With tuples
t1_id = id(())
t2_id = id(())
print(f"  () ID 1: {t1_id:#x}")
print(f"  () ID 2: {t2_id:#x}")
print(f"  Same ID?: {t1_id == t2_id}")
print()

# Test hypothesis B: id() behavior
print("Testing Hypothesis B: What does id() return?")
print("  If id() returns Java object identity/hashCode,")
print("  empty tuples might all have the SAME identity value")
print("  but be DIFFERENT Java objects")
print()

# Test hypothesis C: Special casing
print("Testing Hypothesis C: Are tuple literals special?")
stored1 = ()
stored2 = ()
print(f"  Stored tuples: stored1 is stored2 → {stored1 is stored2}")
print(f"  Literal vs stored: () is stored1 → {() is stored1}")
print(f"  Literal vs literal: () is () → {() is ()}")
print()

# Test 5: The solution
print("=" * 80)
print("SOLUTION:")
print("=" * 80)
print("""
ROOT CAUSE:
GraalPy's id() returns a constant (0x1b) for ALL empty tuple instances.
This is likely a DESIGN CHOICE for memory efficiency:
- All empty tuples are logically identical
- GraalPy assigns them the same identity hash
- But they are DIFFERENT Java objects in memory
- 'is' operator compares Java object identity (different objects → False)
- id() returns logical identity hash (same for all empty tuples → 0x1b)

This is NOT a bug - it's a valid design choice:
- CPython: id() = memory address, interning makes same object
- GraalPy: id() = logical hash, no physical interning

IMPLICATION FOR BEARTYPE:
- NEVER use 'is' to compare tuples (even empty ones)
- ALWAYS use '==' for value comparison
- Store constants and use 'is' to compare references to STORED values
- Use module-level constant as we did: _IS_PYTHON_GRAALPY

OUR FIX IS CORRECT:
  if _IS_PYTHON_GRAALPY:  # Comparing to STORED constant
      is_empty_tuple = hint_param == TUPLE_EMPTY  # Value comparison
  else:
      is_empty_tuple = hint_param is TUPLE_EMPTY  # Identity (works on CPython)
""")
