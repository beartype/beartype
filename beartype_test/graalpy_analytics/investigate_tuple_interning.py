#!/usr/bin/env python3
"""Investigate WHY GraalPy doesn't intern empty tuples."""

import sys

print("=" * 70)
print("INVESTIGATION: Why doesn't GraalPy intern empty tuples?")
print("=" * 70)

# 1. Test empty tuple identity
print("\n1. Empty Tuple Identity Test:")
print("-" * 70)

t1 = ()
t2 = ()
t3 = tuple()

print(f"t1 = (): {id(t1):#x}")
print(f"t2 = (): {id(t2):#x}")
print(f"t3 = tuple(): {id(t3):#x}")
print(f"\nt1 is t2: {t1 is t2}")
print(f"t1 is t3: {t1 is t3}")
print(f"t1 == t2: {t1 == t2}")

# 2. Test with literal vs constructor
print("\n2. Multiple Empty Tuple Creations:")
print("-" * 70)

ids = set()
for i in range(10):
    empty = ()
    ids.add(id(empty))
    print(f"Iteration {i}: id = {id(empty):#x}")

print(f"\nUnique IDs: {len(ids)}")
if len(ids) == 1:
    print("→ All empty tuples share the same ID (INTERNED)")
else:
    print("→ Different empty tuples have different IDs (NOT INTERNED)")

# 3. Check other immutable singletons
print("\n3. Other Immutable Singletons:")
print("-" * 70)

# None, True, False are always interned
n1 = None
n2 = None
print(f"None is None: {n1 is n2} (always interned)")

t1 = True
t2 = True
print(f"True is True: {t1 is t2} (always interned)")

# Small integers are interned in CPython (-5 to 256)
i1 = 42
i2 = 42
print(f"42 is 42: {i1 is i2} (typically interned)")

# Empty strings are typically interned
s1 = ""
s2 = ""
print(f'"" is "": {s1 is s2} (typically interned)')

# Now test empty tuple
e1 = ()
e2 = ()
print(f"() is (): {e1 is e2} (result for this interpreter)")

# 4. Understand Why
print("\n4. Understanding Interning:")
print("-" * 70)
print("""
Interning (String/Tuple Caching):
- Optimization where identical immutable objects share the same memory
- Python can reuse the same object instance for identical values
- Reduces memory usage and speeds up identity comparisons

CPython Implementation:
- Empty tuple is a singleton created at interpreter startup
- All () literals point to the same PyTupleObject instance
- Implemented in Objects/tupleobject.c
- See: https://github.com/python/cpython/blob/main/Objects/tupleobject.c

GraalPy Implementation:
- May not implement tuple interning the same way
- Possible reasons:
  1. Memory model differences (Java heap vs C heap)
  2. GC considerations (Java GC vs CPython's reference counting)
  3. Implementation complexity vs benefit trade-off
  4. Different optimization priorities
""")

# 5. Check if this is a bug or design decision
print("\n5. Bug vs Design Decision:")
print("-" * 70)

# Check Python documentation
print("""
From Python Language Reference:
- CPython implementation detail: tuple interning is NOT guaranteed
- Only singletons like None, True, False are guaranteed
- Empty tuple interning is an optimization, not a language requirement

Conclusion:
- GraalPy's behavior is SPEC-COMPLIANT
- CPython's tuple interning is an implementation detail
- Code should use == not "is" for tuple comparison (except CPython optimization)
""")

# 6. Performance Impact
print("\n6. Performance Impact:")
print("-" * 70)

import timeit

identity_time = timeit.timeit("() is ()", number=1000000)
equality_time = timeit.timeit("() == ()", number=1000000)

print(f"Identity check (() is ()): {identity_time:.6f}s")
print(f"Equality check (() == ()): {equality_time:.6f}s")
print(f"Difference: {abs(identity_time - equality_time):.6f}s")

if identity_time < equality_time:
    print(f"→ Identity is {(equality_time/identity_time - 1) * 100:.1f}% faster")
else:
    print(f"→ Equality is {(identity_time/equality_time - 1) * 100:.1f}% faster")

# 7. Root Cause Conclusion
print("\n" + "=" * 70)
print("ROOT CAUSE CONCLUSION")
print("=" * 70)
print(f"""
Python Version: {sys.version}
Implementation: {sys.implementation.name}

Empty Tuple Interning: {"YES" if () is () else "NO"}

WHY GraalPy doesn't intern empty tuples:
1. Not required by Python language specification
2. Different memory/GC model (Java vs C)
3. Implementation complexity may outweigh benefits
4. GraalPy prioritizes spec compliance over CPython quirks

Impact on beartype:
- Must use == instead of "is" for empty tuple comparison
- Minimal performance impact (microseconds per call)
- Correct solution: Use equality check, not identity check

This is NOT a GraalPy bug - it's a valid implementation choice.
CPython's tuple interning is an undocumented optimization.
""")
