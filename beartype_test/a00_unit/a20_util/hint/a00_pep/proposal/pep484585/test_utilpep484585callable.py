#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484` and :pep:`585` **callable type hint utility unit
tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep484585.utilpep484585callable` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ kind : callable             }....................
def test_get_hint_pep484585_callable_args() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484585.utilpep484585callable.get_hint_pep484585_callable_args`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintPep484585Exception
    from beartype._data.hint.pep.sign.datapepsigns import HintSignCallable
    from beartype._util.hint.pep.proposal.pep484585.utilpep484585callable import (
        get_hint_pep484585_callable_args)
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import HINTS_PEP_META
    from pytest import raises

    # Assert this getter...
    for hint_pep_meta in HINTS_PEP_META:
        # Returns zero or more arguments for PEP-compliant callable type hints.
        if hint_pep_meta.pep_sign is HintSignCallable:
            hint_callable_args = get_hint_pep484585_callable_args(
                hint_pep_meta.hint)
            assert isinstance(hint_callable_args, tuple)
        # Raises an exception for concrete PEP-compliant type hints *NOT*
        # defined by the "typing" module.
        else:
            with raises(BeartypeDecorHintPep484585Exception):
                get_hint_pep484585_callable_args(hint_pep_meta.hint)

    #FIXME: *UGH.* This unhelpfully raises a
    #"BeartypeDecorHintPepSignException". Let's generalize our low-level
    #get_hint_pep_sign() getter to accept an optional "exception_cls", please.
    # # Assert this getter raises the expected exception for non-PEP-compliant
    # # type hints.
    # for not_hint_pep in NOT_HINTS_PEP:
    #     with raises(BeartypeDecorHintPep484585Exception):
    #         get_hint_pep484585_callable_args(not_hint_pep)
