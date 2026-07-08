#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
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
def test_is_hint_pep585_builtin(hints_piths_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep585.is_hint_pep585_builtin_subbed`
    function.

    Parameters
    ----------
    hints_piths_pep_meta : List[beartype_test.a00_unit.data.hint.metadata.pith.data_hintpithmeta.HintPepMetadata]
        List of type hint metadata describing sample type hints exercising edge
        cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep585 import (
        is_hint_pep585_builtin_subbed)

    # Assert this tester accepts only PEP 585-compliant type hints.
    for hint_pep_meta in hints_piths_pep_meta:
        assert is_hint_pep585_builtin_subbed(hint_pep_meta.hint) is (
            hint_pep_meta.is_pep585_builtin_subbed)


def test_is_hint_pep585_generic(hints_piths_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep585.is_hint_pep585_generic`
    function.

    Parameters
    ----------
    hints_piths_pep_meta : List[beartype_test.a00_unit.data.hint.metadata.pith.data_hintpithmeta.HintPepMetadata]
        List of type hint metadata describing sample type hints exercising edge
        cases in the :mod:`beartype` codebase.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep585 import (
        is_hint_pep585_generic)

    # Assert this tester accepts only PEP 585-compliant generics.
    for hint_pep_meta in hints_piths_pep_meta:
        assert is_hint_pep585_generic(hint_pep_meta.hint) is (
            hint_pep_meta.is_pep585_generic)

# ....................{ TESTS ~ getter                     }....................
def test_get_hint_pep585_generic_typeargs_packed(hints_piths_pep_meta) -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep585.get_hint_pep585_generic_typeargs_packed`
    function.

    Parameters
    ----------
    hints_piths_pep_meta : list[beartype_test.a00_unit.data.hint.metadata.pith.data_hintpithmeta.HintPepMetadata]
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
    from beartype_test.a00_unit.data.pep.generic.data_pep585generic import (
        Pep585SequenceTUnsubbed)
    from beartype_test.a00_unit.data.pep.pep484.data_pep484 import T
    from pytest import raises

    # ....................{ PASS                           }....................
    #FIXME: Non-ideal. Promote this to a proper "hint_pep_meta". *shrug*
    # Assert that this getter when passed a PEP 585-compliant generic subclass
    # inheriting a PEP 585-compliant generic superclass subscripted by *NO*
    # child hints and thus implicitly parametrized by the same type variable
    # parametrizing that superclass returns the 1-tuple of that type variable.
    hint_typeargs = get_hint_pep585_generic_typeargs_packed(
        Pep585SequenceTUnsubbed)
    assert hint_typeargs == (T,)

    # ....................{ ITERATE                        }....................
    # For each PEP-compliant test hint...
    for hint_pep_meta in hints_piths_pep_meta:
        # This hint, localized purely to simplify debugging. *sigh*
        hint = hint_pep_meta.hint

        # ....................{ PASS                       }....................
        # If this hint is a PEP 585-compliant generic...
        if hint_pep_meta.is_pep585_generic:
            # Tuple of all type variables discovered by this getter.
            hint_typeargs = get_hint_pep585_generic_typeargs_packed(
                hint,
                #FIXME: Kinda hacky. This parameter should probably be enabled
                #by default, but currently can't be, because ancient behaviour
                #elsewhere depends on the oldschool default of "False". *shrug*
                True,  # <-- optional "is_unsub" parameter
            )
            assert isinstance(hint_typeargs, tuple)

            # Assert that all items of this tuple are actually type variables.
            for hint_typearg in hint_typeargs:
                assert get_hint_pep_sign_or_none(hint_typearg) is (
                    HintSignTypeVar)

            # If this hint is parametrized by one or more type variables...
            if hint_pep_meta.is_typeargs:
                # Assert that this getter returns one or more type variables.
                assert hint_typeargs

                # If the exact type variables parametrizing this hint are known
                # at test time...
                if hint_pep_meta.typeargs_packed:
                    # Assert that this getter returns only these type variables.
                    assert hint_pep_meta.typeargs_packed == hint_typeargs
                # Else, the exact type variables parametrizing this hint are
                # unknown at test time. In this case, silently ignore the exact
                # contents of this tuple.
            # Else, this hint is unparametrized by type variables. In this case,
            # assert that this getter returns the empty tuple.
            else:
                assert hint_typeargs == ()
        # ....................{ FAIL                       }....................
        # If this hint is *NOT* a PEP 585-compliant generic, assert that this
        # getter raises an exception.
        else:
            with raises(BeartypeDecorHintPep585Exception):
                get_hint_pep585_generic_typeargs_packed(hint)
