#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **class globals** (i.e., global constants describing various
well-known types).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._cave._cavefast import (
    EllipsisType,
    FunctionType,
    FunctionOrMethodCType,
    MethodBoundInstanceOrClassType,
    ModuleType,
    NoneType,
    NotImplementedType,
)

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ SETS                              }....................
TYPES_BUILTIN_FAKE = frozenset((
    EllipsisType,
    FunctionType,
    FunctionOrMethodCType,
    MethodBoundInstanceOrClassType,
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

# ....................{ TUPLES                            }....................
TYPES_BUILTIN_DECORATOR_DESCRIPTOR_FACTORY = (
    property,
    classmethod,
    staticmethod,
)
'''
Tuple of all **builtin descriptor factory decorators** (i.e., builtin types
which, when invoked as decorators on callables, wrap those callables in
uncallable descriptors).

These decorators are intentionally contained in a tuple rather than frozen set,
enabling descriptors created by these decorators to be efficiently detected via
the :func:`isinstance` builtin.
'''
