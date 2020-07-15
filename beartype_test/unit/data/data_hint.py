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
from beartype import cave
from collections.abc import Sized
import typing

# ....................{ TYPE VARIABLES                    }....................
S = typing.TypeVar('S')
'''
User-defined generic :mod:`typing` type variable.
'''


T = typing.TypeVar('T')
'''
User-defined generic :mod:`typing` type variable.
'''

# ....................{ CLASSES                           }....................
class GenericUserDefined(typing.Generic[S, T]):
    '''
    User-defined generic :mod:`typing` subtype.
    '''

    pass


class GenericUserDefinedMultiple(Sized, typing.Generic[T]):
    '''
    User-defined generic :mod:`typing` subtype also subclassing a
    non-:mod:`typing` superclass.
    '''

    pass


class TypingUserDefined(typing.Dict[str, typing.List[str]]):
    '''
    User-defined :mod:`typing` subtype.
    '''

    pass



TypeAlias = typing.Iterable[typing.Tuple[T, T]]
'''
User-defined :mod:`typing` type alias.
'''

# ....................{ MAPPINGS                          }....................
P484_HINT_TO_ATTR = {
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
    GenericUserDefinedMultiple: typing.Generic,
    T: typing.TypeVar,
    TypeAlias: typing.Iterable,
    TypingUserDefined: typing.Dict,
}
'''
Dictionary mapping various `PEP 484`_-compliant type hints to the public
attributes of the :mod:`typing` module uniquely identifying those hints.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ ITERABLES                         }....................
P484_HINTS = P484_HINT_TO_ATTR.keys()
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
