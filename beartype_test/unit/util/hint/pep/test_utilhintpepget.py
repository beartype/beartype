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
def test_get_hint_typing_attrs_untypevared_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpepget.get_hint_typing_attrs_untypevared_or_none`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpepget import (
        get_hint_typing_attrs_untypevared_or_none)
    from beartype_test.unit.data.data_hint import (
        PEP_HINT_TO_META, NONPEP_HINTS,)

    # Assert that various "typing" types are correctly detected.
    for pep_hint, pep_hint_meta in PEP_HINT_TO_META.items():
        print('PEP hint: {!r}'.format(pep_hint))
        assert get_hint_typing_attrs_untypevared_or_none(pep_hint) == (
            pep_hint_meta.attrs_untypevared)

    # Assert that various non-"typing" types are correctly detected.
    for nonpep_hint in NONPEP_HINTS:
        print('Non-PEP hint: {!r}'.format(nonpep_hint))
        assert get_hint_typing_attrs_untypevared_or_none(nonpep_hint) is None


def get_hint_typing_super_attrs() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.utilhintpepget.get_hint_typing_super_attrs`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.pep.utilhintpepget import (
        get_hint_typing_super_attrs)
    from beartype_test.unit.data.data_hint import (
        PEP_HINT_TO_META, NONPEP_HINTS,)

    # Assert that various "typing" types are correctly detected.
    for pep_hint, pep_hint_meta in PEP_HINT_TO_META.items():
        print('PEP hint: {!r}'.format(pep_hint))
        assert get_hint_typing_super_attrs(pep_hint) == (
            pep_hint_meta.super_attrs)

    # Assert that various non-"typing" types are correctly detected.
    for nonpep_hint in NONPEP_HINTS:
        print('Non-PEP hint: {!r}'.format(nonpep_hint))
        assert get_hint_typing_super_attrs(nonpep_hint) == ()
