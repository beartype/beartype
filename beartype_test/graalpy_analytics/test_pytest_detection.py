#!/usr/bin/env python3
"""Test if we can detect pytest context and work around the bug."""

import sys

print("=" * 80)
print("INVESTIGATION: Can we detect pytest context?")
print("=" * 80)

# Method 1: Check sys.modules
pytest_in_modules = 'pytest' in sys.modules or '_pytest' in sys.modules
print(f"1. pytest in sys.modules: {pytest_in_modules}")

# Method 2: Check for pytest-specific attributes
has_pytest_current_test = hasattr(sys, '_called_from_test')
print(f"2. sys._called_from_test exists: {has_pytest_current_test}")

# Method 3: Check PYTEST_CURRENT_TEST environment variable
import os
pytest_env = 'PYTEST_CURRENT_TEST' in os.environ
print(f"3. PYTEST_CURRENT_TEST env var: {pytest_env}")
if pytest_env:
    print(f"   Value: {os.environ['PYTEST_CURRENT_TEST']}")

# Method 4: Check if running under pytest
try:
    import pytest
    running_under_pytest = True
    print(f"4. pytest module importable: True")
    print(f"   pytest.version: {pytest.__version__}")
except ImportError:
    running_under_pytest = False
    print(f"4. pytest module importable: False")

# Method 5: Check stack frames for pytest
import inspect
stack = inspect.stack()
has_pytest_in_stack = any('pytest' in str(frame.filename) for frame in stack)
print(f"5. pytest in call stack: {has_pytest_in_stack}")

print()
print("=" * 80)
print("CONCLUSION:")
print("=" * 80)

if pytest_in_modules or pytest_env or has_pytest_in_stack:
    print("✓ PYTEST CONTEXT DETECTED")
    print()
    print("We CAN detect pytest context!")
    print()
    print("POTENTIAL WORKAROUND:")
    print("- Detect if running under pytest on GraalPy")
    print("- Skip problematic decorations")
    print("- Or use alternative code paths")
    print()
    print("Example:")
    print("```python")
    print("from beartype._util.py.utilpyinterpreter import is_python_graalpy")
    print("import sys")
    print()
    print("_IN_PYTEST = 'pytest' in sys.modules")
    print()
    print("if is_python_graalpy() and _IN_PYTEST:")
    print("    # Use safe fallback")
    print("    return func  # Don't decorate")
    print("else:")
    print("    # Normal decoration")
    print("    return beartype(func)")
    print("```")
else:
    print("✗ PYTEST CONTEXT NOT DETECTED")
    print()
    print("Cannot reliably detect pytest - workaround not feasible")

print()
print("Run this with pytest to see if detection works:")
print("  graalpy -m pytest beartype_test/graalpy_analytics/test_pytest_detection.py -xvs")
