#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable name globals** (i.e., global constants describing the
names of various well-known functions and methods).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ STRINGS ~ func                     }....................
FUNC_NAME_LAMBDA = '<lambda>'
'''
Default name of all **pure-Python lambda functions** (i.e., function declared
as a ``lambda`` expression embedded in a larger statement rather than as a
full-blown ``def`` statement).

Python initializes the names of *all* lambda functions to this lambda-specific
placeholder string on lambda definition.

Caveats
-------
**Usage of this placeholder to differentiate lambda from non-lambda callables
invites false positives in unlikely edge cases.** Technically, malicious third
parties may externally change the name of any lambda function *after* defining
that function. Pragmatically, no one sane should ever do such a horrible thing.
While predictably absurd, this is also the only efficient (and thus sane) means
of differentiating lambda from non-lambda callables. Alternatives require
AST-based parsing, which comes with its own substantial caveats, concerns,
edge cases, and false positives. If you must pick your poison, pick this one.
'''

# ....................{ STRINGS ~ init                     }....................
METHOD_NAME_INIT = '__init__'
'''
Name of all **pure-Python class initializers** (i.e., dunder method implicitly
called at instantiation time to initialize a pure-Python class just instantiated
by a call to the ``__new__()`` dunder method for that class).
'''

# ....................{ FROZENSETS                         }....................
METHOD_NAMES_DUNDER_BINARY = frozenset((
    '__add__',
    '__and__',
    '__cmp__',
    '__divmod__',
    '__div__',
    '__eq__',
    '__floordiv__',
    '__ge__',
    '__gt__',
    '__iadd__',
    '__iand__',
    '__idiv__',
    '__ifloordiv__',
    '__ilshift__',
    '__imatmul__',
    '__imod__',
    '__imul__',
    '__ior__',
    '__ipow__',
    '__irshift__',
    '__isub__',
    '__itruediv__',
    '__ixor__',
    '__le__',
    '__lshift__',
    '__lt__',
    '__matmul__',
    '__mod__',
    '__mul__',
    '__ne__',
    '__or__',
    '__pow__',
    '__radd__',
    '__rand__',
    '__rdiv__',
    '__rfloordiv__',
    '__rlshift__',
    '__rmatmul__',
    '__rmod__',
    '__rmul__',
    '__ror__',
    '__rpow__',
    '__rrshift__',
    '__rshift__',
    '__rsub__',
    '__rtruediv__',
    '__rxor__',
    '__sub__',
    '__truediv__',
    '__xor__',
))
'''
Frozen set of the unqualified names of all **binary dunder methods** (i.e.,
methods whose names are both prefixed and suffixed by ``__``, which the active
Python interpreter implicitly calls to perform binary operations on instances
whose first operands are instances of the classes declaring those methods).
'''
