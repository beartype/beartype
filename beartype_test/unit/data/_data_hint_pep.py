#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hints data-driven testing submodule.**

This submodule predefines low-level global constants whose values are
PEP-compliant type hints, exercising known edge cases on behalf of higher-level
unit test submodules.
'''

# ....................{ IMPORTS                           }....................
import collections, typing
from collections import namedtuple

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
_PepHintMetadata = namedtuple('_PepHintMetadata', (
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
    typing.Callable[[], str]: _PepHintMetadata(
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        typing_attr=typing.Callable,
    ),

    # ..................{ CALLABLES ~ generator             }..................
    typing.Generator[int, float, str]: _PepHintMetadata(
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        typing_attr=typing.Generator,
    ),

    # ..................{ COLLECTIONS ~ dict                }..................
    typing.Dict: _PepHintMetadata(
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        typing_attr=typing.Dict,
    ),
    typing.Dict[str, int]: _PepHintMetadata(
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        typing_attr=typing.Dict,
    ),
    typing.Dict[S, T]: _PepHintMetadata(
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        typing_attr=typing.Dict,
    ),

    # ..................{ COLLECTIONS ~ list                }..................
    typing.List: _PepHintMetadata(
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        typing_attr=typing.List,
    ),
    typing.List[float]: _PepHintMetadata(
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        typing_attr=typing.List,
    ),
    typing.List[T]: _PepHintMetadata(
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        typing_attr=typing.List,
    ),

    # ..................{ COLLECTIONS ~ tuple               }..................
    # Note that argumentless "typing.Tuple" attributes are *NOT* parametrized
    # by one or more type variables, unlike most other argumentless "typing"
    # attributes originating from container types. *sigh*
    typing.Tuple: _PepHintMetadata(
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        typing_attr=typing.Tuple,
    ),
    typing.Tuple[float, str, int]: _PepHintMetadata(
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        typing_attr=typing.Tuple,
    ),
    typing.Tuple[T, ...]: _PepHintMetadata(
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        typing_attr=typing.Tuple,
    ),

    # ..................{ SINGLETONS                        }..................
    typing.Any: _PepHintMetadata(
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        typing_attr=typing.Any,
    ),
    typing.NoReturn: _PepHintMetadata(
        is_supported=False,
        is_generic_user=False,
        is_typevared=False,
        typing_attr=typing.NoReturn,
    ),

    # ..................{ TYPE ALIASES                      }..................
    typing.Type: _PepHintMetadata(
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        typing_attr=typing.Type,
    ),
    typing.Type[dict]: _PepHintMetadata(
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        typing_attr=typing.Type,
    ),
    typing.Type[T]: _PepHintMetadata(
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        typing_attr=typing.Type,
    ),

    # ..................{ TYPE VARIABLES                    }..................
    # Type variables.
    T: _PepHintMetadata(
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
    typing.Union[str, typing.Sequence[int]]: _PepHintMetadata(
        is_supported=True,
        is_generic_user=False,
        is_typevared=False,
        typing_attr=typing.Union,
    ),
    # Union of one non-"typing" type and one concrete generic.
    typing.Union[str, typing.Iterable[typing.Tuple[S, T]]]: _PepHintMetadata(
        is_supported=False,
        is_generic_user=False,
        is_typevared=True,
        typing_attr=typing.Union,
    ),

    # ..................{ CUSTOM                            }..................
    PepGenericTypevaredSingle: _PepHintMetadata(
        is_supported=False,
        is_generic_user=True,
        is_typevared=True,
        typing_attr=typing.Generic,
    ),
    PepGenericUntypevaredSingle: _PepHintMetadata(
        is_supported=False,
        is_generic_user=True,
        is_typevared=False,
        typing_attr=typing.Generic,
    ),
    PepGenericTypevaredShallowMultiple: _PepHintMetadata(
        is_supported=False,
        is_generic_user=True,
        is_typevared=True,
        typing_attr=typing.Generic,
    ),
    PepGenericTypevaredDeepMultiple: _PepHintMetadata(
        is_supported=False,
        is_generic_user=True,
        is_typevared=True,
        typing_attr=typing.Generic,
    ),
}
'''
Dictionary mapping various PEP-compliant type hints to
:class:`_PepHintMetadata` instances detailing those hints with metadata
applicable to testing scenarios.
'''

# ....................{ PEP ~ tuples                      }....................
PEP_HINTS = tuple(PEP_HINT_TO_META.keys())
'''
Tuple of various PEP-compliant type hints exercising well-known edge cases.
'''
