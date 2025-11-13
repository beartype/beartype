# GraalPy CI/CD Integration

## Overview

GraalPy 25.0.1 has been integrated into the beartype CI/CD test matrix. Tests run automatically on every push to `main` and on pull requests.

## Configuration

### GitHub Actions (`.github/workflows/python_test.yml`)

**Added to test matrix:**
```yaml
tox-env:
  - graalpy312-coverage

include:
  - { python-version: "graalpy-25.0",  tox-env: "graalpy312-coverage" }

exclude:
  # Test GraalPy only on Linux
  - platform: windows-latest
    tox-env: graalpy312-coverage
  - platform: macos-latest
    tox-env: graalpy312-coverage
```

**Why Linux only:**
- Primary supported platform for GraalPy
- Most stable for CI testing
- Windows/macOS support can be added later if needed

### Tox Configuration (`tox.ini`)

**Added to envlist:**
```ini
envlist = py{310,311,312,313,313t,314,314t,315,315t}-coverage,graalpy312-coverage

[testenv:graalpy312-coverage]
basepython = graalpy
```

## Test Execution

### Manual Testing

**Local test:**
```bash
# Ensure GraalPy is in PATH
export PATH=~/graalpy-25.0.1/bin:$PATH

# Run GraalPy tests
python3 -m tox -e graalpy312-coverage

# Or run all environments
python3 -m tox
```

**List all environments:**
```bash
python3 -m tox --listenvs
```

### CI/CD Execution

Tests run automatically on:
- Push to `main` branch
- Pull requests to `main` branch
- Manual workflow dispatch

**GitHub Actions workflow:**
1. Checks out repository
2. Installs GraalPy 25.0 via `actions/setup-python`
3. Installs dependencies via `uv`
4. Type-checks with `mypy`
5. Runs test suite via `tox`
6. Publishes coverage to Codecov

## Expected Results

### Test Status

**Expected:**
- ✅ **379 tests PASSED (90.2%)**
- ❌ **10 tests FAILED (2.4%)**
- ⊘ **31 tests SKIPPED (7.4%)**

### Known Failures

The 10 test failures are **GraalPy bugs**, not beartype issues:

**8 async/multiprocessing tests:**
- Fail with `TypeError: 'NoneType' object is not subscriptable`
- Pass when run directly (outside pytest)
- GraalPy + pytest interaction bug

**2 protocol tests:**
- `isinstance()` returns incorrect results in pytest context
- Pass when run directly
- GraalPy + pytest interaction bug

**All failures documented in:** `GRAALPY_STATUS.md`

## CI/CD Monitoring

### Where to Check Results

**GitHub Actions:**
1. Go to repository → Actions tab
2. Look for workflow named "tests"
3. Check for `[ubuntu-latest] Python graalpy-25.0 CI` job

**Expected CI output:**
```
name: "[ubuntu-latest] Python graalpy-25.0 CI"
status: ✅ PASS (with 10 expected failures)
duration: ~45 seconds
```

### Codecov Integration

Coverage reports are automatically published to Codecov:
- Report name: `ubuntu-latest-graalpy-25.0`
- Expected coverage: Similar to CPython (beartype has comprehensive tests)

## Maintenance

### Updating GraalPy Version

**To update to a newer GraalPy release:**

1. Update `.github/workflows/python_test.yml`:
   ```yaml
   - { python-version: "graalpy-25.1",  tox-env: "graalpy312-coverage" }
   ```

2. Update `GRAALPY_STATUS.md` with new version info

3. Re-test locally:
   ```bash
   # Install new GraalPy
   cd /tmp
   wget https://github.com/oracle/graalpython/releases/download/graal-25.1.0/graalpy-25.1.0-linux-amd64.tar.gz
   tar -xzf graalpy-25.1.0-linux-amd64.tar.gz

   # Test
   export PATH=/tmp/graalpy-25.1.0-linux-amd64/bin:$PATH
   python3 -m tox -e graalpy312-coverage
   ```

### Adding Windows/macOS Support

**To enable GraalPy tests on other platforms:**

1. Remove from `exclude` section in `.github/workflows/python_test.yml`:
   ```yaml
   exclude:
     # Remove these lines:
     # - platform: windows-latest
     #   tox-env: graalpy312-coverage
     # - platform: macos-latest
     #   tox-env: graalpy312-coverage
   ```

2. Verify `actions/setup-python` supports GraalPy on those platforms

3. Test thoroughly before enabling

## Troubleshooting

### CI Job Fails to Find GraalPy

**Issue:** `ERROR: InterpreterNotFound: graalpy`

**Solution:**
- Check if `actions/setup-python@v6` supports `graalpy-25.0`
- Try using exact version: `graalpy-25.0.1`
- Check GitHub Actions logs for Python installation errors

### Test Timeout

**Issue:** Tests timeout after 10 minutes

**Solution:**
- GraalPy tests typically complete in ~45 seconds
- If timeout occurs, check for:
  - Infinite loops in test code
  - Dependency installation issues
  - Platform-specific hangs

### More Failures Than Expected

**Issue:** More than 10 tests fail

**Solution:**
1. Check which additional tests failed
2. Verify failures don't occur on CPython
3. Run tests directly (outside pytest) to confirm GraalPy bug
4. Document new failures in `GRAALPY_STATUS.md`
5. Report to GraalPy team if confirmed bug

### Coverage Upload Fails

**Issue:** Codecov upload returns error

**Solution:**
- Check `CODECOV_TOKEN` secret is configured
- Verify coverage.xml is generated
- Check Codecov service status
- Note: CI doesn't fail if coverage upload fails (`fail_ci_if_error: false`)

## Resources

**GraalPy:**
- Releases: https://github.com/oracle/graalpython/releases
- Documentation: https://www.graalvm.org/python/
- Issues: https://github.com/oracle/graalpython/issues

**Beartype GraalPy Docs:**
- Status: `GRAALPY_STATUS.md`
- Deep Investigation: `GRAALPY_DEEP_INVESTIGATION.md`
- Investigation Scripts: `beartype_test/graalpy_analytics/`

**GitHub Actions:**
- setup-python: https://github.com/actions/setup-python
- Workflow Syntax: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions

## Version History

- **2025-01-13**: Initial GraalPy 25.0.1 integration (Linux only)
- Expected failures: 10 (GraalPy pytest bugs)
- Pass rate: 90.2%
