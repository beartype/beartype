#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
:pep:`484`-compliant **callable utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.pep.utilpep484func` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_is_func_pep484_notypechecked() -> None:
    '''
    Test the
    :func:`beartype._util.func.pep.utilpep484func.is_func_pep484_notypechecked`
    tester.
    '''

    # Defer test-specific imports.
    from beartype._util.func.pep.utilpep484func import (
        is_func_pep484_notypechecked)
    from typing import no_type_check

    @no_type_check
    def now_float_above_thy_darkness() -> None:
        '''
        Arbitrary callable decorated by the
        :pep:`484`-compliant :func:`typing.no_type_check` decorator.
        '''

        pass

    def and_now_rest() -> None:
        '''
        Arbitrary callable *not* decorated by the
        :pep:`484`-compliant :func:`typing.no_type_check` decorator.
        '''

        pass

    # Assert this tester returns the expected results for these callables.
    assert is_func_pep484_notypechecked(
        now_float_above_thy_darkness) is True
    assert is_func_pep484_notypechecked(
        and_now_rest) is False
