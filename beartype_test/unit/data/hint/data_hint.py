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
from beartype._util.hint.data.utilhintdata import HINTS_IGNORABLE_SHALLOW
from beartype_test.unit.data.hint.pep.data_hintpep import (
    HINTS_PEP,
    HINTS_PEP_IGNORABLE_DEEP,
)

# ....................{ NON-HINTS ~ sets                  }....................
NOT_HINTS_HASHABLE = frozenset((
    # Scalar that is neither a type nor string (i.e., forward reference).
    0.12345678910111213141516,
    # Empty tuple.
    (),
    # Tuple containing an scalar that is neither a type nor string.
    (list, 'list', 0xFEEDFACE, cave.NoneType,),
))
'''
Frozen set of various objects that are hashable but nonetheless unsupported by
the :func:`beartype.beartype` decorator as valid type hints.
'''

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

Since sets *cannot* by design contain unhashable objects, this container is
defined as a tuple rather than set.
'''

# ....................{ NON-PEP ~ classes                 }....................
class NonPepCustom(str):
    '''
    PEP-noncompliant user-defined class subclassing an arbitrary superclass.
    '''

    pass


class NonPepCustomFakeTyping(object):
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

# ....................{ NON-PEP ~ sets                    }....................
HINTS_NONPEP = frozenset((
    # Builtin container type.
    list,
    # Builtin scalar type.
    str,
    # User-defined type.
    NonPepCustom,
    # Beartype cave type.
    cave.NoneType,
    # Non-empty tuple containing two types.
    cave.NoneTypeOr[cave.AnyType],
    # Non-empty tuple containing two types and a fully-qualified forward
    # reference.
    (int, 'beartype.cave.NoneType', set)
))
'''
Frozen set of PEP-noncompliant type hints exercising well-known edge cases.
'''


HINTS_NONPEP_UNIGNORABLE = (
    # PEP-noncompliant type.
    str,
    # PEP-noncompliant tuple of types.
    cave.NoneTypeOr[cave.AnyType],
)
'''
Frozen set of **unignorable PEP-noncompliant type hints** (i.e.,
PEP-noncompliant type hints that are *not* ignorable).
'''

# ....................{ NOT ~ sets                        }....................
NOT_HINTS_NONPEP = frozenset((
    # Set comprehension of tuples containing PEP-compliant type hints. Although
    # tuples containing PEP-noncompliant type hints are themselves valid
    # PEP-noncompliant type hints supported by @beartype, tuples containing
    # PEP-compliant type hints are invalid and thus unsupported.
    {
        # Tuple containing a PEP-compliant type hint.
        (int, hint_pep, cave.NoneType,)
        for hint_pep in HINTS_PEP
    } |
    # PEP-compliant type hints.
    HINTS_PEP |
    # Hashable objects invalid as type hints (e.g., scalars).
    NOT_HINTS_HASHABLE
))
'''
Tuple of various objects that are *not* PEP-noncompliant type hints exercising
well-known edge cases.
'''


NOT_HINTS_PEP = (
    # PEP-noncompliant type hints.
    HINTS_NONPEP |
    # Hashable objects invalid as type hints (e.g., scalars).
    NOT_HINTS_HASHABLE
)
'''
Tuple of various objects that are *not* PEP-compliant type hints exercising
well-known edge cases.
'''

# ....................{ NOT ~ tuples                      }....................
HINTS_IGNORABLE = (
    # Shallowly ignorable type hints.
    HINTS_IGNORABLE_SHALLOW |
    # Deeply ignorable PEP-compliant type hints.
    HINTS_PEP_IGNORABLE_DEEP
)
'''
Frozen set of **ignorable type hints** (i.e., type hints that are either
shallowly ignorable *or* deeply ignorable PEP-compliant type hints).
'''
