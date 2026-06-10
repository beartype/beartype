#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :mod:`warnings` utility unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.api.standard.utilwarnings` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS                              }....................
@skip_if_python_version_less_than('3.13.0')
def test_is_func_warnings_deprecated() -> None:
    '''
    Test the
    :func:`beartype._util.api.standard.utilwarnings.is_func_warnings_deprecated`
    tester if the active Python interpreter targets Python >= 3.13 and thus
    supports :pep:`702` *or* silently reduce to a noop otherwise.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.api.standard.utilwarnings import (
        is_func_warnings_deprecated)
    from beartype._util.func.utilfuncwrap import unwrap_func_once
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

    # ....................{ LOCALS                         }....................
    # Original callable decorated by the @warnings.deprecated decorator above.
    manifestations_of_that_func = unwrap_func_once(manifestations_of_that)

    # ....................{ PASS                           }....................
    # Assert that this tester accepts an arbitrary callable decorated by the
    # @warnings.deprecated decorator.
    assert is_func_warnings_deprecated(manifestations_of_that) is True

    # ....................{ FAIL                           }....................
    # Assert that this tester rejects the original callable decorated by the
    # @warnings.deprecated decorator above. While seemingly senseless, this
    # assertion validates a subtle edge case with respect to this decorator.
    assert is_func_warnings_deprecated(manifestations_of_that_func) is False

    # Assert that this tester rejects an arbitrary callable *NOT* decorated by
    # the @warnings.deprecated decorator.
    assert is_func_warnings_deprecated(beauteous_life) is False
