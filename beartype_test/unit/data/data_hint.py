#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype annotations and type hints data submodule.**

This submodule defines various types (including both `PEP 484`_-compliant and
-noncompliant types) exercising *all* edge cases on behalf of test submodules.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ IMPORTS                           }....................
import collections, typing
from beartype import cave
from beartype._util.utilpy import IS_PYTHON_AT_LEAST_3_7
from collections import namedtuple

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

# ....................{ PEP ~ typevars                    }....................
S = typing.TypeVar('S')
'''
User-defined generic :mod:`typing` type variable.
'''


T = typing.TypeVar('T')
'''
User-defined generic :mod:`typing` type variable.
'''

# ....................{ PEP ~ generics : single           }....................
class PepGenericTypevaredSingle(typing.Generic[S, T]):
    '''
    PEP-compliant user-defined class subclassing a single parametrized
    :mod:`typing` type.
    '''

    pass


class PepGenericUntypevaredSingle(typing.Dict[str, typing.List[str]]):
    '''
    PEP-compliant user-defined class subclassing a single unparametrized
    :mod:`typing` type.
    '''

    pass

# ....................{ PEP ~ generics : multiple         }....................
class PepGenericTypevaredShallowMultiple(
    typing.Iterable[T], typing.Container[T]):
    '''
    PEP-compliant user-defined class subclassing multiple directly parametrized
    :mod:`typing` types.
    '''

    pass


class PepGenericTypevaredDeepMultiple(
    collections.abc.Sized,
    typing.Iterable[typing.Tuple[S, T]],
    typing.Container[typing.Tuple[S, T]],
):
    '''
    PEP-compliant user-defined generic :mod:`typing` subtype subclassing a
    heterogeneous amalgam of non-:mod:`typing` and :mod:`typing` superclasses.
    User-defined class subclassing multiple indirectly parametrized
    :mod:`typing` types as well as a non-:mod:`typing` abstract base class
    '''

    pass

# ....................{ PEP ~ mappings                    }....................
PepHintMeta = namedtuple('PepHintMeta', (
    'is_supported',
    'is_generic_user',
    'is_typevared',
    'typing_attr',
))
'''
**PEP-compliant type hint metadata** (i.e., named tuple whose variables detail
a PEP-compliant type hint with metadata applicable to testing scenarios).

Attributes
----------
is_supported : bool
    ``True`` only if this PEP-compliant type hint is currently supported by the
    :func:`beartype.beartype` decorator.
is_generic_user : bool
    ``True`` only if this PEP-compliant type hint is a **user-defined generic**
    (i.e., PEP-compliant type hint whose class subclasses one or more public
    :mod:`typing` pseudo-superclasses but *not* itself defined by the
    :mod:`typing` module).
is_typevared : bool
    ``True`` only if this PEP-compliant type hint is parametrized by one or
    more **type variables** (i.e., :class:`typing.TypeVar` instances).
typing_attr : object
    **Argumentless** :mod:`typing` **attribute** (i.e., public attribute of the
    :mod:`typing` module uniquely identifying this PEP-compliant type hint,
    stripped of all subscripted arguments but *not* default type variables).
'''


PEP_HINT_TO_META = {
    # ..................{ CALLABLES                         }..................
    typing.Callable[[], str]: PepHintMeta(
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        typing_attr=typing.Callable,
    ),

    # ..................{ CALLABLES ~ generator             }..................
    typing.Generator[int, float, str]: PepHintMeta(
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        typing_attr=typing.Generator,
    ),

    # ..................{ COLLECTIONS ~ dict                }..................
    typing.Dict: PepHintMeta(
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        typing_attr=typing.Dict,
    ),
    typing.Dict[str, int]: PepHintMeta(
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        typing_attr=typing.Dict,
    ),
    typing.Dict[S, T]: PepHintMeta(
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        typing_attr=typing.Dict,
    ),

    # ..................{ COLLECTIONS ~ list                }..................
    typing.List: PepHintMeta(
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        typing_attr=typing.List,
    ),
    typing.List[float]: PepHintMeta(
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        typing_attr=typing.List,
    ),
    typing.List[T]: PepHintMeta(
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        typing_attr=typing.List,
    ),

    # ..................{ COLLECTIONS ~ tuple               }..................
    # Note that argumentless "typing.Tuple" attributes are *NOT* parametrized
    # by one or more type variables, unlike most other argumentless "typing"
    # attributes originating from container types. *sigh*
    typing.Tuple: PepHintMeta(
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        typing_attr=typing.Tuple,
    ),
    typing.Tuple[float, str, int]: PepHintMeta(
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        typing_attr=typing.Tuple,
    ),
    typing.Tuple[T, ...]: PepHintMeta(
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        typing_attr=typing.Tuple,
    ),

    # ..................{ SINGLETONS                        }..................
    typing.Any: PepHintMeta(
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        typing_attr=typing.Any,
    ),
    typing.NoReturn: PepHintMeta(
        is_supported=False,
        is_generic_user=False,
        is_typevared=False,
        typing_attr=typing.NoReturn,
    ),

    # ..................{ TYPE ALIASES                      }..................
    typing.Type: PepHintMeta(
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        typing_attr=typing.Type,
    ),
    typing.Type[dict]: PepHintMeta(
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        typing_attr=typing.Type,
    ),
    typing.Type[T]: PepHintMeta(
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        typing_attr=typing.Type,
    ),

    # ..................{ TYPE VARIABLES                    }..................
    # Type variables.
    T: PepHintMeta(
        is_supported=False,
        is_generic_user=False,
        is_typevared=False,
        typing_attr=typing.TypeVar,
    ),

    # ..................{ UNIONS                            }..................
    # Note that unions of one arguments (e.g., "typing.Union[str]") *CANNOT* be
    # listed here, as the "typing" module implicitly reduces these unions to
    # only that argument (e.g., "str") on our behalf. Thanks. Thanks alot.

    # Union of one non-"typing" type and an isinstance()-able "typing" type,
    # exercising an edge case.
    typing.Union[str, typing.Sequence[int]]: PepHintMeta(
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        typing_attr=typing.Union,
    ),
    # Union of one non-"typing" type and one concrete generic.
    typing.Union[str, typing.Iterable[typing.Tuple[S, T]]]: PepHintMeta(
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        typing_attr=typing.Union,
    ),

    # ..................{ CUSTOM                            }..................
    PepGenericTypevaredSingle: PepHintMeta(
        is_supported=False,
        is_generic_user=True,
        is_typevared=True,
        typing_attr=typing.Generic,
    ),
    PepGenericUntypevaredSingle: PepHintMeta(
        is_supported=False,
        is_generic_user=True,
        is_typevared=False,
        typing_attr=typing.Generic,
    ),
    PepGenericTypevaredShallowMultiple: PepHintMeta(
        is_supported=False,
        is_generic_user=True,
        is_typevared=True,
        typing_attr=typing.Generic,
    ),
    PepGenericTypevaredDeepMultiple: PepHintMeta(
        is_supported=False,
        is_generic_user=True,
        is_typevared=True,
        typing_attr=typing.Generic,
    ),
}
'''
Dictionary mapping various PEP-compliant type hints to :class:`PepHintMeta`
instances detailing those hints with metadata applicable to testing scenarios.
'''

# ....................{ PEP ~ tuples                      }....................
PEP_HINTS = tuple(PEP_HINT_TO_META.keys())
'''
Tuple of various PEP-compliant type hints exercising well-known edge cases.
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

# ....................{ NON-PEP ~ tuples (more)           }....................
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

