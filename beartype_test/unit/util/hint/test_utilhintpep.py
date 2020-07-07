#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.utilhintpep` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import typing

# ....................{ TESTS                             }....................
def test_utilhint_is_hint_typing() -> None:
    '''
    Test the :func:`beartype._util.hint.utilhintpep._is_hint_typing` tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.utilhintpep import _is_hint_typing
    from beartype_test.unit.data.data_hint import NONPEP_HINTS, P484_HINTS

    # Assert that various "typing" types are correctly detected.
    for pep_hint in P484_HINTS:
        print('PEP hint: {!r}'.format(pep_hint))
        assert _is_hint_typing(pep_hint) is True

    # Assert that various non-"typing" types are correctly detected.
    for nonpep_hint in NONPEP_HINTS:
        print('Non-PEP hint: {!r}'.format(nonpep_hint))
        assert _is_hint_typing(nonpep_hint) is False


def test_p484test_is_hint_typing_typevarish() -> None:
    '''
    Test the :func:`beartype._util.hint.utilhintpep.is_hint_typing_typevarish`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.utilhintpep import is_hint_typing_typevarish
    from beartype_test.unit.data.data_hint import (
        S,
        T,
        GenericUserDefined,
        GenericUserDefinedMultiple,
        TypeAlias,
        TypingUserDefined,
    )

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
        assert is_hint_typing_typevarish(typevar_type) is True

    # Assert that various "TypeVar"-agnostic types are correctly detected.
    for non_typevar_type in NON_TYPEVAR_TYPES:
        print('"TypeVar"-agnostic type: {!r}'.format(non_typevar_type))
        assert is_hint_typing_typevarish(non_typevar_type) is False
