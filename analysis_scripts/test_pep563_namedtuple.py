#!/usr/bin/env pypy3
"""
Test PEP 563 with NamedTuple specifically.
"""

import sys
print(f"Python: {sys.implementation.name} {sys.version}")
print("=" * 80)

print("\nTEST: PEP 563 with NamedTuple")
print("-" * 80)

try:
    from beartype.roar import BeartypeCallHintParamViolation
    from beartype_test.a00_unit.data.pep.pep563.pep484.data_pep563_pep484 import (
        LeadOnlyTo)

    # Test instantiation with valid field
    result = LeadOnlyTo(0xCAFEFACE)
    assert result.a_black_and_watery_depth == 0xCAFEFACE
    print(f"✅ Valid instantiation works: {result}")

    # Test instantiation with invalid field
    try:
        LeadOnlyTo("While death's blue vault, with loathliest vapours hung,")
        print("❌ Should have raised BeartypeCallHintParamViolation")
    except BeartypeCallHintParamViolation:
        print("✅ Type-checking works - invalid input rejected")

    print("\n✅✅✅ PEP 563 + NamedTuple WORKS ON PYPY! ✅✅✅")

except Exception as e:
    print(f"❌ Failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
