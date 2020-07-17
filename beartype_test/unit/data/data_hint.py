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

# ....................{ TYPE VARIABLES                    }....................
S = typing.TypeVar('S')
'''
User-defined generic :mod:`typing` type variable.
'''


T = typing.TypeVar('T')
'''
User-defined generic :mod:`typing` type variable.
'''

# ....................{ TYPE ALIASES                      }....................
TypeAlias = typing.Iterable[typing.Tuple[T, T]]
'''
User-defined :mod:`typing` type alias.
'''

# ....................{ CLASSES ~ generic                 }....................
class TypingUserDefined(typing.Dict[str, typing.List[str]]):
    '''
    User-defined :mod:`typing` subtype.
    '''

    pass


class TypingUserDefinedMultiple(
    typing.Iterable[T],
    typing.Container[T],
):
    '''
    User-defined :mod:`typing` subtype subclassing multiple :mod:`typing`
    types.
    '''

    pass

# ....................{ CLASSES ~ generic                 }....................
class GenericUserDefined(typing.Generic[S, T]):
    '''
    User-defined generic :mod:`typing` subtype.
    '''

    pass


class GenericUserDefinedMultiple(
    collections.abc.Sized,
    typing.Iterable[typing.Tuple[S, T]],
    typing.Container[typing.Tuple[S, T]],
    typing.Generic[S, T],
):
    '''
    User-defined generic :mod:`typing` subtype subclassing a heterogeneous
    amalgam of non-:mod:`typing` and :mod:`typing` superclasses.
    '''

    pass

# ....................{ MAPPINGS                          }....................
P484_HINT_TO_ATTRS = {
    typing.Any: typing.Any,
    typing.Callable[[], str]: typing.Callable,
    typing.Dict[str, str]: typing.Dict,
    typing.List[float]: typing.List,
    typing.Generator[int, float, str]: typing.Generator,
    typing.NoReturn: typing.NoReturn,
    typing.Tuple[str, int]: typing.Tuple,
    typing.Type[dict]: typing.Type,
    typing.Union[str, typing.Iterable[typing.Tuple[S, T]]]: typing.Union,
    typing.Union[str, typing.Sequence[int]]: typing.Union,
    GenericUserDefined: typing.Generic,
    GenericUserDefinedMultiple: (
        typing.Iterable, typing.Container, typing.Generic,),
    T: typing.TypeVar,
    TypeAlias: typing.Iterable,
    TypingUserDefined: typing.Dict,
    TypingUserDefinedMultiple: (typing.Iterable, typing.Container,),
}
'''
Dictionary mapping various `PEP 484`_-compliant type hints to a set of all
public attributes of the :mod:`typing` module uniquely identifying those hints.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ ITERABLES                         }....................
P484_HINTS = P484_HINT_TO_ATTRS.keys()
'''
Iterable of various `PEP 484`_-compliant type hints exercising *all* edge cases
on behalf of test submodules.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''


NONPEP_HINTS = (
    list,
    str,
    cave.AnyType,
    cave.NoneType,
    cave.NoneTypeOr[cave.AnyType],
)
'''
Tuple of various PEP-noncompliant type hints of interest.
'''
