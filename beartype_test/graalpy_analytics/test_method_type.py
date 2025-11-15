#!/usr/bin/env python3
"""Test method type on GraalPy vs CPython."""

import re

pattern = re.compile(r'\b[Ff]ollow after\b')
sub_method = pattern.sub

print(f"Method: {sub_method}")
print(f"Type: {type(sub_method)}")
print(f"Type name: {type(sub_method).__name__}")
print(f"Type module: {type(sub_method).__module__}")

# Check if it's builtin_function_or_method
print(f"\nIs builtin_function_or_method? {isinstance(sub_method, type(len))}")
print(f"Type of len: {type(len)}")
print(f"Type of sub: {type(sub_method)}")
print(f"Are they the same? {type(len) == type(sub_method)}")
