#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`585` **utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep585` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_is_hint_pep585_builtin(hints_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep585.is_hint_pep585_builtin_subbed`
    function.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        List of type hint metadata describing sample type hints exercising edge
        cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep585 import (
        is_hint_pep585_builtin_subbed)

    # Assert this tester accepts only PEP 585-compliant type hints.
    for hint_pep_meta in hints_pep_meta:
        assert is_hint_pep585_builtin_subbed(hint_pep_meta.hint) is (
            hint_pep_meta.is_pep585_builtin_subbed)


def test_is_hint_pep585_generic(hints_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep585.is_hint_pep585_generic`
    function.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        List of type hint metadata describing sample type hints exercising edge
        cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep585 import (
        is_hint_pep585_generic)

    # Assert this tester accepts only PEP 585-compliant generics.
    for hint_pep_meta in hints_pep_meta:
        assert is_hint_pep585_generic(hint_pep_meta.hint) is (
            hint_pep_meta.is_pep585_generic)

# ....................{ TESTS ~ getter                     }....................
def test_get_hint_pep585_generic_typeargs_packed(hints_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep585.get_hint_pep585_generic_typeargs_packed`
    function.

    Parameters
    ----------
    hints_pep_meta : List[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        List of type hint metadata describing sample type hints exercising edge
        cases in the :mod:`beartype` codebase.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep585Exception
    from beartype._data.hint.sign.datahintsigns import HintSignTypeVar
    from beartype._util.hint.pep.proposal.pep585 import (
        get_hint_pep585_generic_typeargs_packed)
    from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign_or_none
    from pytest import raises

    # ....................{ ASSERTS                        }....................
    # For each PEP-compliant test hint...
    for hint_pep_meta in hints_pep_meta:
        # If this hint is a PEP 585-compliant generic...
        if hint_pep_meta.is_pep585_generic:
            # Tuple of all type variables discovered by this getter.
            hint_typevars = get_hint_pep585_generic_typeargs_packed(hint_pep_meta.hint)
            assert isinstance(hint_typevars, tuple)

            # Assert that all items of this tuple are actually type variables.
            for hint_typevar in hint_typevars:
                assert get_hint_pep_sign_or_none(hint_typevar) is (
                    HintSignTypeVar)

            # If this hint is parametrized by one or more type variables...
            if hint_pep_meta.is_typeargs:
                # Assert that this getter returns one or more type variables.
                assert hint_typevars

                # If the exact type variables parametrizing this hint are known
                # at test time...
                if hint_pep_meta.typeargs_packed:
                    # Assert that this getter returns only these type variables.
                    assert hint_pep_meta.typeargs_packed == hint_typevars
                # Else, the exact type variables parametrizing this hint are
                # unknown at test time. In this case, silently ignore the exact
                # contents of this tuple.
            # Else, this hint is unparametrized by type variables. In this case,
            # assert that this getter returns the empty tuple.
            else:
                assert hint_typevars == ()
        # If this hint is *NOT* a PEP 585-compliant generic, assert that this
        # getter raises an exception.
        else:
            with raises(BeartypeDecorHintPep585Exception):
                get_hint_pep585_generic_typeargs_packed(hint_pep_meta.hint)
