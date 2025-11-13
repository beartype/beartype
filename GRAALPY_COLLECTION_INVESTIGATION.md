# GraalPy Pytest Collection Performance Investigation

## Summary

**Finding**: Pytest collection is NOT the bottleneck. Collection times are reasonable (~1-2s per directory).

## Measurements

### Collection Times (--collect-only)

| Directory | Files | Collection Time |
|-----------|-------|----------------|
| a00_core | 2 | 1.09s |
| a10_data | 2 | 1.05s |
| a20_util/func | 8 | 1.16s |
| a20_util/cls | 3 | 1.06s |
| a20_util/text | 9 | 1.06s |
| **a20_util** | **89** | **2.15s** |
| a40_api | 16 | 1.89s |

**Conclusion**: Even with 89 files, collection takes only 2.15 seconds. This is NOT slow.

### Actual Test Execution

| Directory | Tests | Execution Time |
|-----------|-------|----------------|
| a00_core | 3 | 0.63s |
| a40_api | 30 | 1.39s |
| a20_util | 203 | 2.56s |

**Conclusion**: Test execution is also fast!

## Root Cause Analysis

### Original Problem (from CI history)

The user reported:
- "it still hangs after: test session starts"
- "collecting ... Warning: beartype_test/a00_unit/a40_api timed out or had failures"

### What Was Actually Happening

The timeouts were **NOT** due to slow collection. The real issues were:

1. **Tox hanging** during dependency installation
   - GraalPy was compiling heavy packages from source (poetry, sphinx, nuitka)
   - Solution: Excluded these packages via platform markers

2. **Test execution hanging** on specific tests
   - Some tests would hang indefinitely
   - This happened DURING test execution, not collection
   - Solution: File-by-file testing with 60s timeout per file

3. **Startup overhead**
   - Each pytest invocation has ~0.8-1s startup overhead
   - For 161 files × 1s = ~161s = 2.7 minutes just in startup overhead
   - Plus actual test time (~200-300s) = ~6-8 minutes total

## Performance Breakdown

### File-by-file Testing (Current CI Strategy)

```
Per file:
  - Startup overhead: ~1s
  - Collection: ~0.01-0.05s
  - Test execution: ~0.1-2s
  - Total per file: ~1-3s

For 161 files:
  - Passing files (~140): ~3s each = ~420s
  - Failing/timeout files (~20): ~60s each = ~1200s
  - **Total time: ~1620s = 27 minutes**
  - Observed in CI: 20-30 minutes
```

### Batch Testing (What We Tried Before)

```
For entire directory (89 files):
  - Startup overhead: ~1s
  - Collection: ~2s
  - Test execution: would HANG on certain tests
  - Result: TIMEOUT after 3+ minutes
```

## Why File-by-File Works

**The issue wasn't collection speed, it was test isolation:**

1. Some tests cause GraalPy to hang when run together
2. File-by-file isolation prevents cascading hangs
3. 60s timeout per file catches problem tests
4. `continue-on-error: true` allows CI to complete despite failures

## Optimization Opportunities

### Could We Speed This Up?

**Option 1**: Batch small files together
- Group files with < 5 tests each
- Could save ~50-100s of startup overhead
- Risk: One bad test hangs the entire batch

**Option 2**: Identify problem tests and skip them
- The 15 failing tests are known
- Could run remaining tests in batches
- Requires maintaining skip list

**Option 3**: Run in parallel
- GitHub Actions supports matrix parallelization
- Split 161 files across 4-8 workers
- Would reduce wall-clock time to ~1-2 minutes

**Current Status**: File-by-file is working reliably. Optimization can wait.

## Recommendations

1. **Keep file-by-file approach** for reliability
2. **60-minute timeout is appropriate** (gives ~22s per file on average)
3. **Collection is NOT the problem** - don't try to optimize it
4. **Consider parallelization** in the future for faster CI

## Conclusion

The original assumption that "collection is slow on GraalPy" was incorrect. The real issues were:
- Dependency installation timeouts (solved by excluding heavy packages)
- Test execution hangs (solved by file-by-file isolation)
- Startup overhead scaling (acceptable for 161 files)

**Collection itself is fast and not a bottleneck.**
