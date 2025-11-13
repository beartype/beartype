# GraalPy Analytics Scripts

This directory contains investigation and profiling scripts used during GraalPy compatibility development.

## Purpose

These scripts are NOT tests - they are analysis tools to:
- Investigate GraalPy behavior differences from CPython
- Profile performance characteristics
- Reproduce and analyze bugs
- Document root causes

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
**File:** `investigate_pytest_bug.py`

**Status:** Under investigation
- Async/protocol tests fail in pytest but pass directly
- Error: `TypeError: 'NoneType' object is not subscriptable`
- Suspected: Module initialization order or pytest import hooks

## Usage

These scripts are meant to be run directly, NOT as pytest tests:

```bash
# Run investigation
graalpy beartype_test/graalpy_analytics/investigate_is_operator.py

# Compare with CPython
python3 beartype_test/graalpy_analytics/investigate_is_operator.py
```

## Exclusions

This directory should be excluded from:
- pytest test discovery
- ruff/linting
- type checking
- Coverage reports

See `pytest.ini` and `pyproject.toml` for exclusion configurations.
