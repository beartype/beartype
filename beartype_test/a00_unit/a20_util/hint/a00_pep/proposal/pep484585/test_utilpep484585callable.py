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

# ....................{ TESTS                              }....................
#FIXME: Exercise get_hint_pep484585_callable_params() here as well, please.
def test_get_hint_pep484585_callable_args_and_params() -> None:
    '''
    Test both the ``get_hint_pep484585_callable_args`` and
    ``get_hint_pep484585_callable_params`` declared by the
    :mod:`beartype._util.hint.pep.proposal.pep484585.utilpep484585callable`
    submodule.

    Since these getters are inextricably interrelated, this unit test exercises
    both within the same test to satisfy Don't Repeat Yourself (DRY).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintPep484585Exception
    from beartype._data.hint.pep.sign.datapepsigns import HintSignCallable
    from beartype._util.hint.pep.proposal.pep484585.utilpep484585callable import (
        get_hint_pep484585_callable_args)
    from beartype_test.a00_unit.data.hint.data_hint import NOT_HINTS_PEP
    from beartype_test.a00_unit.data.hint.pep.data_pep import HINTS_PEP_META
    from pytest import raises

    # ..................{ GENERIC                            }..................
    # General-purpose logic generically exercising these getters against all
    # globally defined type hints.

    # Assert these getters...
    for hint_pep_meta in HINTS_PEP_META:
        # Return zero or more arguments for PEP-compliant callable type hints.
        if hint_pep_meta.pep_sign is HintSignCallable:
            hint_callable_args = get_hint_pep484585_callable_args(
                hint_pep_meta.hint)
            assert isinstance(hint_callable_args, tuple)
        # Raise an exception for concrete PEP-compliant type hints *NOT*
        # defined by the "typing" module.
        else:
            with raises(BeartypeDecorHintPep484585Exception):
                get_hint_pep484585_callable_args(hint_pep_meta.hint)

    # Assert these getters raise the expected exception for non-PEP-compliant
    # type hints.
    for not_hint_pep in NOT_HINTS_PEP:
        with raises(BeartypeDecorHintPep484585Exception):
            get_hint_pep484585_callable_args(not_hint_pep)
