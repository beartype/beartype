#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`557` **type hint utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep557` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ getter                     }....................
def test_get_hint_pep557_initvar_arg() -> None:
    '''
    Test the public
    :mod:`beartype._util.hint.pep.proposal.pep557.get_hint_pep557_initvar_arg`
    getter.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep557Exception
    from beartype._util.hint.pep.proposal.pep557 import (
        get_hint_pep557_initvar_arg)
    from dataclasses import InitVar
    from pytest import raises

    # Assert that this getter returns the argument subscripting an InitVar.
    assert get_hint_pep557_initvar_arg(InitVar[str]) is str

    # Assert that this getter raises the expected exception when passed a
    # non-InitVar.
    with raises(BeartypeDecorHintPep557Exception):
        get_hint_pep557_initvar_arg(
            'Large codes of fraud and woe; not understood')


def test_get_func_pep557_init_arg_default_factory() -> None:
    '''
    Test the public
    :mod:`beartype._util.hint.pep.proposal.pep557.get_func_pep557_init_arg_default_factory`
    getter.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep557 import (
        get_func_pep557_init_arg_default_factory)
    from dataclasses import _HAS_DEFAULT_FACTORY

    # PEP 557-compliant dataclass constructor default factory.
    FUNC_PEP557_INIT_ARG_DEFAULT_FACTORY = (
        get_func_pep557_init_arg_default_factory())

    # Assert that this factory is the expected private magic constant internal
    # to the standard "dataclasses" module.
    #
    # Note that violating privacy encapsulation renders this test fragile
    # against new CPython versions, but that doing so here is still superior to
    # doing so in the main codebase. It is what it is. So, we sigh. *megasigh*
    assert FUNC_PEP557_INIT_ARG_DEFAULT_FACTORY is _HAS_DEFAULT_FACTORY
