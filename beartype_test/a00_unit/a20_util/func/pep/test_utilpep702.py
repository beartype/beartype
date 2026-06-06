#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
:pep:`702`-compliant **callable utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.pep.utilpep702` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS                              }....................
@skip_if_python_version_less_than('3.13.0')
def test_is_func_pep702() -> None:
    '''
    Test the :func:`beartype._util.func.pep.utilpep702func.is_func_pep702`
    tester if the active Python interpreter targets Python >= 3.13 and thus
    supports :pep:`702` *or* silently reduce to a noop otherwise.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.func.pep.utilpep702 import is_func_pep702
    from warnings import deprecated

    # ....................{ CALLABLES                      }....................
    @deprecated('Manifestations of that beauteous life')
    def manifestations_of_that() -> None:
        '''
        Arbitrary callable decorated by the
        :pep:`702`-compliant :func:`warnings.deprecated` decorator.
        '''

        pass


    def beauteous_life() -> None:
        '''
        Arbitrary callable *not* decorated by the
        :pep:`702`-compliant :func:`warnings.deprecated` decorator.
        '''

        pass

    # ....................{ PASS                           }....................
    # Assert that this tester accepts an arbitrary callable decorated by the
    # @warnings.deprecated decorator.
    assert is_func_pep702(manifestations_of_that) is True

    # ....................{ FAIL                           }....................
    # Assert that this tester rejects an arbitrary callable *NOT* decorated by
    # the @warnings.deprecated decorator.
    assert is_func_pep702(beauteous_life) is False
