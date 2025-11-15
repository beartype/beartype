# Why the `.pth` File Was Missing on GraalPy

## TL;DR

**CPython**: beartype installed in **editable mode** (`pip install -e .`) → `.pth` file created automatically
**GraalPy**: beartype **not installed** → no `.pth` file → subprocesses can't find beartype

## Investigation

### CPython Setup

```bash
$ pip show beartype
Name: beartype
Version: 0.22.6
Location: /home/srvadmin/venvs/pycharm314/lib/python3.14/site-packages
Editable project location: /media/srv-main-softdev/rnprivat/bitranox/beartype
```

**Key Detail**: `Editable project location` shows beartype is installed in **editable mode**.

### What is Editable Install?

When you run `pip install -e .` (editable install):

1. pip creates a `.egg-link` or `.pth` file in site-packages
2. File contains path to source directory
3. Python adds this path to `sys.path` on startup
4. Changes to source code immediately available (no reinstall needed)

**Example `.pth` file**:
```bash
$ cat /home/srvadmin/venvs/pycharm314/lib/python3.14/site-packages/_beartype.pth
/media/srv-main-softdev/rnprivat/bitranox/beartype
```

### GraalPy Setup

```bash
$ /tmp/graalpy-25.0.1-linux-amd64/bin/graalpy -m pip show beartype
WARNING: Package(s) not found: beartype
```

**beartype is NOT installed on GraalPy at all!**

### How Was Testing Done Then?

During initial testing, beartype was imported **because**:

1. Tests were run from repository directory
2. Python automatically adds current directory (`''`) to `sys.path[0]`
3. From repo directory: `import beartype` works (finds `beartype/` subdirectory)

**But when spawning subprocesses**:
1. Subprocess changes working directory (via `monkeypatch.chdir()`)
2. Current directory no longer contains beartype
3. GraalPy has no `.pth` file to add beartype path
4. Subprocess fails: `ModuleNotFoundError: No module named 'beartype'`

## Timeline of Discovery

### Initial Testing (Working)
```bash
# From repo directory
/tmp/graalpy-25.0.1-linux-amd64/bin/graalpy -m pytest ...
# ✅ Works! Current directory in sys.path
```

### Subprocess Tests (Failing)
```bash
# Test changes directory then spawns subprocess
cd beartype_test/a00_unit/data/door/extraprocess
graalpy -m data_door_multiprocessing
# ❌ Fails! beartype not in sys.path, no .pth file
```

### Why CPython Worked
```bash
# CPython has .pth file from editable install
# Subprocess inherits sys.path with beartype location
python3 -m data_door_multiprocessing
# ✅ Works! beartype in sys.path via .pth file
```

## Root Cause Analysis

### The Workflow Difference

**CPython Development Workflow**:
```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install in editable mode (standard practice)
pip install -e .

# 3. Run tests
pytest
# ✅ Works everywhere, including subprocesses
```

**GraalPy Testing Workflow** (as done initially):
```bash
# 1. Download GraalPy binary
wget https://.../graalpy-25.0.1-linux-amd64.tar.gz
tar xf graalpy-25.0.1-linux-amd64.tar.gz

# 2. Install test dependencies only
/tmp/graalpy-25.0.1-linux-amd64/bin/graalpy -m pip install pytest

# 3. Run tests from repo directory
cd /path/to/beartype
graalpy -m pytest
# ⚠️ Works for most tests, fails for subprocess tests
```

**Why the difference?**
- CPython: Used existing virtualenv with editable install (for normal development)
- GraalPy: Fresh installation, only test dependencies installed (to test compatibility)

### The Missing Step

GraalPy testing was missing:
```bash
/tmp/graalpy-25.0.1-linux-amd64/bin/graalpy -m pip install -e .
```

This single command would have:
1. Created `.pth` file in GraalPy's site-packages
2. Added beartype source path to sys.path
3. Made beartype available to all subprocesses
4. Fixed all 3 subprocess test failures immediately

## Implications

### This Explains Several Mysteries

**Mystery #1**: Why did most tests pass?
- **Answer**: Tests run from repo directory, current directory in sys.path

**Mystery #2**: Why did only subprocess tests fail?
- **Answer**: Subprocesses change directory, lose current directory access

**Mystery #3**: Why did CPython work without issues?
- **Answer**: Editable install created `.pth` file, subprocesses inherit sys.path

**Mystery #4**: Why was PYTHONPATH not sufficient?
- **Answer**: PYTHONPATH not reliably inherited by subprocesses, `.pth` is more robust

## Proper Testing Setup

### Recommended Workflow for GraalPy Testing

```bash
# 1. Download and extract GraalPy
wget https://github.com/oracle/graalpython/releases/download/graal-25.0.1/graalpy-25.0.1-linux-amd64.tar.gz
tar xf graalpy-25.0.1-linux-amd64.tar.gz

# 2. Install beartype in EDITABLE mode (crucial!)
/tmp/graalpy-25.0.1-linux-amd64/bin/graalpy -m pip install -e .

# 3. Install test dependencies
/tmp/graalpy-25.0.1-linux-amd64/bin/graalpy -m pip install pytest

# 4. Run tests
/tmp/graalpy-25.0.1-linux-amd64/bin/graalpy -m pytest
```

### Why Step #2 is Critical

The editable install (`pip install -e .`):
- ✅ Creates `.pth` file automatically
- ✅ Makes beartype available to all subprocesses
- ✅ Allows testing changes without reinstall
- ✅ Matches standard Python development practice
- ✅ Ensures consistent behavior with CPython

## Lesson Learned

### The Fundamental Issue

**Testing a package without installing it properly leads to incomplete testing.**

While `PYTHONPATH` or running from the source directory works for simple cases, it doesn't fully replicate how the package behaves when properly installed.

### Best Practice

**Always test with editable install**, even during development:
- Ensures subprocesses work correctly
- Matches how users will install the package
- Catches installation-related issues early
- Provides consistent test environment

### Why This Matters

Packages that spawn subprocesses (using `multiprocessing`, import hooks, etc.) rely on proper Python environment setup. Without editable install:
- Main process: Works (source directory in path)
- Subprocesses: Fail (no path to source)
- False negative: Looks like subprocess limitation, actually setup issue

## Conclusion

The `.pth` file wasn't "missing" - **it was never created because beartype wasn't installed on GraalPy**.

This was not:
- ❌ A GraalPy bug
- ❌ A GraalPy limitation
- ❌ A beartype issue
- ❌ A subprocess incompatibility

This was:
- ✅ An incomplete test environment setup
- ✅ Missing the standard editable install step
- ✅ Testing workflow difference between CPython and GraalPy

**Fix**: One command solves everything:
```bash
/tmp/graalpy-25.0.1-linux-amd64/bin/graalpy -m pip install -e .
```

## Recommendations Update

### For Documentation

Update subprocess investigation to clarify:
- Issue was **missing editable install**, not GraalPy limitation
- All subprocess functionality works correctly on GraalPy
- Proper installation setup is required for subprocess tests

### For CI/CD

Ensure editable install in GitHub Actions:
```yaml
- name: Install beartype for testing
  run: |
    if [[ "${{ matrix.python-version }}" == graalpy* ]]; then
      python3 -m pip install -e .
    fi
```

### For Local Testing

Document in contributor guide:
```bash
# For any Python interpreter (including GraalPy)
python -m pip install -e .
pytest
```

This is **standard Python development practice** - not a GraalPy-specific requirement!
