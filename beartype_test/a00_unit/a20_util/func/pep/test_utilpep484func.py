#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
:pep:`484`-compliant **callable utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.pep.utilfuncpep484` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_is_func_pep484_notypechecked() -> None:
    '''
    Test the
    :func:`beartype._util.func.pep.utilfuncpep484.is_func_pep484_notypechecked`
    tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.func.pep.utilfuncpep484 import (
        is_func_pep484_notypechecked)
    from typing import no_type_check

    # ....................{ CALLABLES                      }....................
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

    # ....................{ PASS                           }....................
    # Assert that this tester accepts an arbitrary callable decorated by the
    # @typing.no_type_check decorator.
    assert is_func_pep484_notypechecked(
        now_float_above_thy_darkness) is True

    # ....................{ FAIL                           }....................
    # Assert that this tester rejects an arbitrary callable *NOT* decorated by
    # the @typing.no_type_check decorator.
    assert is_func_pep484_notypechecked(and_now_rest) is False
