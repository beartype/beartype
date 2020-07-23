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
# import typing

# ....................{ TESTS                             }....................
def test_get_hint_typing_attrs_untypevared() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpepget.get_hint_typing_attrs_untypevared`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpepget import (
        get_hint_typing_attrs_untypevared)
    from beartype_test.unit.data.data_hint import (
        NONPEP_HINTS, PEP_HINT_TO_META,)

    # Assert that various "typing" types are correctly detected.
    for pep_hint, pep_hint_meta in PEP_HINT_TO_META.items():
        print('PEP hint: {!r}'.format(pep_hint))
        assert get_hint_typing_attrs_untypevared(pep_hint) == (
            pep_hint_meta.attrs_untypevared)

    # Assert that various non-"typing" types are correctly detected.
    for nonpep_hint in NONPEP_HINTS:
        print('Non-PEP hint: {!r}'.format(nonpep_hint))
        assert get_hint_typing_attrs_untypevared(nonpep_hint) is ()

# ....................{ TESTS ~ superattrs                }....................
def get_hint_typing_superattrs() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpepget.get_hint_typing_superattrs`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpepget import (
        get_hint_typing_superattrs)
    from beartype_test.unit.data.data_hint import (
        NONPEP_HINTS, PEP_HINT_TO_META,)

    # Assert that various "typing" types are correctly detected.
    for pep_hint, pep_hint_meta in PEP_HINT_TO_META.items():
        print('PEP hint: {!r}'.format(pep_hint))
        assert get_hint_typing_superattrs(pep_hint) == (
            pep_hint_meta.superattrs)

    # Assert that various non-"typing" types are correctly detected.
    for nonpep_hint in NONPEP_HINTS:
        print('Non-PEP hint: {!r}'.format(nonpep_hint))
        assert get_hint_typing_superattrs(nonpep_hint) == ()


def get_hint_typing_superattrs_untypevared() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpepget.get_hint_typing_superattrs_untypevared`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpepget import (
        get_hint_typing_superattrs_untypevared)
    from beartype_test.unit.data.data_hint import (
        NONPEP_HINTS, PEP_HINT_TO_META,)

    # Assert that various "typing" types are correctly detected.
    for pep_hint, pep_hint_meta in PEP_HINT_TO_META.items():
        print('PEP hint: {!r}'.format(pep_hint))
        assert get_hint_typing_superattrs_untypevared(pep_hint) == (
            pep_hint_meta.superattrs_untypevared)

    # Assert that various non-"typing" types are correctly detected.
    for nonpep_hint in NONPEP_HINTS:
        print('Non-PEP hint: {!r}'.format(nonpep_hint))
        assert get_hint_typing_superattrs_untypevared(nonpep_hint) == ()
