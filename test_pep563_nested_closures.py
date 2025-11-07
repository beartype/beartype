#!/usr/bin/env pypy3
"""
Test PEP 563 with nested closures - the exact test that's skipped.
"""

import sys
print(f"Python: {sys.implementation.name} {sys.version}")
print("=" * 80)

print("\nTEST: PEP 563 Nested Closures (from test_pep563_closure_nested)")
print("-" * 80)

try:
    from beartype_test.a00_unit.data.pep.pep563.data_pep563_poem import (
        get_minecraft_end_txt_closure_factory)

    # Assert that declaring a @beartype-decorated closure factory works under
    # PEP 563.
    print("Step 1: Call closure factory...")
    get_minecraft_end_txt_closure_outer = (
        get_minecraft_end_txt_closure_factory(player_name='Markus Persson'))
    assert callable(get_minecraft_end_txt_closure_outer)
    print(f"✅ Closure factory works: {get_minecraft_end_txt_closure_outer}")

    # Assert that declaring a @beartype-decorated closure declared by a
    # @beartype-decorated closure factory works under PEP 563.
    print("\nStep 2: Call outer closure...")
    get_minecraft_end_txt_closure_inner = get_minecraft_end_txt_closure_outer(
        stanza_len_min=65)
    assert callable(get_minecraft_end_txt_closure_inner)
    print(f"✅ Outer closure works: {get_minecraft_end_txt_closure_inner}")

    # Assert that this closure works under PEP 563.
    print("\nStep 3: Call inner closure...")
    minecraft_end_txt_inner = get_minecraft_end_txt_closure_inner(
        stanza_len_max=65, substr='thought')
    assert isinstance(minecraft_end_txt_inner, list)
    assert len(minecraft_end_txt_inner) == 1
    assert minecraft_end_txt_inner[0] == (
        'It is reading our thoughts as though they were words on a screen.')
    print(f"✅ Inner closure works: {minecraft_end_txt_inner[0]}")

    print("\n✅✅✅ PEP 563 NESTED CLOSURES WORK ON PYPY! ✅✅✅")

except Exception as e:
    print(f"❌ Failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
