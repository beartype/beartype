#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 484`_ **detection unit tests.**

This submodule unit tests `PEP 484`_ **detection support** (i.e., testing
whether arbitrary objects comply with `PEP 484`_).

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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

# ....................{ TESTS ~ type                      }....................
def test_is_typing() -> None:
    '''
    Test the :func:`beartype._decor.pep484.p484test.is_typing` tester.
    '''

    # Defer heavyweight imports.
    from beartype import cave
    from beartype._decor.pep484.p484test import is_typing

    # Tuple of various "typing" types of interest.
    P484_TYPES = (
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
        T,
        TypingUserDefined,
        GenericUserDefined,
        TypeAlias,
    )

    # Tuple of various non-"typing" types of interest.
    NON_P484_TYPES = (
        list,
        str,
        cave.AnyType,
        cave.NoneType,
        cave.NoneTypeOr[cave.AnyType],
    )

    # Assert that various "typing" types are correctly detected.
    for p484_type in P484_TYPES:
        print('PEP 484 type: {!r}'.format(p484_type))
        assert is_typing(p484_type) is True

    # Assert that various non-"typing" types are correctly detected.
    for non_p484_type in NON_P484_TYPES:
        print('Non-PEP 484 type: {!r}'.format(non_p484_type))
        assert is_typing(non_p484_type) is False


def test_is_typing_typevar() -> None:
    '''
    Test the :func:`beartype._decor.pep484.p484test.is_typing_typevar` tester.
    '''

    # Defer heavyweight imports.
    from beartype._decor.pep484.p484test import is_typing_typevar

    # Tuple of various "TypeVar"-centric types of interest.
    TYPEVAR_TYPES = (
        typing.Union[str, typing.Iterable[typing.Tuple[S, T]]],
        S,
        T,
        GenericUserDefined,
        GenericUserDefinedMultiple,
        TypeAlias,
        TypeAlias[T],
    )

    # Tuple of various "TypeVar"-agnostic types of interest.
    NON_TYPEVAR_TYPES = (
        typing.Any,
        typing.Callable[[], str],
        typing.Dict[str, str],
        typing.List[float],
        typing.Generator[int, float, str],
        typing.NoReturn,
        typing.Tuple[str, int],
        typing.Type[dict],
        typing.Union[str, typing.Sequence[int]],
        TypingUserDefined,
    )

    # Assert that various "TypeVar"-centric types are correctly detected.
    for typevar_type in TYPEVAR_TYPES:
        print('"TypeVar"-centric type: {!r}'.format(typevar_type))
        assert is_typing_typevar(typevar_type) is True

    # Assert that various "TypeVar"-agnostic types are correctly detected.
    for non_typevar_type in NON_TYPEVAR_TYPES:
        print('"TypeVar"-agnostic type: {!r}'.format(non_typevar_type))
        assert is_typing_typevar(non_typevar_type) is False
