#!/usr/bin/env python3
"""Profile cache decorator benefit for is_python_graalpy()."""

import timeit
import platform

# Test 1: Direct call overhead
print("=" * 60)
print("Test 1: Direct platform.python_implementation() call")
print("=" * 60)

uncached_time = timeit.timeit(
    'platform.python_implementation() == "GraalVM"',
    setup='import platform',
    number=1000000
)
print(f"1,000,000 calls: {uncached_time:.6f}s")
print(f"Per call: {uncached_time * 1000000:.2f}ns")

# Test 2: Cached call overhead
print("\n" + "=" * 60)
print("Test 2: Cached is_python_graalpy() call")
print("=" * 60)

cached_time = timeit.timeit(
    'is_python_graalpy()',
    setup='from beartype._util.py.utilpyinterpreter import is_python_graalpy',
    number=1000000
)
print(f"1,000,000 calls: {cached_time:.6f}s")
print(f"Per call: {cached_time * 1000000:.2f}ns")

# Test 3: Module-level constant
print("\n" + "=" * 60)
print("Test 3: Module-level constant access")
print("=" * 60)

module_constant_time = timeit.timeit(
    '_IS_GRAALPY',
    setup='_IS_GRAALPY = True',
    number=1000000
)
print(f"1,000,000 calls: {module_constant_time:.6f}s")
print(f"Per call: {module_constant_time * 1000000:.2f}ns")

# Analysis
print("\n" + "=" * 60)
print("ANALYSIS")
print("=" * 60)

benefit_abs = uncached_time - cached_time
benefit_pct = (benefit_abs / uncached_time * 100) if uncached_time > 0 else 0

print(f"Uncached: {uncached_time:.6f}s")
print(f"Cached:   {cached_time:.6f}s")
print(f"Constant: {module_constant_time:.6f}s")
print(f"\nCache benefit vs uncached: {benefit_abs:.6f}s ({benefit_pct:.2f}%)")

constant_vs_cached = cached_time - module_constant_time
constant_vs_cached_pct = (constant_vs_cached / cached_time * 100) if cached_time > 0 else 0
print(f"Constant benefit vs cached: {constant_vs_cached:.6f}s ({constant_vs_cached_pct:.2f}%)")

# Recommendation
print("\n" + "=" * 60)
print("RECOMMENDATION")
print("=" * 60)

if benefit_pct > 50:
    print("✓ Cache decorator is BENEFICIAL (>50% improvement)")
elif benefit_pct > 10:
    print("⚠ Cache decorator provides MODEST benefit (10-50% improvement)")
elif benefit_pct > 1:
    print("⚠ Cache decorator provides MINIMAL benefit (1-10% improvement)")
else:
    print("✗ Cache decorator provides NO MEANINGFUL benefit (<1% improvement)")
    print("  Consider removing @callable_cached")

if constant_vs_cached_pct > 50:
    print(f"\n✓ Module-level constant would be {constant_vs_cached_pct:.1f}% faster than cache")
    print("  STRONGLY RECOMMEND: Use module-level constant instead")
elif constant_vs_cached_pct > 10:
    print(f"\n⚠ Module-level constant would be {constant_vs_cached_pct:.1f}% faster than cache")
    print("  RECOMMEND: Consider module-level constant for hot paths")

# Real-world frequency estimation
print("\n" + "=" * 60)
print("REAL-WORLD IMPACT")
print("=" * 60)

# Estimate: How often is this function called in typical beartype usage?
print("\nEstimated call frequency in typical beartype usage:")
print("- Module import: ~3-5 times")
print("- Type hint processing: ~10-100 times per decorated function")
print("- For 100 decorated functions: ~1,000-10,000 calls")
print("\nWith 10,000 calls:")
print(f"  Uncached total: {uncached_time * 10000 / 1000000:.6f}s")
print(f"  Cached total:   {cached_time * 10000 / 1000000:.6f}s")
print(f"  Constant total: {module_constant_time * 10000 / 1000000:.6f}s")
print(f"  Cache saves:    {benefit_abs * 10000 / 1000000:.6f}s per run")

if benefit_abs * 10000 / 1000000 < 0.001:
    print("\n✗ Savings < 1ms per typical run - NOT WORTH IT")
elif benefit_abs * 10000 / 1000000 < 0.01:
    print("\n⚠ Savings < 10ms per typical run - MARGINAL")
else:
    print("\n✓ Savings > 10ms per typical run - WORTHWHILE")
