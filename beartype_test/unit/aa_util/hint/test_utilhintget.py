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
    from beartype._util.hint.utilhintget import (
        get_hint_type_origin_or_none)
    from beartype._util.hint.pep.utilhintpepdata import (
        TYPING_ATTR_TO_TYPE_ORIGIN)

    # Assert this function accepts non-"typing" types.
    assert get_hint_type_origin_or_none(str) is str

    # Assert this function accepts all instanceable argumentless "typing"
    # attributes.
    for typing_attr_argless, supercls in TYPING_ATTR_TO_TYPE_ORIGIN.items():
        assert get_hint_type_origin_or_none(typing_attr_argless) is (
            supercls)

    # Assert this function rejects objects that are *NOT* instanceable.
    assert get_hint_type_origin_or_none(
        'Growth for the sake of growth '
        'is the ideology of the cancer cell.') is None
