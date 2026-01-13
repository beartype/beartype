#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **third-party NumPy type hint reduction** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._check.convert._reduce.redmain` submodule with respect to
third-party NumPy-specific type hints.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ reducers                   }....................
def test_reduce_hint_api_numpy() -> None:
    '''
    Test the private
    :func:`beartype._check.convert._reduce.redmain.reduce_hint` reducer with
    respect to third-party NumPy-specific type hints.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype._check.convert._reduce.redmain import reduce_hint
    from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign
    from beartype._data.hint.sign.datahintsigns import HintSignAnnotated
    from beartype_test._util.module.pytmodtest import is_package_numpy
    from pytest import raises

    # ..................{ API ~ numpy                        }..................
    # If a recent version of NumPy is importable...
    if is_package_numpy():
        # Defer API-specific imports.
        from beartype.roar import BeartypeDecorHintNonpepNumpyException
        from numpy import float64
        from numpy.typing import NDArray

        # Metadata encapsulating the reduction of a NumPy array type hint to a
        # beartype validator.
        ndarray_reduced_sane = reduce_hint(NDArray[float64])

        # This beartype validator.
        ndarray_reduced = ndarray_reduced_sane.hint

        # Assert this validator is a "typing{_extensions}.Annotated" hint.
        assert get_hint_pep_sign(ndarray_reduced) is HintSignAnnotated

        # Assert that reducing a "numpy.typing.NDArray" type hint
        # erroneously subscripted by an object *NOT* reducible to a data
        # type raises the expected exception.
        with raises(BeartypeDecorHintNonpepNumpyException):
            reduce_hint(NDArray['From_my_wings_are_shaken_the_dews_that_waken'])
    # Else, a recent version of NumPy is *NOT* importable.
