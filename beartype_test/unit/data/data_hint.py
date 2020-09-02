#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype type hints data-driven testing submodule.**

This submodule predefines low-level global constants exercising known edge
cases on behalf of higher-level unit test submodules -- including PEP-compliant
type hints, PEP-noncompliant type hint, and objects satisfying neither.
'''

# ....................{ IMPORTS                           }....................
from beartype import cave

# Import all public attributes of this private data-driven testing submodule
# for use by higher-level unit test submodules elsewhere.
from beartype_test.unit.data._data_hint_pep import (
    PEP_HINT_TO_META,
    PEP_HINT_NONATTR_TO_META,
    PEP_HINTS,
    S,
    T,
    PepGenericTypevaredSingle,
    PepGenericUntypevaredSingle,
    PepGenericTypevaredShallowMultiple,
    PepGenericTypevaredDeepMultiple,
)

# ....................{ NON-HINTS ~ tuples                }....................
NOT_HINTS_UNHASHABLE = (
    # Dictionary.
    {'For all things turn to barrenness':
     'In the dim glass the demons hold,',},
    # List.
    ['The glass of outer weariness,',
     'Made when God slept in times of old.',],
    # Set.
    {'There, through the broken branches, go',
     'The ravens of unresting thought;',},
)
'''
Tuple of various objects that are unhashable and thus unsupported by the
:func:`beartype.beartype` decorator as valid type hints.
'''


NOT_HINTS_HASHABLE = (
    # Scalar that is neither a type nor string (i.e., forward reference).
    0.12345678910111213141516,
    # Empty tuple.
    (),
    # Tuple containing an scalar that is neither a type nor string.
    (list, 'list', 0xFEEDFACE, cave.NoneType,),
)
'''
Tuple of various objects that are hashable but nonetheless unsupported by the
:func:`beartype.beartype` decorator as valid type hints.
'''

# ....................{ NON-PEP ~ classes                 }....................
class NonPepCustom(str):
    '''
    PEP-noncompliant user-defined class subclassing an arbitrary superclass.
    '''

    pass


class NonPepCustomFakeTyping(str):
    '''
    PEP-noncompliant user-defined class subclassing an arbitrary superclass
    erroneously masquerading as a :mod:`typing` class.

    Specifically, this class:

    * Defines the :meth:`__repr__` dunder method to return a string prefixed by
      the substring ``"typing."``.
    * Defines the :attr:`__module__` dunder attribute to be the fully-qualified
      module name ``"typing"``.
    '''

    def __repr__(self) -> str:
        return 'typing.FakeTypingType'
NonPepCustomFakeTyping.__module__ = 'typing'

# ....................{ NON-PEP ~ tuples                  }....................
NONPEP_HINTS = (
    # Builtin container type.
    list,
    # Builtin scalar type.
    str,
    # User-defined type.
    NonPepCustom,
    # Beartype cave type.
    cave.NoneType,
    # Unqualified forward reference.
    'dict',
    # Fully-qualified forward reference.
    'beartype.cave.AnyType',
    # Non-empty tuple containing two types.
    cave.NoneTypeOr[cave.AnyType],
    # Non-empty tuple containing two types and a fully-qualified forward
    # reference.
    (int, 'beartype.cave.NoneType', set)
)
'''
Tuple of various PEP-noncompliant type hints exercising well-known edge cases.
'''

# ....................{ NOT ~ tuples                      }....................
NOT_NONPEP_HINTS = (
    # Tuple comprehension of tuples containing PEP-compliant type hints.
    tuple(
        # Tuple containing a PEP-compliant type hint.
        (int, pep_hint, cave.NoneType,)
        for pep_hint in PEP_HINTS
    ) +
    # PEP-compliant type hints.
    PEP_HINTS +
    # Hashable objects invalid as type hints (e.g., scalars).
    NOT_HINTS_HASHABLE
)
'''
Tuple of various objects that are *not* PEP-noncompliant type hints exercising
well-known edge cases.
'''


NOT_PEP_HINTS = (
    # PEP-noncompliant type hints.
    NONPEP_HINTS +
    # Hashable objects invalid as type hints (e.g., scalars).
    NOT_HINTS_HASHABLE
)
'''
Tuple of various objects that are *not* PEP-compliant type hints exercising
well-known edge cases.
'''
