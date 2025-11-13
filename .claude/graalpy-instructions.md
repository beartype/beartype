# GraalPy Compatibility Development Instructions

## Overview

This document provides instructions for developing GraalPy compatibility in the beartype project. This work is being done on the `graalpy` branch, which is synced with upstream `beartype/beartype` (not the `bitranox/main` branch with PyPy work).

## Branch Structure

- **graalpy** (working branch) - Synced with `upstream/main` (beartype/beartype)
- **main** - Contains PyPy compatibility work (separate)
- **pypy** - PyPy-specific work (separate)

**IMPORTANT:** The `graalpy` branch is independent from PyPy work. Do not merge or cherry-pick PyPy changes.

## GraalPy Test Results Summary

Initial test run (GraalPy 25.0.1):
- ✅ **370 tests PASSED (88.3%)**
- ❌ **19 tests FAILED (4.5%)**
- ⊘ **30 tests SKIPPED (7.2%)** (missing optional dependencies)

### Known Failure Categories

1. **Async/Coroutine Issues (5 failures)** - `TypeError: 'NoneType' object is not subscriptable`
   - Affects: `test_decor_async_coroutine`, `test_decor_async_generator`, `test_decor_contextlib_asynccontextmanager`, `test_decor_noop_redecorated_async`
   - Impact: Type subscripting in async contexts (e.g., `Union[str, int]` in async signatures)

2. **Type Detection Issues (3 failures)**
   - `OrderedDict` detection: GraalPy's `_collections.OrderedDict` not recognized
   - Protocol metaclass `isinstance` checks fail
   - Protocol with TypeVar fails instance checks

3. **Metadata Issue (1 failure)**
   - `beartype.meta.PYTHON_VERSION_MIN` is `None` instead of string

4. **Door API Type Checking (2 failures)**
   - `test_door_die_if_unbearable`, `test_door_is_bearable`

5. **Subprocess Tests (7 failures)**
   - All due to beartype not being installed in GraalPy's site-packages
   - Not core functionality issues, just test infrastructure

6. **Expected Failure (1 failure)**
   - `test_beartype` - needs investigation

## Development Guidelines

### 1. Using `is_python_graalpy()`

A cached function `is_python_graalpy()` has been created in `beartype/_util/py/utilpyinterpreter.py`.

**Usage pattern:**
```python
from beartype._util.py.utilpyinterpreter import is_python_graalpy

if is_python_graalpy():
    # GraalPy-specific workaround
    pass
else:
    # Standard implementation
    pass
```

**When to use:**
- Wrap GraalPy-specific workarounds
- Skip unsupported features on GraalPy
- Use alternative implementations for GraalPy

**When NOT to use:**
- Don't wrap code that should work on all Python implementations
- Don't create unnecessary branches if a universal fix exists

### 2. Code Style

Follow the existing beartype patterns:
- Use `@callable_cached` for expensive operations
- Add docstrings following beartype conventions
- Place GraalPy checks near PyPy checks when they address similar issues
- Keep workarounds minimal and well-documented

### 3. Documentation

For each GraalPy-specific change:
1. Add inline comments explaining WHY the workaround is needed
2. Reference the specific GraalPy issue or limitation
3. Include GraalPy version information if version-specific

Example:
```python
# GraalPy 25.0.1 reports OrderedDict as Pep585BuiltinSubscriptedUnknown
# instead of OrderedDict. Workaround: check for _collections.OrderedDict
if is_python_graalpy():
    # GraalPy-specific handling
    pass
```

## Testing Workflow

### 1. Environment Setup

GraalPy is installed at: `~/graalpy-25.0.1/`

Add to PATH:
```bash
export PATH=~/graalpy-25.0.1/bin:$PATH
```

### 2. Running Tests

**Single test:**
```bash
graalpy -m pytest beartype_test/path/to/test.py::test_function_name -v
```

**Test file:**
```bash
graalpy -m pytest beartype_test/path/to/test.py -v
```

**Full test suite:**
```bash
graalpy -m pytest beartype_test --tb=short -v
```

**Specific test category:**
```bash
graalpy -m pytest beartype_test/a00_unit/a70_decor/a20_code/a60_pep/ -v
```

### 3. Test Output

Save results for analysis:
```bash
graalpy -m pytest beartype_test --tb=short -v > /tmp/graalpy_test_results.txt 2>&1
```

### 4. Comparing with CPython

Always test fixes work on both GraalPy AND CPython:
```bash
# Test on GraalPy
graalpy -m pytest beartype_test/path/to/test.py -v

# Test on CPython
python3 -m pytest beartype_test/path/to/test.py -v
```

## Priority Issues to Fix

### High Priority (Core Functionality)

1. **Async type subscripting** (`TypeError: 'NoneType' object is not subscriptable`)
   - Files: `test_decorpep484585.py`, `test_decor_contextlib.py`, `test_decornoop.py`
   - Impact: All async function type checking

2. **OrderedDict type detection** (`test_get_hint_pep_sign`)
   - File: `test_a00_utilpepsign.py`
   - Impact: OrderedDict type hints not recognized

3. **Protocol metaclass issues** (`test_typingpep544_metaclass`)
   - File: `test_typingpep544.py`
   - Impact: Runtime checkable protocols fail

### Medium Priority

4. **Metadata issue** (`test_api_meta`)
   - File: `test_api_meta.py`
   - Issue: `beartype.meta.PYTHON_VERSION_MIN` is `None`

5. **Door API logic** (`test_door_die_if_unbearable`, `test_door_is_bearable`)
   - File: `test_checkdoor.py`
   - Impact: `beartype.door` API type checking

### Low Priority (Test Infrastructure)

6. **Subprocess tests** (7 failures)
   - Solution: Install beartype in GraalPy environment: `graalpy -m pip install -e .`

## Development Process

### Step-by-Step Workflow

1. **Pick a failing test from priority list**
2. **Investigate the failure:**
   - Run the specific test with GraalPy
   - Read the test code to understand what it's checking
   - Identify the root cause (GraalPy behavior vs expected behavior)

3. **Find the source code:**
   - Locate the beartype code being tested
   - Understand the current implementation

4. **Design the fix:**
   - Determine if a GraalPy-specific workaround is needed
   - Consider if a universal fix is possible
   - Check if similar patterns exist for PyPy

5. **Implement the fix:**
   - Add `is_python_graalpy()` check if needed
   - Write the workaround or fix
   - Add explanatory comments

6. **Test the fix:**
   - Verify the test passes on GraalPy
   - Verify the test still passes on CPython
   - Run related tests to check for regressions

7. **Document the change:**
   - Update inline comments
   - Note any limitations or caveats

8. **Commit:**
   - Write clear commit message
   - Reference the specific test fixed
   - Include GraalPy version if relevant

### Commit Message Format

```
GraalPy: Fix [test name or feature]

[Brief description of the issue]

Changes:
- [Specific change 1]
- [Specific change 2]

Testing:
- Verified on GraalPy 25.0.1
- Verified on CPython 3.12.8

[Optional: Notes about limitations or future work]
```

## Important Notes

### What Works Well on GraalPy

- Core type checking (sync functions)
- Most PEP 484/585 features
- Type introspection
- Caching mechanisms
- Utility functions
- Most protocols (non-generic)
- Dataclasses
- Generics and TypeVars

### What Needs Work

- Async function type subscripting
- OrderedDict detection
- Protocol metaclass checks
- Some Door API logic

### Don't Break These

- CPython compatibility (always test both)
- PyPy compatibility (separate branch, but be aware)
- Existing test suite (no regressions)
- Performance (use caching appropriately)

## Useful Commands

**Check GraalPy version:**
```bash
graalpy --version
```

**Check Python implementation:**
```bash
graalpy -c "from platform import python_implementation; print(python_implementation())"
```

**Test is_python_graalpy():**
```bash
graalpy -c "from beartype._util.py.utilpyinterpreter import is_python_graalpy; print(is_python_graalpy())"
```

**Find test files:**
```bash
find beartype_test -name "test_*.py" | grep <keyword>
```

**Search for specific functions:**
```bash
grep -r "def <function_name>" beartype/
```

## Getting Help

- Check similar PyPy workarounds in the codebase (search for `is_python_pypy()`)
- Review GraalPy documentation: https://www.graalvm.org/python/
- Check existing issues: https://github.com/oracle/graalpython/issues
- Refer to the test results report saved in `/tmp/graalpy_beartype_test_results.txt`

## Progress Tracking

Current status: Initial `is_python_graalpy()` function created and tested.

**Completed:**
- ✅ Created `is_python_graalpy()` function
- ✅ Added test for `is_python_graalpy()`
- ✅ Verified caching works correctly

**TODO:**
- [ ] Fix async type subscripting issues (5 tests)
- [ ] Fix OrderedDict type detection (1 test)
- [ ] Fix protocol metaclass issues (2 tests)
- [ ] Fix metadata issue (1 test)
- [ ] Fix Door API logic (2 tests)
- [ ] Investigate main beartype test failure (1 test)
- [ ] Install beartype in GraalPy for subprocess tests (7 tests)

## End Goal

Achieve 100% test pass rate on GraalPy while maintaining full compatibility with CPython and not breaking PyPy compatibility.
