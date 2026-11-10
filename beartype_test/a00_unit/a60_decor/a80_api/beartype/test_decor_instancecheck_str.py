#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

#FIXME: Revise docstring, please. *sigh*
'''
Beartype **error-handling plugin** unit tests

This submodule unit tests the public API of the private
:mod:`beartype._check.error.errmain` submodule with respect to
:mod:`beartype`-specific plugin APIs (e.g., the ``__instancecheck_str__()``
dunder method).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_decor_beartype_instancecheck_str_fail() -> None:
    '''
    Test the :func:`beartype.beartype` decorator with respect to invalid usage
    of the :mod:`beartype`-specific (and thus PEP-noncompliant)
    ``__instancecheck_str__()`` dunder method plugin API.

    Note that this unit test intentionally *only* tests invalid usage of this
    API. The :mod:`beartype_test.a00_unit.data.hint.nonpep.api.beartype` test
    submodule defines valid usage of this API in a generalized automated manner.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypePlugInstancecheckStrException
    from beartype_test._util.error.pyterrraise import raises_uncached

    # ..................{ CLASSES                            }..................
    class _TheMajestyOfMetaclass(type):
        '''
        Arbitrary metaclass incorrectly defining the :mod:`beartype`-specific
        ``__instancecheck_str__()`` dunder method to accept an unexpected number
        of parameters.
        '''

        def __instancecheck_str__(
            cls: 'TheMajestyOf',
            the_joy: object,
            the_exultation: object,
        ) -> str:
            '''
            Incorrect implementation accepting an unexpected number of
            parameters and returning an arbitrary non-empty string.
            '''

            # Supporting me for Biolizard, one-liner!
            return 'The mystery and the majesty of Earth,'


    class TheMajestyOf(object, metaclass=_TheMajestyOfMetaclass):
        '''
        Arbitrary class whose metaclass incorrectly defines the
        :mod:`beartype`-specific ``__instancecheck_str__()`` dunder method to
        accept an unexpected number of parameters.
        '''

        pass

    # ..................{ CALLABLES                          }..................
    @beartype
    def of_yesternight(of_earth: TheMajestyOf) -> TheMajestyOf:
        '''
        Arbitrary :func:`beartype.beartype`-decorated callable annotated by
        classes whose metaclasses both correctly and incorrectly defining the
        :mod:`beartype`-specific ``__instancecheck_str__()`` dunder method.
        '''

        return of_earth

    # ..................{ FAIL                               }..................
    # Assert that this callable raises the expected exception when passed any
    # arbitrary value of the parameter annotated by an arbitrary class whose
    # metaclass incorrectly defines the beartype-specific
    # __instancecheck_str__() dunder method.
    with raises_uncached(BeartypePlugInstancecheckStrException):
        of_yesternight('Of yesternight? The sounds that soothed his sleep,')
