#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype type hints data-driven testing submodule.**

This submodule predefines low-level global constants exercising known edge
cases on behalf of higher-level unit test submodules -- including PEP-compliant
type hints, PEP-noncompliant type hint, and objects satisfying neither.
'''

# ....................{ IMPORTS                            }....................
from beartype._cave._cavefast import (
    AnyType,
    NoneType,
)
from beartype._cave._cavemap import NoneTypeOr
from pytest import fixture

# ....................{ FIXTURES                           }....................
@fixture(scope='session')
def hints_meta(hints_pep_meta, hints_nonpep_meta) -> (
    'Tuple[HintNonpepMetadata]'):
    '''
    Session-scoped fixture yielding a tuple of **PEP-agnostic type hint
    metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintNonpepMetadata`
    instances, each describing a sample type hint exercising an edge case in the
    :mod:`beartype` codebase -- including both PEP-compliant and -noncompliant
    type hints).

    Parameters
    ----------
    hints_pep_meta : Tuple[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        Tuple of PEP-compliant type hint metadata describing PEP-compliant type
        hints exercising edge cases in the :mod:`beartype` codebase.
    hints_nonpep_meta : Tuple[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintNonpepMetadata]
        Tuple of PEP-noncompliant type hint metadata describing PEP-noncompliant
        type hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # One world. One-liner. Let's get together and code alright.
    yield hints_pep_meta + hints_nonpep_meta


@fixture(scope='session')
def hints_ignorable(
    hints_pep_ignorable_shallow,
    hints_pep_ignorable_deep,
) -> frozenset:
    '''
    Session-scoped fixture yielding a frozen set of **ignorable
    PEP-agnostic type hints,** including both PEP-compliant *and* -noncompliant
    and shallowly *and* deeply ignorable type hints.

    Parameters
    ----------
    hints_pep_ignorable_shallow : frozenset
        Frozen set of all shallowly ignorable PEP-compliant type hints.
    hints_pep_ignorable_deep : frozenset
        Frozen set of all deeply ignorable PEP-compliant type hints.
    '''

    # I code the one-liner, but I did not code the two-liner.
    yield (
        hints_pep_ignorable_shallow |
        hints_pep_ignorable_deep
    )

# ....................{ FIXTURES ~ not : sets              }....................
@fixture(scope='session')
def not_hints_nonpep(hints_pep_hashable) -> frozenset:
    '''
    Session-scoped fixture yielding a frozen set of various objects that are
    *not* PEP-noncompliant type hints exercising well-known edge cases.

    Parameters
    ----------
    hints_pep_hashable : frozenset
        Tuple of PEP-compliant type hint metadata describing PEP-compliant type
        hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    yield frozenset((
        # Set comprehension of tuples containing PEP-compliant type hints. Although
        # tuples containing PEP-noncompliant type hints are themselves valid
        # PEP-noncompliant type hints supported by @beartype, tuples containing
        # PEP-compliant type hints are invalid and thus unsupported.
        {
            # Tuple containing this PEP-compliant type hint...
            (int, hint_pep_hashable, NoneType,)
            # For each hashable PEP-compliant type hint...
            for hint_pep_hashable in hints_pep_hashable
            # That is neither:
            # * An isinstanceable class.
            # * A string-based forward reference.
            #
            # Both are unique edge cases supported as both PEP 484-compliant outside
            # tuples *AND* beartype-specific inside tuples. Including these hints
            # here would erroneously cause tests to treat tuples containing these
            # hints as *NOT* tuple type hints.
            if not isinstance(hint_pep_hashable, (str, type))
        } |
        # Set comprehension of hashable PEP-compliant non-class type hints.
        hints_pep_hashable |
        # Hashable objects invalid as type hints (e.g., scalars).
        NOT_HINTS_HASHABLE
    ))

# ....................{ NON-HINTS ~ sets                   }....................
#FIXME: Refactor *ALL* remaining globals below into comparable fixtures, please.
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
