#!/usr/bin/env python3
"""Deep investigation: Why does GraalPy's 'is' return False for same ID objects?"""

import sys

print("=" * 80)
print("INVESTIGATION: GraalPy 'is' operator behavior")
print("=" * 80)
print(f"Python: {sys.version}")
print(f"Implementation: {sys.implementation.name}")
print()

# Test 1: Empty tuples
print("1. EMPTY TUPLES:")
print("-" * 80)
t1 = ()
t2 = ()
print(f"t1 = (): id={id(t1):#x}")
print(f"t2 = (): id={id(t2):#x}")
print(f"t1 is t2: {t1 is t2}")
print(f"id(t1) == id(t2): {id(t1) == id(t2)}")
print()

# Test 2: Check if object identity is maintained
print("2. OBJECT IDENTITY CONSISTENCY:")
print("-" * 80)
t = ()
print(f"t = (): id={id(t):#x}")
print(f"t is t: {t is t}")
print(f"id(t) == id(t): {id(t) == id(t)}")
print()

# Test 3: Test with different object types
print("3. OTHER SINGLETONS:")
print("-" * 80)

# None
n1 = None
n2 = None
print(f"None: id(n1)={id(n1):#x}, id(n2)={id(n2):#x}")
print(f"  n1 is n2: {n1 is n2}")
print(f"  id(n1) == id(n2): {id(n1) == id(n2)}")

# True
b1 = True
b2 = True
print(f"True: id(b1)={id(b1):#x}, id(b2)={id(b2):#x}")
print(f"  b1 is b2: {b1 is b2}")
print(f"  id(b1) == id(b2): {id(b1) == id(b2)}")

# Empty string
s1 = ""
s2 = ""
print(f"'': id(s1)={id(s1):#x}, id(s2)={id(s2):#x}")
print(f"  s1 is s2: {s1 is s2}")
print(f"  id(s1) == id(s2): {id(s1) == id(s2)}")

# Small integer
i1 = 42
i2 = 42
print(f"42: id(i1)={id(i1):#x}, id(i2)={id(i2):#x}")
print(f"  i1 is i2: {i1 is i2}")
print(f"  id(i1) == id(i2): {id(i1) == id(i2)}")

print()

# Test 4: Hypothesis - Maybe GraalPy creates copies?
print("4. HYPOTHESIS TEST: Object creation timing")
print("-" * 80)

# Create in same expression
result_expr = () is ()
print(f"() is () in expression: {result_expr}")

# Create separately, test immediately
t_a = ()
result_immediate = t_a is ()
print(f"t_a is () immediately: {result_immediate}")

# Store reference, test
t_ref = ()
t_test = t_ref
result_ref = t_ref is t_test
print(f"t_ref is t_test (same ref): {result_ref}")

print()

# Test 5: Check CPython's PyObject structure vs GraalPy
print("5. DEEP DIVE: How does 'is' work?")
print("-" * 80)
print("""
CPython 'is' operator:
- Compares PyObject* pointers directly
- If pointers are same → True
- If pointers differ → False
- id() returns the memory address

GraalPy 'is' operator possibilities:
1. Different object identity semantics (Java object identity?)
2. Lazy object creation (creates new object on each access?)
3. Different handling of tuple literals
4. Context-dependent object identity

Let's test which one it is:
""")

# Test 6: Check if it's context-dependent
print("6. CONTEXT TEST:")
print("-" * 80)

def test_in_function():
    """Test inside function scope."""
    f1 = ()
    f2 = ()
    print(f"  Inside function: id(f1)={id(f1):#x}, id(f2)={id(f2):#x}")
    print(f"  f1 is f2: {f1 is f2}")
    return f1, f2

class TestClass:
    """Test inside class."""
    c1 = ()
    c2 = ()

# Module level
m1 = ()
m2 = ()
print(f"Module level: id(m1)={id(m1):#x}, id(m2)={id(m2):#x}")
print(f"  m1 is m2: {m1 is m2}")

f1, f2 = test_in_function()

print(f"Class level: id(TestClass.c1)={id(TestClass.c1):#x}, id(TestClass.c2)={id(TestClass.c2):#x}")
print(f"  TestClass.c1 is TestClass.c2: {TestClass.c1 is TestClass.c2}")

print()

# Test 7: What if we use the same constant?
print("7. CONSTANT REUSE TEST:")
print("-" * 80)

EMPTY_TUPLE = ()
test1 = EMPTY_TUPLE
test2 = EMPTY_TUPLE
print(f"EMPTY_TUPLE constant: id={id(EMPTY_TUPLE):#x}")
print(f"test1 (from constant): id={id(test1):#x}")
print(f"test2 (from constant): id={id(test2):#x}")
print(f"test1 is EMPTY_TUPLE: {test1 is EMPTY_TUPLE}")
print(f"test2 is EMPTY_TUPLE: {test2 is EMPTY_TUPLE}")
print(f"test1 is test2: {test1 is test2}")

print()

# Test 8: bytecode analysis
print("8. BYTECODE INSPECTION:")
print("-" * 80)

import dis

def test_is_operator():
    return () is ()

print("Bytecode for '() is ()':")
dis.dis(test_is_operator)

print()

# Test 9: Check if it's about tuple creation
print("9. TUPLE CREATION INVESTIGATION:")
print("-" * 80)

# Using tuple() constructor
t_ctor1 = tuple()
t_ctor2 = tuple()
print(f"tuple() constructor:")
print(f"  id(t_ctor1)={id(t_ctor1):#x}, id(t_ctor2)={id(t_ctor2):#x}")
print(f"  t_ctor1 is t_ctor2: {t_ctor1 is t_ctor2}")

# Using literal
t_lit1 = ()
t_lit2 = ()
print(f"() literal:")
print(f"  id(t_lit1)={id(t_lit1):#x}, id(t_lit2)={id(t_lit2):#x}")
print(f"  t_lit1 is t_lit2: {t_lit1 is t_lit2}")

# Cross-test
print(f"Cross-test:")
print(f"  tuple() is (): {tuple() is ()}")
print(f"  id(tuple()) == id(()): {id(tuple()) == id(())}")

print()

# CONCLUSION
print("=" * 80)
print("CONCLUSION:")
print("=" * 80)

if () is ():
    print("✓ Empty tuples use identity comparison (CPython-like)")
else:
    print("✗ Empty tuples DON'T use identity comparison")
    print()
    print("Possible explanations:")
    print("1. GraalPy id() returns Java hashCode(), not memory address")
    print("2. GraalPy 'is' uses different identity semantics")
    print("3. Tuple literals create temporary objects that are GC'd")
    print("4. Java object identity != memory address identity")
    print()
    print("IMPLICATION:")
    print("- NEVER rely on 'is' for tuples in GraalPy")
    print("- Always use '==' for value comparison")
    print("- id() returning same value doesn't guarantee 'is' returns True")
