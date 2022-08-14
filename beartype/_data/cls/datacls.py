#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **class globals** (i.e., global constants describing various
well-known types).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
#FIXME: Export these types from "beartype.cave", please.
from beartype._cave._cavefast import (
    AsyncCoroutineCType,
    AsyncGeneratorCType,
    CallableCodeObjectType,
    CallableFrameType,
    ClassDictType,
    ClassType,
    ClosureVarCellType,
    EllipsisType,
    ExceptionTracebackType,
    FunctionType,
    FunctionOrMethodCType,
    GeneratorCType,
    MethodBoundInstanceDunderCType,
    MethodBoundInstanceOrClassType,
    MethodDecoratorBuiltinTypes,
    MethodUnboundClassCType,
    MethodUnboundInstanceDunderCType,
    MethodUnboundInstanceNondunderCType,
    MethodUnboundPropertyNontrivialCExtensionType,
    MethodUnboundPropertyTrivialCExtensionType,
    ModuleType,
    NoneType,
    NotImplementedType,
)

# ....................{ SETS                               }....................
TYPES_BUILTIN_FAKE = frozenset((
    AsyncCoroutineCType,
    AsyncGeneratorCType,
    CallableCodeObjectType,
    CallableFrameType,
    ClassDictType,
    ClosureVarCellType,
    EllipsisType,
    ExceptionTracebackType,
    FunctionType,
    FunctionOrMethodCType,
    GeneratorCType,
    MethodBoundInstanceDunderCType,
    MethodBoundInstanceOrClassType,
    MethodUnboundClassCType,
    MethodUnboundInstanceDunderCType,
    MethodUnboundInstanceNondunderCType,
    MethodUnboundPropertyNontrivialCExtensionType,
    MethodUnboundPropertyTrivialCExtensionType,
    ModuleType,
    NoneType,
    NotImplementedType,
))
'''
Frozen set of all **fake builtin types** (i.e., types that are *not* builtin
but which nonetheless erroneously masquerade as being builtin).

Like all non-builtin types, fake builtin types are globally inaccessible until
explicitly imported into the current lexical variable scope. Unlike all
non-builtin types, however, fake builtin types declare themselves to be
builtin. The standard example is the type of the ``None`` singleton: e.g.,

.. code-block:: python

   >>> f'{type(None).__module__}.{type(None).__name__}'
   'builtins.NoneType'
   >>> NoneType
   NameError: name 'NoneType' is not defined    # <---- this is balls

These inconsistencies almost certainly constitute bugs in the CPython
interpreter itself, but it seems doubtful CPython developers would see it that
way and almost certain everyone else would defend these edge cases.

We're *not* dying on that lonely hill. We obey the Iron Law of Guido.

See Also
----------
:data:`beartype_test.a00_unit.data.TYPES_BUILTIN_FAKE`
    Related test-time set. Whereas this runtime-specific set is efficiently
    defined explicitly by listing all non-builtin builtin mimic types, that
    test-specific set is inefficiently defined implicitly by introspecting the
    :mod:`builtins` module. While less efficient, that test-specific set serves
    as an essential sanity check on that runtime-specific set.
'''

# ....................{ TUPLES                             }....................
# Types of *ALL* objects that may be decorated by @beartype, intentionally
# listed in descending order of real-world prevalence for negligible efficiency
# gains when performing isinstance()-based tests against this tuple. These
# include the types of *ALL*...
TYPES_BEARTYPEABLE = (
    # Pure-Python unbound functions and methods.
    FunctionType,
    # Pure-Python classes.
    ClassType,
    # C-based builtin method descriptors wrapping pure-Python unbound methods,
    # including class methods, static methods, and property methods.
    MethodDecoratorBuiltinTypes,
)
'''
Tuple set of all **beartypeable types** (i.e., types of all objects that may be
decorated by the :func:`beartype.beartype` decorator).
'''
