#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint getter utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.utilhintpepget` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_get_hint_pep_typing_attrs_argless_to_args() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpepget.get_hint_pep_typing_attr_to_args`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpepget import (
        get_hint_pep_typing_attr_to_args)
    from beartype_test.unit.data.data_hint import (
        S, T, NONPEP_HINTS, PEP_HINT_TO_META,)

    # Assert that various "typing" types are correctly detected.
    for pep_hint, pep_hint_meta in PEP_HINT_TO_META.items():
        assert get_hint_pep_typing_attr_to_args(pep_hint) == (
            pep_hint_meta.attrs_argless_to_args)

    # Assert that various non-"typing" types are correctly detected.
    for nonpep_hint in NONPEP_HINTS:
        assert get_hint_pep_typing_attr_to_args(nonpep_hint) == {}

    # Assert that this getter returns the same non-empty dictionary for two
    # arbitrarily different "typing" type variables.
    assert (
        get_hint_pep_typing_attr_to_args(S) is
        get_hint_pep_typing_attr_to_args(T))

    # Assert that this getter returns the same empty dictionary for two
    # arbitrarily different non-"typing" types.
    assert (
        get_hint_pep_typing_attr_to_args(NONPEP_HINTS[0]) is
        get_hint_pep_typing_attr_to_args(NONPEP_HINTS[1]))

# ....................{ TESTS ~ super                     }....................
def test_get_hint_pep_typing_superattrs() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpepget._get_hint_pep_typing_superobjects`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpepget import (
        _get_hint_pep_typing_superobjects)
    from beartype_test.unit.data.data_hint import (
        NONPEP_HINTS, PEP_HINT_TO_META,)

    # Assert that various "typing" types are correctly detected.
    for pep_hint, pep_hint_meta in PEP_HINT_TO_META.items():
        assert _get_hint_pep_typing_superobjects(pep_hint) == (
            pep_hint_meta.superattrs)

    # Assert that various non-"typing" types are correctly detected.
    for nonpep_hint in NONPEP_HINTS:
        assert _get_hint_pep_typing_superobjects(nonpep_hint) == ()


#FIXME: Remove after excising the corresponding getter, which will shortly
#become irrelevant.
# def test_get_hint_pep_typing_superattrs_argless_to_args() -> None:
#     '''
#     Test the
#     :func:`beartype._util.hint.pep.utilhintpepget._get_hint_pep_typing_superattrs_argless_to_args`
#     getter.
#     '''
#
#     # Defer heavyweight imports.
#     from beartype._util.hint.pep.utilhintpepget import (
#         _get_hint_pep_typing_superattrs_argless_to_args)
#     from beartype_test.unit.data.data_hint import (
#         NONPEP_HINTS, PEP_HINT_TO_META,)
#
#     # Assert that various "typing" types are correctly detected.
#     for pep_hint, pep_hint_meta in PEP_HINT_TO_META.items():
#         assert _get_hint_pep_typing_superattrs_argless_to_args(pep_hint) == (
#             pep_hint_meta.superattrs_argless_to_args)
#
#     # Assert that various non-"typing" types are correctly detected.
#     for nonpep_hint in NONPEP_HINTS:
#         assert _get_hint_pep_typing_superattrs_argless_to_args(
#             nonpep_hint) == {}
