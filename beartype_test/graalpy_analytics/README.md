# GraalPy Analytics & Documentation

This directory contains investigation scripts, profiling tools, and comprehensive documentation from GraalPy 25.0 compatibility work.

## 🚀 Quick Start

**For local GraalPy testing, always use**:
```bash
/home/srvadmin/graalpy-25.0.1/bin/graalpy
```

See **[GRAALPY_TESTING_INSTRUCTIONS.md](GRAALPY_TESTING_INSTRUCTIONS.md)** for complete testing guide.

## Purpose

This directory contains:
- **Investigation scripts** - Analyze GraalPy behavior differences
- **Profiling tools** - Measure performance characteristics
- **Bug reproducers** - Minimal test cases for issues
- **Comprehensive documentation** - Complete integration reports and guides

## Scripts

### Performance Analysis
- `profile_cache_decorator.py` - Proves @callable_cached is harmful (172% slower on GraalPy)

### Core Behavior Investigations
- `investigate_is_operator.py` - Deep dive into GraalPy's 'is' operator behavior
- `investigate_tuple_literal.py` - Why () literals have same ID but different identity
- `investigate_tuple_interning.py` - Tuple interning behavior comparison
- `investigate_module_names.py` - Why GraalPy uses _collections/_sre modules

### Bug Investigations
- `investigate_pytest_bug.py` - Async/protocol test failures in pytest context
- `test_async_pytest.py` - Minimal reproducer for pytest async bug
- `test_protocol_typevar_pytest.py` - Protocol TypeVar pytest failure
- **`GRAALPY_ASYNC_BUG_ANALYSIS.md`** ⭐ - **Complete analysis of pytest-asyncio Union annotation bug** (SOLVED!)

### Specific Test Cases
- `test_callable_empty_tuple.py` - Callable[[()], str] parameter extraction
- `test_method_type.py` - C-method type detection differences
- `test_protocol_graalpy.py` - Protocol isinstance behavior
- `test_tuple_identity.py` - Tuple identity semantics

## Key Findings

### 1. Cache Decorator is Harmful
**File:** `profile_cache_decorator.py`

Profiling revealed `@callable_cached` adds significant overhead:
- GraalPy: 172% SLOWER (343μs vs 126μs direct call)
- CPython: 71% SLOWER (117μs vs 69μs direct call)
- Module constant: 86% FASTER on GraalPy, 95% FASTER on CPython

**Action:** Use module-level constants instead of repeated cached calls.

### 2. GraalPy's 'is' Operator Mystery
**Files:** `investigate_is_operator.py`, `investigate_tuple_literal.py`

**Discovery:** GraalPy's `id()` returns a constant (0x1b) for ALL empty tuple instances, but `is` returns False.

**Root Cause:**
- GraalPy's `id()` returns logical identity hash (not memory address)
- All empty tuples get the same hash (0x1b)
- But they are DIFFERENT Java objects
- `is` operator compares Java object identity (different objects → False)

**Implication:** NEVER use `is` for tuple comparison; always use `==`.

### 3. Module Name Differences
**File:** `investigate_module_names.py`

**Discovery:** GraalPy exposes internal module names (_collections, _sre) instead of wrapper names.

**Root Cause:**
- CPython: C extensions with Python wrappers (public API uses wrapper names)
- GraalPy: Native implementation without C (exposes internal module names)
- Architectural difference, NOT a bug

### 4. pytest + GraalPy Interaction Bug
**File:** `GRAALPY_ASYNC_BUG_ANALYSIS.md` ⭐

**Status:** ✅ **FULLY ANALYZED**
- **Root Cause**: GraalPy bytecode compiler bug when compiling nested async functions with `Union` annotations in pytest-asyncio context
- **Error**: `TypeError: 'NoneType' object is not subscriptable`
- **Discovery**: NOT a beartype bug - happens without beartype too!
- **Workaround**: Use `from __future__ import annotations` (PEP 563)
- **Conclusion**: Current approach of skipping tests with `@skip_if_graalpy()` is correct

## Usage

These scripts are meant to be run directly, NOT as pytest tests:

```bash
# Run investigation
graalpy beartype_test/graalpy_analytics/investigate_is_operator.py

# Compare with CPython
python3 beartype_test/graalpy_analytics/investigate_is_operator.py
```

## Documentation

### Essential Guides
- **`GRAALPY_TESTING_INSTRUCTIONS.md`** ⭐ - **START HERE** for local GraalPy testing
  - Always use `/home/srvadmin/graalpy-25.0.1/bin/graalpy`
  - Quick commands, troubleshooting, best practices

### Comprehensive Reports
- **`GRAALPY_FINAL_SUMMARY.md`** - Complete integration summary with all code changes, test results, and recommendations
- **`GRAALPY_SUBPROCESS_INVESTIGATION.md`** - Deep dive into subprocess/claw hooks failures and the `.pth` file solution
- **`WHY_PTH_FILE_MISSING.md`** - Detailed explanation of why beartype wasn't installed on GraalPy
- **`INDEX.md`** - Complete documentation index with navigation

These documents provide:
- Root cause analysis for all compatibility issues
- Solutions and workarounds implemented
- Test statistics and compatibility assessment
- Recommendations for users, developers, and GraalPy team
- Step-by-step testing instructions

## Exclusions

This directory should be excluded from:
- pytest test discovery
- ruff/linting
- type checking
- Coverage reports

See `pytest.ini` and `pyproject.toml` for exclusion configurations.
