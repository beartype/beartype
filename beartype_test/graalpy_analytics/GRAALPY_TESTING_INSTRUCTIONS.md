# GraalPy Testing Instructions for Beartype Development

## Quick Start

### Use the Local GraalPy Installation

**Always use this interpreter for local GraalPy testing**:
```bash
/opt/graalpy/bin/python3
```

This installation:
- ✅ Has beartype installed in editable mode (`pip install -e .`)
- ✅ Has all test dependencies installed
- ✅ Has proper `.pth` file for subprocess tests
- ✅ Is ready to use immediately

### Quick Test Commands

```bash
# Run all tests
/opt/graalpy/bin/python3 -m pytest

# Run specific test file
/opt/graalpy/bin/python3 -m pytest beartype_test/a00_unit/a00_core/

# Run with verbose output
/opt/graalpy/bin/python3 -m pytest -v

# Run specific test
/opt/graalpy/bin/python3 -m pytest beartype_test/a00_unit/a60_check/a90_door/test_checkdoor_extraprocess.py::test_door_extraprocess_multiprocessing -v
```

---

## Why Use `/opt/graalpy/bin/python3`?

### Proper Setup ✅

The `/opt/graalpy` installation has been properly configured:

```bash
$ /opt/graalpy/bin/python3 -m pip show beartype
Location: /home/srvadmin/.local/lib/python3.12/site-packages
Editable project location: /media/srv-main-softdev/rnprivat/bitranox/beartype
```

**This means**:
1. ✅ Beartype installed in editable mode
2. ✅ `.pth` file created automatically
3. ✅ Subprocess tests work correctly
4. ✅ Changes to source immediately available

### System-Wide Installation

The `/opt/graalpy` installation is system-wide and permanent:

**Benefits**:
- ✅ Standard Python binary name (`python3`)
- ✅ Permanent installation location
- ✅ All dependencies properly installed
- ✅ Ready for production use

---

## Installation Status Verification

### Check Current Setup

```bash
# 1. Check if beartype is installed
/opt/graalpy/bin/python3 -m pip show beartype

# Should show:
# Name: beartype
# Editable project location: /media/srv-main-softdev/rnprivat/bitranox/beartype

# 2. Check if .pth file exists
ls -la /home/srvadmin/.local/lib/python3.12/site-packages/*.pth

# Should show:
# _beartype.pth

# 3. Verify sys.path includes beartype
/opt/graalpy/bin/python3 -c "import sys; print('/media/srv-main-softdev/rnprivat/bitranox/beartype' in sys.path)"

# Should print:
# True
```

---

## Setting Up a New GraalPy Installation

If you need to set up a fresh GraalPy installation:

### Step 1: Download and Extract

```bash
cd /tmp
wget https://github.com/oracle/graalpython/releases/download/graal-25.0.1/graalpy-25.0.1-linux-amd64.tar.gz
tar xf graalpy-25.0.1-linux-amd64.tar.gz
sudo mv graalpy-25.0.1-linux-amd64 /opt/graalpy
cd /media/srv-main-softdev/rnprivat/bitranox/beartype
```

### Step 2: Install Beartype in Editable Mode (CRITICAL!)

```bash
/opt/graalpy/bin/python3 -m pip install -e .
```

This single command:
- ✅ Creates `.pth` file in site-packages
- ✅ Makes beartype available to all subprocesses
- ✅ Allows testing changes without reinstall
- ✅ Enables proper development workflow

### Step 3: Install Test Dependencies

```bash
# Minimal dependencies (fast)
/opt/graalpy/bin/python3 -m pip install pytest typing-extensions

# Full dependencies (slow, includes optional integrations)
/opt/graalpy/bin/python3 -m pip install pytest typing-extensions pydantic attrs cattrs redis sqlalchemy typer click docutils
```

### Step 4: Verify Setup

```bash
# Test that beartype can be imported
/opt/graalpy/bin/python3 -c "import beartype; print(beartype.__file__)"

# Should print:
# /media/srv-main-softdev/rnprivat/bitranox/beartype/beartype/__init__.py

# Test subprocess functionality
/opt/graalpy/bin/python3 -m pytest beartype_test/a00_unit/a60_check/a90_door/test_checkdoor_extraprocess.py -v
```

---

## Common Testing Scenarios

### Running Full Test Suite

```bash
cd /media/srv-main-softdev/rnprivat/bitranox/beartype
/opt/graalpy/bin/python3 -m pytest
```

**Expected Results** (as of 2025-01):
- **Passing**: 383/420 (91.2%)
- **Failing**: 7 (async generator pytest bug)
- **Skipped**: 30 (version-specific, missing deps, async skip)

### Testing Specific Areas

```bash
# Core functionality
/opt/graalpy/bin/python3 -m pytest beartype_test/a00_unit/a00_core/

# Subprocess/multiprocessing tests
/opt/graalpy/bin/python3 -m pytest beartype_test/a00_unit/a60_check/a90_door/

# Claw (import hook) tests
/opt/graalpy/bin/python3 -m pytest beartype_test/a00_unit/a90_claw/

# Decorator tests
/opt/graalpy/bin/python3 -m pytest beartype_test/a00_unit/a70_decor/
```

### Running Skipped Tests

To see which tests are skipped on GraalPy:

```bash
/opt/graalpy/bin/python3 -m pytest -v | grep SKIPPED
```

### Debugging Specific Failures

```bash
# Run with full traceback
/opt/graalpy/bin/python3 -m pytest beartype_test/a00_unit/a90_claw/ -vv

# Run with pdb on failure
/opt/graalpy/bin/python3 -m pytest --pdb

# Run with prints shown
/opt/graalpy/bin/python3 -m pytest -s
```

---

## Investigation and Analysis Scripts

### Running Analytics Scripts

Scripts in this directory can be run directly:

```bash
# Profile cache decorator performance
/opt/graalpy/bin/python3 beartype_test/graalpy_analytics/profile_cache_decorator.py

# Investigate tuple identity
/opt/graalpy/bin/python3 beartype_test/graalpy_analytics/investigate_tuple_literal.py

# Compare with CPython
python3 beartype_test/graalpy_analytics/profile_cache_decorator.py
/opt/graalpy/bin/python3 beartype_test/graalpy_analytics/profile_cache_decorator.py
```

---

## Comparing CPython vs GraalPy

### Side-by-Side Testing

```bash
# Run test on CPython
python3 -m pytest beartype_test/a00_unit/a00_core/ -v

# Run same test on GraalPy
/opt/graalpy/bin/python3 -m pytest beartype_test/a00_unit/a00_core/ -v
```

### Performance Comparison

```bash
# Time CPython tests
time python3 -m pytest beartype_test/a00_unit/a00_core/

# Time GraalPy tests
time /opt/graalpy/bin/python3 -m pytest beartype_test/a00_unit/a00_core/
```

**Expected Performance**:
- CPython: ~0.3-0.5s per test file
- GraalPy: ~0.6-1.4s per test file (slower startup, similar execution)

---

## Troubleshooting

### Problem: `ModuleNotFoundError: No module named 'beartype'`

**Symptom**: Subprocess tests fail with this error.

**Cause**: Beartype not installed in editable mode.

**Solution**:
```bash
/opt/graalpy/bin/python3 -m pip install -e .
```

**Verify fix**:
```bash
/opt/graalpy/bin/python3 -c "import sys; print('/media/srv-main-softdev/rnprivat/bitranox/beartype' in sys.path)"
# Should print: True
```

### Problem: Tests hang or timeout

**Symptom**: Tests run indefinitely without completing.

**Known Issues**:
- Some async generator tests hang in pytest context (GraalPy bug)
- These are properly skipped with `@skip_if_graalpy()` decorator

**Solution**: Use timeout for individual tests:
```bash
timeout 60 /opt/graalpy/bin/python3 -m pytest beartype_test/a00_unit/a70_decor/a20_code/a60_pep/test_decorpep484585.py -v
```

### Problem: Different results between interpreters

**Expected**: Some tests behave differently on GraalPy due to implementation differences:
- Empty tuple identity (`() is ()` → False on GraalPy)
- Module names (`_collections`, `_sre` on GraalPy)
- Async generator pytest bug

**These are documented and handled** in the codebase with proper conditional logic and skip decorators.

---

## Environment Variables

### Useful Environment Variables

```bash
# Show Python paths
/opt/graalpy/bin/python3 -c "import sys; print('\n'.join(sys.path))"

# Check Python version
/opt/graalpy/bin/python3 --version

# Show pip version
/opt/graalpy/bin/python3 -m pip --version

# List installed packages
/opt/graalpy/bin/python3 -m pip list
```

### Setting PYTHONPATH (Not Recommended)

While you can set `PYTHONPATH`, it's **not reliable for subprocess tests**:

```bash
# Don't do this - not reliable
PYTHONPATH=/media/srv-main-softdev/rnprivat/bitranox/beartype /opt/graalpy/bin/python3 -m pytest

# Do this instead - use editable install
/opt/graalpy/bin/python3 -m pip install -e .
```

---

## Integration with CI/CD

The local setup mirrors the CI configuration in `.github/workflows/python_test.yml`:

```yaml
- name: Install beartype
  run: |
    if [[ "${{ matrix.python-version }}" == graalpy* ]]; then
      python3 -m pip install -e .
    fi
```

**Local testing should match CI behavior** to catch issues early.

---

## Quick Reference Card

### Essential Commands

```bash
# Use this interpreter
GRAALPY=/opt/graalpy/bin/python3

# Run all tests
$GRAALPY -m pytest

# Run specific test
$GRAALPY -m pytest beartype_test/a00_unit/a00_core/ -v

# Verify installation
$GRAALPY -m pip show beartype

# Check beartype in sys.path
$GRAALPY -c "import beartype; print(beartype.__file__)"

# Compare with CPython
python3 -m pytest beartype_test/a00_unit/a00_core/
$GRAALPY -m pytest beartype_test/a00_unit/a00_core/
```

### File Locations

- **GraalPy binary**: `/opt/graalpy/bin/python3`
- **Site-packages**: `/home/srvadmin/.local/lib/python3.12/site-packages/`
- **`.pth` file**: `/home/srvadmin/.local/lib/python3.12/site-packages/_beartype.pth`
- **Beartype source**: `/media/srv-main-softdev/rnprivat/bitranox/beartype/`
- **Analytics**: `/media/srv-main-softdev/rnprivat/bitranox/beartype/beartype_test/graalpy_analytics/`

---

## Additional Resources

- **[INDEX.md](INDEX.md)** - Complete documentation index
- **[GRAALPY_FINAL_SUMMARY.md](GRAALPY_FINAL_SUMMARY.md)** - Integration overview
- **[GRAALPY_SUBPROCESS_INVESTIGATION.md](GRAALPY_SUBPROCESS_INVESTIGATION.md)** - Subprocess investigation
- **[WHY_PTH_FILE_MISSING.md](WHY_PTH_FILE_MISSING.md)** - Explanation of `.pth` file issue
- **[README.md](README.md)** - Investigation scripts overview

---

## Best Practices

### ✅ DO

- Use `/opt/graalpy/bin/python3` for all local GraalPy testing
- Install beartype in editable mode (`pip install -e .`) for any new GraalPy setup
- Run tests from repository root directory
- Compare results with CPython to catch differences early
- Use investigation scripts to understand GraalPy behavior

### ❌ DON'T

- Don't use temporary GraalPy installations without proper setup
- Don't rely on PYTHONPATH for subprocess tests
- Don't run tests without verifying editable install
- Don't assume CPython behavior applies to GraalPy
- Don't skip verification steps

---

## Summary

**For local GraalPy testing, always use**:
```bash
/opt/graalpy/bin/python3
```

This installation is **properly configured** with:
- ✅ Editable beartype install
- ✅ Test dependencies
- ✅ `.pth` file for subprocesses
- ✅ Ready to use immediately

**No additional setup required!**
