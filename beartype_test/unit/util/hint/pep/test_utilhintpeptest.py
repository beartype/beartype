#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint tester utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.utilhintpeptest` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import typing

# ....................{ TESTS                             }....................
def test_is_hint_pep() -> None:
    '''
    Test the :func:`beartype._util.hint.pep.utilhintpeptest.is_hint_pep`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpeptest import is_hint_pep
    from beartype_test.unit.data.data_hint import NONPEP_HINTS, PEP_HINTS

    # Assert that various "typing" types are correctly detected.
    for pep_hint in PEP_HINTS:
        print('PEP hint: {!r}'.format(pep_hint))
        assert is_hint_pep(pep_hint) is True

    # Assert that various non-"typing" types are correctly detected.
    for nonpep_hint in NONPEP_HINTS:
        print('Non-PEP hint: {!r}'.format(nonpep_hint))
        assert is_hint_pep(nonpep_hint) is False

# ....................{ TESTS ~ typevar                   }....................
def test_is_hint_typing_typevar() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpeptest.is_hint_typing_typevar`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpeptest import is_hint_typing_typevar
    from beartype_test.unit.data.data_hint import (
        S,
        T,
        GenericUserDefined,
        GenericUserDefinedMultiple,
        TypeAlias,
        TypingUserDefined,
    )

    # Tuple of various type variables.
    TYPEVAR_TYPES = (
        S,
        T,
    )

    # Tuple of various non-type variables.
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
        typing.Union[str, typing.Iterable[typing.Tuple[S, T]]],
        GenericUserDefined,
        GenericUserDefinedMultiple,
        TypeAlias,
        TypeAlias[T],
        TypingUserDefined,
    )

    # Assert that various "TypeVar"-centric types are correctly detected.
    for typevar_type in TYPEVAR_TYPES:
        print('Type variable: {!r}'.format(typevar_type))
        assert is_hint_typing_typevar(typevar_type) is True

    # Assert that various "TypeVar"-agnostic types are correctly detected.
    for non_typevar_type in NON_TYPEVAR_TYPES:
        print('Non-type variable: {!r}'.format(non_typevar_type))
        assert is_hint_typing_typevar(non_typevar_type) is False


def test_is_hint_typing_typevared() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpeptest.is_hint_typing_typevared`
    tester.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpeptest import (
        is_hint_typing_typevared)
    from beartype_test.unit.data.data_hint import (
        S,
        T,
        GenericUserDefined,
        GenericUserDefinedMultiple,
        TypeAlias,
        TypingUserDefined,
    )

    # Tuple of PEP 484 types parametrized by one or more type variables.
    TYPEVARED_TYPES = (
        typing.Union[str, typing.Iterable[typing.Tuple[S, T]]],
        GenericUserDefined,
        GenericUserDefinedMultiple,
        TypeAlias,
        TypeAlias[T],
    )

    # Tuple of PEP 484 types *NOT* parametrized by one or more type variables.
    NON_TYPEVARED_TYPES = (
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
        S,
        T,
    )

    # Assert that various "TypeVar"-centric types are correctly detected.
    for typevared_type in TYPEVARED_TYPES:
        print('"TypeVar"-parametrized type: {!r}'.format(typevared_type))
        assert is_hint_typing_typevared(typevared_type) is True

    # Assert that various "TypeVar"-agnostic types are correctly detected.
    for non_typevared_type in NON_TYPEVARED_TYPES:
        print('"TypeVar"-unparametrized type: {!r}'.format(non_typevared_type))
        assert is_hint_typing_typevared(non_typevared_type) is False
