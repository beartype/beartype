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
        P484_HINT_TO_ATTRS, NONPEP_HINTS,)

    # Assert that various "typing" types are correctly detected.
    for pep_hint, typing_attrs in P484_HINT_TO_ATTRS.items():
        print('PEP hint: {!r}'.format(pep_hint))
        assert get_hint_typing_attrs_untypevared_or_none(pep_hint) == (
            typing_attrs)

    # Assert that various non-"typing" types are correctly detected.
    for nonpep_hint in NONPEP_HINTS:
        print('Non-PEP hint: {!r}'.format(nonpep_hint))
        assert get_hint_typing_attrs_untypevared_or_none(nonpep_hint) is None
