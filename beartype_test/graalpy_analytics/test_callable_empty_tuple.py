#!/usr/bin/env python3
"""Test Callable[[()], str] parameter extraction."""

from collections.abc import Callable
from beartype._util.hint.pep.proposal.pep484585.pep484585callable import (
    get_hint_pep484585_callable_params,
    get_hint_pep484585_callable_return,
)

# Create the callable hint
hint = Callable[[()], str]

print(f"Hint: {hint}")
print(f"Hint repr: {repr(hint)}")
print(f"Hint __args__: {hint.__args__}")

# Get params and return
params = get_hint_pep484585_callable_params(hint)
ret = get_hint_pep484585_callable_return(hint)

print(f"Parameters: {params}")
print(f"Parameters repr: {repr(params)}")
print(f"Return: {ret}")
print(f"Return repr: {repr(ret)}")
