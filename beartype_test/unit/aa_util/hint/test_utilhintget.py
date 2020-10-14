#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-agnostic type hint getter utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.utilhintget` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# from pytest import raises

# ....................{ TESTS                             }....................
def test_get_hint_type_origin_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.hint.utilhintget.get_hint_type_origin_or_none`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype._util.hint.utilhintget import get_hint_type_origin_or_none
    from beartype._util.hint.pep.utilhintpepdata import (
        TYPING_ATTR_TO_TYPE_ORIGIN)

    # Assert this function accepts non-"typing" types.
    assert get_hint_type_origin_or_none(str) is str

    # Assert this function accepts all instanceable argumentless "typing"
    # attributes.
    for hint_attr, supercls in TYPING_ATTR_TO_TYPE_ORIGIN.items():
        # Non-"typing" type originating this attribute.
        hint_type_origin = get_hint_type_origin_or_none(hint_attr)

        # Assert this type to be the expected non-"typing" type.
        #
        # Note that we intentionally do *NOT* assert this type to actually be a
        # non-"typing" type. Why? Because some origin types under some Python
        # versions are actually standard types (e.g., "typing.SupportsRound").
        assert hint_type_origin is supercls

    # Assert this function rejects objects that are *NOT* instanceable.
    assert get_hint_type_origin_or_none(
        'Growth for the sake of growth '
        'is the ideology of the cancer cell.') is None
