#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`557` **type hint utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.utilpep557` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ getter                     }....................
def test_get_hint_pep557_initvar_arg() -> None:
    '''
    Test usage of the private
    :mod:`beartype._util.hint.pep.proposal.utilpep557.get_hint_pep557_initvar_arg`
    getter.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep557Exception
    from beartype._util.hint.pep.proposal.utilpep557 import (
        get_hint_pep557_initvar_arg)
    from dataclasses import InitVar
    from pytest import raises

    # Assert this getter returns the argument subscripting an InitVar.
    assert get_hint_pep557_initvar_arg(InitVar[str]) is str

    # Assert this tester raises the expected exception when passed a
    # non-InitVar.
    with raises(BeartypeDecorHintPep557Exception):
        get_hint_pep557_initvar_arg(
            'Large codes of fraud and woe; not understood')
