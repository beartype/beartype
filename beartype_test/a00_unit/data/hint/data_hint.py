#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide **type hint container data submodule.**

This submodule predefines low-level global constants exercising known edge
cases on behalf of higher-level unit test submodules -- including PEP-compliant
type hints, PEP-noncompliant type hint, and objects satisfying neither.
'''

# ....................{ TODO                               }....................
#FIXME: This submodule is largely vestigial. As time permits (so, never),
#refactor *ALL* remaining globals #below into either:
#* Comparable fixtures in the sibling "data_hintfixture" submodule.
#* Comparable globals in the parent "data_type" submodule.
#
#There's *A LOT* of weird stuff going on below. So it goes, QA friends. *sigh*

# ....................{ IMPORTS                            }....................
from beartype._cave._cavefast import (
    AnyType,
    NoneType,
)
from beartype._cave._cavemap import NoneTypeOr

# ....................{ NON-HINTS ~ sets                   }....................
NOT_HINTS_HASHABLE = frozenset((
    # Scalar that is neither a type nor string (i.e., forward reference).
    0.12345678910111213141516,
    # Empty tuple.
    (),
    # Tuple containing a scalar that is neither a type nor string.
    (list, 'list', 0xFEEDFACE, NoneType,),
))
'''
Frozen set of various objects that are hashable but nonetheless unsupported by
the :func:`beartype.beartype` decorator as valid type hints.
'''

# ....................{ NON-HINTS ~ tuples                 }....................
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
defined as a tuple rather than a set.
'''


NOT_HINTS = tuple(NOT_HINTS_HASHABLE) + NOT_HINTS_UNHASHABLE
'''
Tuple of various objects unsupported by the :func:`beartype.beartype` decorator
as valid type hints, including both hashable and unhashable unsupported
objects.

Since sets *cannot* by design contain unhashable objects, this container is
defined as a tuple rather than a set.
'''

# ....................{ NON-PEP ~ classes                  }....................
class NonpepCustom(str):
    '''
    PEP-noncompliant user-defined class subclassing an arbitrary superclass.
    '''

    pass


class NonpepCustomFakeTyping(object):
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
NonpepCustomFakeTyping.__module__ = 'typing'

# ....................{ NON-PEP ~ sets                     }....................
# Note that we intentionally omit the "NonpepCustomFakeTyping" class here, as
# that class masquerades too well as a "typing" class -- so well, in fact, that
# "beartype._util.hint.pep.utilpeptest" functions are incapable of reasonably
# distinguishing instances of that class from actual "typing" type hints.
HINTS_NONPEP = frozenset((
    # Builtin container type.
    list,
    # Builtin scalar type.
    str,
    # User-defined type.
    NonpepCustom,
    # Non-empty tuple containing two types.
    NoneTypeOr[AnyType],
    # Non-empty tuple containing two types and a fully-qualified forward
    # reference.
    (int, 'beartype._cave._cavefast.NoneType', set)
))
'''
Frozen set of PEP-noncompliant type hints exercising well-known edge cases.
'''


HINTS_NONPEP_UNIGNORABLE = (
    # PEP-noncompliant type.
    str,
    # PEP-noncompliant tuple of types.
    NoneTypeOr[AnyType],
)
'''
Frozen set of **unignorable PEP-noncompliant type hints** (i.e.,
PEP-noncompliant type hints that are *not* ignorable).
'''

# ....................{ NOT ~ sets                         }....................
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
