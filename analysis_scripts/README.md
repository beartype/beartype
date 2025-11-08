# PyPy Analysis Scripts

This directory contains analysis and debugging scripts used during PyPy compatibility investigation. These are **NOT** part of the main test suite.

## Scripts

### PEP 604 Analysis
- `test_pypy_pep604.py` - Verified that PyPy 3.11+ fully supports PEP 604 union syntax

### PEP 563 Analysis
- `test_pep563_namedtuple.py` - Verified PEP 563 + NamedTuple works on PyPy
- `test_pep563_nested_closures.py` - Identified PEP 563 nested closures limitation

### Deep Dive Analysis
- `deep_dive_enum.py` - Analyzed Enum decoration limitations and documented workarounds
- `deep_dive_functools_wraps.py` - Analyzed functools.wraps on builtins and documented workarounds
- `deep_dive_pep563.py` - Comprehensive PEP 563 testing on PyPy

## Purpose

These scripts were used to:
1. Identify specific PyPy compatibility issues
2. Test workarounds and solutions
3. Document behavior differences between CPython and PyPy

## Results

All findings have been documented in:
- `REMAINING_PYPY_SKIPS_ANALYSIS.md`
- `MINIMAL_PYPY_CHANGES_FINAL.md`
- `COMPREHENSIVE_SKIP_ANALYSIS.md`

## Note

These scripts should NOT be run as part of the regular test suite. They were used during investigation only.
