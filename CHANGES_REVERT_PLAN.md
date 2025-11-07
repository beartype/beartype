# PyPy Changes: Revert Plan

## Goal
Revert ALL unnecessary changes compared to upstream `beartype/beartype`, keeping ONLY the minimum changes required for PyPy support.

## Files to Keep Unchanged (Documentation/Tests)
✅ Keep all analysis documentation:
- `PYPY_COMPATIBILITY.md`
- `REMAINING_PYPY_SKIPS_ANALYSIS.md`
- `NESTED_CLOSURES_ANALYSIS.md`
- `DESCRIPTOR_PYPY_FIX_SUMMARY.md`
- `COMPREHENSIVE_SKIP_ANALYSIS.md`
- `PYPY_UNION_FIX_SUMMARY.md`

✅ Keep all analysis test scripts:
- `deep_dive_enum.py`
- `deep_dive_functools_wraps.py`
- `deep_dive_pep563.py`
- `test_pep563_namedtuple.py`
- `test_pep563_nested_closures.py`
- `test_pypy_pep604.py`

✅ Keep test changes (skip markers, etc.)

## Source Code Changes Analysis

### KEEP (Essential for PyPy)

#### 1. `beartype/_data/hint/sign/datahintsignmap.py`
**Why:** PyPy's UnionType is in `_pypy_generic_alias` module, not `types`
**Change:** Conditional mapping of both `types.UnionType` and `_pypy_generic_alias.UnionType`
**Status:** ✅ ESSENTIAL - Keep as-is

#### 2. `beartype/_decor/_nontype/_decordescriptor.py`
**Why:** PyPy descriptors need try-except wrapper for safety
**Change:** Wrapped descriptor decoration in try-except
**Status:** ✅ ESSENTIAL - Keep as-is

#### 3. `beartype/_data/typing/datatyping.py`
**Why:** None - PEP 604 works on PyPy!
**Change:** Removed unnecessary PyPy conditional for PEP 604
**Status:** ✅ ALREADY FIXED - Keep current version (uses PEP 604 everywhere)

#### 4. `beartype_test/a00_unit/data/hint/pep/proposal/_data_pep604.py`
**Why:** None - PEP 604 works on PyPy!
**Change:** Re-enabled PEP 604 tests on PyPy
**Status:** ✅ ALREADY FIXED - Keep current version (tests enabled)

### REVERT (Unnecessary)

#### 1. `beartype/_cave/_cavefast.py` ❌
**Why:** PyPy HAS `types.UnionType`
**Current:** Try-except fallback for missing `types.UnionType`
**Action:** REVERT to upstream - direct assignment works fine
```python
# Upstream (correct):
HintPep604Type = _types.UnionType

# Current (unnecessary):
try:
    HintPep604Type = _types.UnionType
except AttributeError:
    HintPep604Type = type(int | str)
```

#### 2. Check other files for unnecessary changes...

Let me analyze the remaining files:

### Need to Check

#### `beartype/_data/cls/datacls.py`
- Check if changes are necessary

#### `beartype/_util/api/standard/utilfunctools.py`
- Check if changes are necessary

#### `beartype/_util/cache/utilcacheobjattr.py`
- Check if changes are necessary

#### `beartype/_util/func/arg/utilfuncargiter.py`
- Check if changes are necessary

#### `beartype/_util/func/arg/utilfuncarglen.py`
- Check if changes are necessary

#### `beartype/_util/func/utilfunccodeobj.py`
- Check if changes are necessary

#### `beartype/_util/py/utilpyinterpreter.py`
- Likely has PyPy detection helpers - probably needed

## Action Plan

1. ✅ Keep documentation (all `.md` files)
2. ✅ Keep test scripts (all `test_*.py` and `deep_dive_*.py`)
3. ✅ Keep `datahintsignmap.py` (essential PyPy UnionType mapping)
4. ✅ Keep `_decordescriptor.py` (essential try-except wrapper)
5. ✅ Keep current `datatyping.py` and `_data_pep604.py` (PEP 604 fixes)
6. ❌ REVERT `_cavefast.py` to upstream
7. ❓ CHECK remaining utility files one by one

## Next Steps

1. Review each remaining changed file
2. Determine if change is essential for PyPy
3. Revert unnecessary changes
4. Test that PyPy still works after reverts
5. Create final PR with minimal changes
