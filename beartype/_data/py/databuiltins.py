#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **builtins module globals** (i.e., global constants describing the
standard :mod:`builtins` module).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._cave._cavefast import NoneType
from beartype._data.typing.datatyping import (
    LexicalScopeMutable,
    FrozenSetTypes,
)
from builtins import __dict__ as _BUILTINS_DICT  # type: ignore[attr-defined]

# ....................{ CONSTANTS ~ mappings               }....................
BUILTINS_DICT = _BUILTINS_DICT
'''
**Builtins module dictionary** mapping from the name to value of each **builtin
attribute** (i.e., object defined by the standard :mod:`builtins` module and
thus globally available by default *without* requiring explicit importation).

Caveats
-------
**Callers should typically prefer the higher-level**
:data:`.BUILTIN_NAME_TO_VALUE` **dictionary global**. This unfiltered
lower-level dictionary contains ignorable, useless, and otherwise unhelpful
attributes and is thus considered harmful for most real-world purposes.
'''


# Defined below by the _init() function.
BUILTIN_NAME_TO_VALUE: LexicalScopeMutable = None  # type: ignore[assignment]
'''
**Builtins module dictionary** mapping from the name to value of each **builtin
attribute** (i.e., object defined by the standard :mod:`builtins` module and
thus globally available by default *without* requiring explicit importation),
intentionally filtered so as to exclude ignorable, useless, and otherwise
unhelpful attributes.

This dictionary intentionally excludes:

* **Fake builtin types** (i.e., types that are *not* builtin but nonetheless
  erroneously masquerade as being builtin, infamously including the type of the
  :data:`None` singleton).
* **Dunder attributes** (i.e., attributes whose unqualified basenames are both
  prefixed and suffixed by ``"__"`` delimiters).
'''


# Defined below by the _init() function.
BUILTIN_NAME_TO_TYPE: LexicalScopeMutable = None  # type: ignore[assignment]
'''
Dictionary mapping from the name of each **non-fake builtin type** (i.e.,
globally accessible C-based type implicitly accessible from all scopes and thus
requiring *no* explicit importation) to that type.

This dictionary intentionally ignores **fake builtin types** (i.e., types that
are *not* builtin but nonetheless erroneously masquerade as being builtin,
including the type of the :data:`None` singleton).
'''


# Defined below by the _init() function.
BUILTIN_TYPES: FrozenSetTypes = None  # type: ignore[assignment]
'''
Frozen set of all **non-fake builtin types** (i.e., globally accessible C-based
types implicitly accessible from all scopes and thus requiring *no* explicit
importation).

This set intentionally ignores **fake builtin types** (i.e., types that are
*not* builtin but nonetheless erroneously masquerade as being builtin, including
the type of the :data:`None` singleton).
'''


BUILTIN_TYPES_SCALAR: FrozenSetTypes = frozenset((
    bytes,
    complex,
    float,
    int,
    str,
))
'''
Frozen set of all **builtin scalar types** (i.e., globally accessible C-based
types whose instances are scalar values).
'''


BUILTIN_TYPES_CONTAINER_MUTABLE: FrozenSetTypes = frozenset((
    bytearray,
    dict,
    list,
    set,
))
'''
Frozen set of all **builtin mutable container types** (i.e., C-based container
types globally accessible *without* requiring explicit importation, whose items
may be modified after instantiation).

All builtin mutable container types define these methods:

* ``clear()``, reducing the current object to the empty container.
'''

# ....................{ CONSTANTS ~ strings                }....................
BUILTINS_MODULE_NAME = 'builtins'
'''
Fully-qualified name of the **builtins module** (i.e., objects defined by the
standard :mod:`builtins` module and thus globally available by default
*without* requiring explicit importation).
'''


GLOBAL_SCOPE_BUILTINS_BASENAME = '__builtins__'
'''
Unqualified basename of the standard dunder attribute whose value is expected to
be a **builtins lexical scope** (i.e., dictionary mapping from the unqualified
basename to value of an attribute globally accessible from all possible scopes
*without* needing to be explicitly imported into either the current local or
global scope).

When Python fails to find an accessed attribute in either the current local or
global scope *and* that global scope defines a global attribute by this
basename, Python falls back to accessing that attribute from that global
attribute whose value is this builtins lexical scope instead.
'''

# ....................{ PRIVATE ~ init                     }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # ....................{ LOCALS                         }....................
    # Frozen set of all fake builtin types (i.e., types that erroneously
    # masquerade as being builtin). This includes:
    # * The type of the "None" singleton. For unknown reasons:
    #   * The CPython implementation of the standard "builtin" module correctly
    #     omits this type.
    #   * The PyPy implementation of the standard "builtin" module *INCORRECTLY*
    #     includes this type. Technically, this type should *ONLY* be included
    #     under PyPy. Pragmatically, unconditionally including this type under
    #     *ALL* Python implementations does no harm. This type is *ALWAYS*
    #     guaranteed to be fake wherever it appears.
    _FAKE_BUILTIN_TYPES = frozenset((NoneType,))

    # ....................{ GLOBALs                        }....................
    # Global variables redefined below.
    global \
        BUILTIN_NAME_TO_VALUE, \
        BUILTIN_NAME_TO_TYPE, \
        BUILTIN_TYPES

    # Dictionary mapping from...
    BUILTIN_NAME_TO_VALUE = {
        # The name of each builtin attribute to that attribute...
        builtin_name: builtin_value
        # For each attribute defined by the standard "builtins" module...
        for builtin_name, builtin_value in BUILTINS_DICT.items()
        # If...
        if (
            # Either...
            (
                # This builtin is not a type *OR*...
                not isinstance(builtin_value, type) or
                # This builtin is a non-fake type...
                builtin_value not in _FAKE_BUILTIN_TYPES
            # *AND*...
            ) and
            # This is not a dunder attribute (i.e., attribute whose unqualified
            # basename is both prefixed and suffixed by double underscores)...
            not (
                builtin_name.startswith('__') and
                builtin_name.endswith  ('__')
            )
        )
    }

    # Dictionary mapping from...
    BUILTIN_NAME_TO_TYPE = {
        # The name of each builtin type to that type...
        builtin_name: builtin_value
        # For each attribute defined by the standard "builtins" module...
        for builtin_name, builtin_value in BUILTIN_NAME_TO_VALUE.items()
        # If this attribute is a type.
        if isinstance(builtin_value, type)
    }

    # Frozenset of all builtin types, derived from this dictionary.
    BUILTIN_TYPES = frozenset(BUILTIN_NAME_TO_TYPE.values())


# Initialize this submodule.
_init()
