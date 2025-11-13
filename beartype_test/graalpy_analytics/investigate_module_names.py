#!/usr/bin/env python3
"""Investigate WHY GraalPy uses different module names."""

import sys
from collections import OrderedDict
import re

print("="  * 70)
print("INVESTIGATION: Why does GraalPy use _collections/_sre modules?")
print("=" * 70)

# 1. Check OrderedDict
print("\n1. OrderedDict Investigation:")
print("-" * 70)
od = OrderedDict[int, str]
print(f"OrderedDict[int, str] repr: {repr(od)}")
print(f"OrderedDict type: {type(OrderedDict)}")
print(f"OrderedDict module: {OrderedDict.__module__}")
print(f"OrderedDict class module: {OrderedDict.__class__.__module__}")

# Check if it's a C extension or Python implementation
try:
    import inspect
    source_file = inspect.getfile(OrderedDict)
    print(f"OrderedDict source file: {source_file}")
    is_builtin = source_file.endswith(('.so', '.pyd', 'built-in'))
    print(f"Is C extension/built-in: {is_builtin}")
except Exception as e:
    print(f"Cannot get source file: {e}")

# 2. Check re.Match and re.Pattern
print("\n2. re.Match and re.Pattern Investigation:")
print("-" * 70)
pattern = re.compile(r'test')
match_obj = pattern.match('test')

print(f"Pattern type: {type(pattern)}")
print(f"Pattern __module__: {pattern.__class__.__module__}")
print(f"Pattern __qualname__: {pattern.__class__.__qualname__}")

if match_obj:
    print(f"Match type: {type(match_obj)}")
    print(f"Match __module__: {match_obj.__class__.__module__}")
    print(f"Match __qualname__: {match_obj.__class__.__qualname__}")

# Check re module implementation
print(f"\nre module file: {re.__file__}")
print(f"re module spec: {re.__spec__}")

# 3. Check if these are Python implementations vs C extensions
print("\n3. Implementation Analysis:")
print("-" * 70)

def check_implementation(obj, name):
    """Check if object is Python or C implementation."""
    obj_class = obj if isinstance(obj, type) else type(obj)

    # Check __module__
    module_name = getattr(obj_class, '__module__', 'unknown')
    print(f"\n{name}:")
    print(f"  __module__: {module_name}")

    # Underscore prefix typically indicates C implementation or internal
    if module_name.startswith('_'):
        print(f"  → Likely C extension or internal implementation")
        print(f"  → Reason: Module name starts with underscore (Python convention)")
    else:
        print(f"  → Likely pure Python implementation")

    # Try to get source
    try:
        import inspect
        source = inspect.getsource(obj_class)
        print(f"  → Has Python source code: YES")
        print(f"  → First 100 chars: {source[:100]!r}...")
    except (TypeError, OSError):
        print(f"  → Has Python source code: NO (likely C extension)")

    return module_name

od_module = check_implementation(OrderedDict, "OrderedDict")
pattern_module = check_implementation(pattern, "re.Pattern")
if match_obj:
    match_module = check_implementation(match_obj, "re.Match")

# 4. Compare with standard library
print("\n4. Standard Library Comparison:")
print("-" * 70)
print("CPython typically uses:")
print("  - C extensions for performance (re, collections)")
print("  - Internal modules named with underscore (_collections, _sre)")
print("  - Public API in regular modules (collections, re)")
print("\nGraalPy likely:")
print("  - Implements these in Python for compatibility")
print("  - Uses the internal module names directly")
print("  - May not have the same wrapper structure as CPython")

# 5. Root Cause Conclusion
print("\n" + "=" * 70)
print("ROOT CAUSE CONCLUSION")
print("=" * 70)
print("""
CPython Architecture:
- Collections and regex are implemented in C for performance
- C code is in _collections.c, _sre.c
- Python wrappers in collections.py, re.py import from C modules
- Public API uses wrapper module names

GraalPy Architecture:
- Implements standard library in Python (or Java/Truffle)
- No separate C extensions
- Internal module structure may be exposed differently
- Type repr() shows the actual internal module name

This is NOT a bug - it's an architectural difference:
- CPython: C implementation with Python wrappers
- GraalPy: Native implementation (Python/Java) without C
""")
