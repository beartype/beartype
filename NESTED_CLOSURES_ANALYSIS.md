# PEP 563 Nested Closures Analysis

## Test Status: CORRECTLY SKIPPED ✅

The `test_pep563_closure_nested` test is correctly skipped on PyPy due to a real PyPy limitation.

---

## The Issue

### PyPy-Specific Problem
PyPy's `FrameType.f_locals` dictionary **omits local variables from distant parent callables** when those variables are **only accessed in annotations**.

### Code Example
```python
from __future__ import annotations
from typing import Union
from beartype import beartype

@beartype
def outer() -> Callable:
    IntLike = Union[float, int]  # Local type hint in outer function

    @beartype
    def middle() -> Callable:
        @beartype
        def inner(x: IntLike) -> int:  # Uses IntLike from outer
            return int(x)
        return inner
    return middle
```

### What Happens
1. **CPython**: `outer.IntLike` is accessible in `f_locals` when resolving `inner`'s annotations
2. **PyPy**: `outer.IntLike` is **NOT** in `f_locals` when resolving `inner`'s annotations
   - PyPy only includes it if used in function **body**, not just annotations
   - This breaks beartype's type hint resolution

---

## Test Results

### Test Script
```bash
pypy3 test_pep563_nested_closures.py
```

### Output
```
Step 1: Call closure factory...
✅ Closure factory works

Step 2: Call outer closure...
✅ Outer closure works

Step 3: Call inner closure...
❌ Failed: BeartypeCallHintForwardRefException: Forward reference "IntLike"
unimportable from module "beartype_test.a00_unit.data.pep.pep563.data_pep563_poem".
```

### Error Explanation
- Beartype tries to resolve `IntLike` forward reference
- PyPy's `f_locals` doesn't include `IntLike` because:
  - It's declared in the **grandparent** function (not direct parent)
  - It's **only used in annotations** (not in function body)
- Beartype cannot import `IntLike` from the module (it's local to a closure)
- Result: `BeartypeCallHintForwardRefException`

---

## Why This Happens

From the test file comments:

> PyPy developers failed to add local variables of lexical scopes declared by
> distant parent callables (i.e., callables that are NOT the direct parent of
> the lowest-level closure in question) when those local variables are ONLY
> accessed in annotations.

### Key Points
1. **Direct parent variables**: Work fine (e.g., `player_name` parameter)
2. **Distant parent variables**: Fail if annotation-only
3. **Body-accessed variables**: Work fine even from distant parents
4. **Annotation-only variables**: PyPy's f_locals computation omits them

---

## CPython Status

The test is ALSO skipped on CPython >= 3.10 due to different PEP 563 bugs:

```python
@skip_if_pypy311()
@skip_if_python_version_greater_than_or_equal_to('3.10.0')
def test_pep563_closure_nested() -> None:
```

Comment in code:
> FIXME: CPython is subtly broken with respect to "from __future__ import
> annotations" imports under Python >= 3.10. Until resolved, disable this.

---

## Impact

### What Works ✅
- Simple PEP 563 annotations
- Single-level closures with PEP 563
- Class-level type hints with PEP 563
- Module-level type hints with PEP 563
- NamedTuple with PEP 563

### What Fails on PyPy ❌
- **Nested closures** (3+ levels) with local type hints used only in annotations
- Specifically: grandparent → parent → child where grandparent defines type hint

### Workaround
Don't use local type aliases in deeply nested closures. Instead:

```python
# BAD - Fails on PyPy
@beartype
def outer() -> Callable:
    IntLike = Union[float, int]  # Local to outer

    @beartype
    def middle() -> Callable:
        @beartype
        def inner(x: IntLike) -> int:  # Can't find IntLike
            return int(x)

# GOOD - Use module-level type hints
IntLike = Union[float, int]  # Module-level

@beartype
def outer() -> Callable:
    @beartype
    def middle() -> Callable:
        @beartype
        def inner(x: IntLike) -> int:  # Works!
            return int(x)

# ALSO GOOD - Use typing directly
@beartype
def outer() -> Callable:
    @beartype
    def middle() -> Callable:
        @beartype
        def inner(x: Union[float, int]) -> int:  # Works!
            return int(x)
```

---

## Conclusion

**Verdict: Test correctly skipped** ✅

This is a **real PyPy limitation** with `FrameType.f_locals` in deeply nested closures with PEP 563. The skip is justified and should remain.

**Frequency**: Very rare edge case
- Requires 3+ levels of nesting
- Requires local type alias in distant parent
- Requires type alias used ONLY in annotations

**Most users will never encounter this issue.**
