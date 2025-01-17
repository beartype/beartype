#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator call metadata dataclass** unit tests.

This submodule unit tests the :func:`beartype._check.metadata.metadecor`
submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_metadata_decor() -> None:
    '''
    Test the :func:`beartype._check.metadata.metadecor.BeartypeDecorMeta`
    dataclass.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import BeartypeConf
    from beartype.roar import BeartypeDecorWrappeeException
    from beartype._check.metadata.metadecor import BeartypeDecorMeta
    from beartype_test.a00_unit.data.data_type import function_lambda
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Arbitrary beartype decorator call metadata.
    bear_data = BeartypeDecorMeta()

    # ....................{ FAIL                           }....................
    # Assert this metadata to be unhashable.
    with raises(TypeError):
        hash(bear_data)

    # Assert that reinitializing this metadata an uncallable object to be
    # type-checked raises the expected exception.
    with raises(BeartypeDecorWrappeeException):
        bear_data.reinit(
            func='The fields, the lakes, the forests, and the streams,',
            conf=BeartypeConf(),
        )

    # Assert that reinitializing this metadata an uncallable object to be
    # unwrapped raises the expected exception.
    with raises(BeartypeDecorWrappeeException):
        bear_data.reinit(
            func=function_lambda,
            conf=BeartypeConf(),
            wrapper="Like serpents struggling in a vulture's grasp.",
        )

    # Assert that reinitializing this metadata with a C-based builtin function
    # raises the expected exception.
    with raises(BeartypeDecorWrappeeException):
        bear_data.reinit(func=iter, conf=BeartypeConf())

    # Assert that reinitializing this metadata with an invalid configuration
    # raises the expected exception.
    with raises(BeartypeDecorWrappeeException):
        bear_data.reinit(
            func=function_lambda,
            conf='Ocean, and all the living things that dwell',
        )

    # Assert that reinitializing this metadata with invalid class stacks raises
    # the expected exception.
    with raises(BeartypeDecorWrappeeException):
        bear_data.reinit(
            func=function_lambda,
            conf=BeartypeConf(),
            cls_stack="Shine in the rushing torrents' restless gleam,",
        )
    with raises(BeartypeDecorWrappeeException):
        bear_data.reinit(
            func=function_lambda,
            conf=BeartypeConf(),
            cls_stack=('Which from those secret chasms in tumult welling',),
        )
