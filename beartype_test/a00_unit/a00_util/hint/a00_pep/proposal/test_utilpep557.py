#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`557` **type hint utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.utilpep557` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ getter                    }....................
def test_get_hint_pep557_initvar_arg() -> None:
    '''
    Test usage of the private
    :mod:`beartype._util.hint.pep.proposal.utilpep557.get_hint_pep557_initvar_arg`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintPep557Exception
    from beartype._util.hint.pep.proposal.utilpep557 import (
        get_hint_pep557_initvar_arg)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
    from pytest import raises

    # If the active Python interpreter targets at least Python >= 3.8 and thus
    # supports PEP 557...
    if IS_PYTHON_AT_LEAST_3_8:
        # Defer version-specific imports.
        from dataclasses import InitVar

        # Assert this getter returns the argument subscripting an InitVar.
        assert get_hint_pep557_initvar_arg(InitVar[str]) is str

    # Assert this tester raises the expected exception when passed a
    # non-InitVar.
    with raises(BeartypeDecorHintPep557Exception):
        get_hint_pep557_initvar_arg(
            'Large codes of fraud and woe; not understood')
