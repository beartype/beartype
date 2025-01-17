#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype error-handling plugin unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._check.error.errget` submodule with respect to
:mod:`beartype`-specific plugin APIs (e.g., the ``__instancecheck_str__()``
dunder method).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_get_func_pith_violation_instancecheck_str() -> None:
    '''
    Test the
    :func:`beartype._check.error.errget.get_func_pith_violation`
    getter with respect to the :mod:`beartype`-specific
    ``__instancecheck_str__()`` dunder method plugin API.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import BeartypeConf
    from beartype.roar import BeartypePlugInstancecheckStrException
    from beartype.typing import Any
    from beartype._check.error.errget import get_func_pith_violation
    from beartype._check.metadata.metacheck import BeartypeCheckMeta
    from pytest import raises

    # ..................{ METACLASSES                        }..................
    class TheMysteryAndMeta(type):
        '''
        Arbitrary metaclass correctly defining the :mod:`beartype`-specific
        ``__instancecheck_str__()`` dunder method.
        '''

        def __instancecheck_str__(cls, obj: Any) -> str:
            '''
            Correct implementation accepting the expected number of parameters
            and returning the passed object as is.
            '''

            # Return the passed object as is.
            return obj


    class TheMajestyOfMeta(type):
        '''
        Arbitrary metaclass incorrectly defining the :mod:`beartype`-specific
        ``__instancecheck_str__()`` dunder method to accept an unexpected number
        of parameters.
        '''

        def __instancecheck_str__(
            cls, the_joy: Any, the_exultation: Any) -> str:
            '''
            Incorrect implementation accepting an unexpected number of
            parameters and returning an arbitrary non-empty string.
            '''

            return 'The mystery and the majesty of Earth,'

    # ..................{ CLASSES                            }..................
    class TheMysteryAnd(object, metaclass=TheMysteryAndMeta):
        '''
        Arbitrary class whose metaclass correctly defines the
        :mod:`beartype`-specific ``__instancecheck_str__()`` dunder method.
        '''

        pass


    class TheMajestyOf(object, metaclass=TheMajestyOfMeta):
        '''
        Arbitrary class whose metaclass incorrectly defines the
        :mod:`beartype`-specific ``__instancecheck_str__()`` dunder method to
        accept an unexpected number of parameters.
        '''

        pass

    # ..................{ LOCALS                             }..................
    def of_yesternight(
        the_sounds_that: TheMysteryAnd,
        of_earth: TheMajestyOf,
    ) -> TheMysteryAnd:
        '''
        Arbitrary callable annotated by classes whose metaclasses both correctly
        and incorrectly defining the :mod:`beartype`-specific
        ``__instancecheck_str__()`` dunder method.
        '''

        return the_sounds_that

    # Keyword arguments to be unconditionally passed to *ALL* calls of the
    # get_func_pith_violation() getter below.
    kwargs = dict(
        check_meta=BeartypeCheckMeta.make_from_decor_meta_kwargs(
            func=of_yesternight, conf=BeartypeConf()))

    # Arbitrary non-empty string.
    HIS_WAN_EYES = 'Of yesternight? The sounds that soothed his sleep,'

    # ..................{ PASS                               }..................
    # Violation exception created and returned by this getter for a hypothetical
    # call of the function defined above when passed a non-empty string as the
    # value of the parameter annotated by an arbitrary class whose metaclass
    # correctly defines __instancecheck_str__().
    violation = get_func_pith_violation(
        pith_name='the_sounds_that',
        pith_value=HIS_WAN_EYES,
        **kwargs
    )

    # Message of this violation.
    violation_str = str(violation)

    # Assert that this violation contains the passed non-empty string.
    assert HIS_WAN_EYES in violation_str

    # ..................{ FAIL                               }..................
    # Assert that this getter raises the expected exception for a hypothetical
    # call of the function defined above when passed an arbitrary non-string
    # object as the value of the parameter annotated by an arbitrary class whose
    # metaclass correctly defines __instancecheck_str__().
    with raises(BeartypePlugInstancecheckStrException):
        get_func_pith_violation(
            pith_name='the_sounds_that',
            pith_value=b"As ocean's moon looks on the moon in heaven.",
            **kwargs
        )

    # Assert that this getter raises the expected exception for a hypothetical
    # call of the function defined above when passed an empty string as the
    # value of the parameter annotated by an arbitrary class whose metaclass
    # correctly defines __instancecheck_str__().
    with raises(BeartypePlugInstancecheckStrException):
        get_func_pith_violation(
            pith_name='the_sounds_that',
            pith_value='',
            **kwargs
        )

    # Assert that this getter raises the expected exception for a hypothetical
    # call of the function defined above when passed a non-empty string as the
    # value of the parameter annotated by an arbitrary class whose metaclass
    # incorrectly defines __instancecheck_str__().
    with raises(BeartypePlugInstancecheckStrException):
        get_func_pith_violation(
            pith_name='of_earth',
            pith_value='Gaze on the empty scene as vacantly',
            **kwargs
        )
