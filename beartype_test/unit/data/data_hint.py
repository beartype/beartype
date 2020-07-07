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

# ....................{ TUPLES                            }....................
P484_HINTS = (
    typing.Any,
    typing.Callable[[], str],
    typing.Dict[str, str],
    typing.List[float],
    typing.Generator[int, float, str],
    typing.NoReturn,
    typing.Tuple[str, int],
    typing.Type[dict],
    typing.Union[str, typing.Iterable[typing.Tuple[S, T]]],
    typing.Union[str, typing.Sequence[int]],
    GenericUserDefined,
    GenericUserDefinedMultiple,
    T,
    TypeAlias,
    TypingUserDefined,
)
'''
Tuple of various `PEP 484`_-compliant type hints exercising *all* edge cases on
behalf of test submodules.

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
