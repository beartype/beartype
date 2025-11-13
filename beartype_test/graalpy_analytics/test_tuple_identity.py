#!/usr/bin/env python3
"""Test empty tuple identity."""

# Test 1: Are literal empty tuples the same object?
t1 = ()
t2 = ()
print(f"() is (): {t1 is t2}")
print(f"id(t1): {id(t1)}, id(t2): {id(t2)}")

# Test 2: Does __args__ from Callable[[()], str] give the same empty tuple?
from collections.abc import Callable

hint = Callable[[()], str]
print(f"\nCallable[[()], str].__args__: {hint.__args__}")
print(f"hint.__args__[0]: {hint.__args__[0]}")
print(f"hint.__args__[0] is (): {hint.__args__[0] is ()}")
print(f"id(hint.__args__[0]): {id(hint.__args__[0])}, id(()): {id(())}")

# Test 3: Test with TUPLE_EMPTY pattern
TUPLE_EMPTY = ()
hint_param = hint.__args__[0]
print(f"\nTUPLE_EMPTY = ()")
print(f"hint_param is TUPLE_EMPTY: {hint_param is TUPLE_EMPTY}")
print(f"hint_param == TUPLE_EMPTY: {hint_param == TUPLE_EMPTY}")
print(f"hint_param == (): {hint_param == ()}")
