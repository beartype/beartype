#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator dataclass unit tests.**

This submodule unit tests the :func:`beartype._check.checkcall` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_beartypecall() -> None:
    '''
    Test the :func:`beartype._check.checkcall.BeartypeCall` dataclass.
    '''

    # Defer test-specific imports.
    from beartype import BeartypeConf
    from beartype.roar import BeartypeDecorWrappeeException
    from beartype._check.checkcall import BeartypeCall
    from pytest import raises

    # Arbitrary beartype metadata.
    bear_data = BeartypeCall()

    # Assert this metadata to be unhashable.
    with raises(TypeError):
        hash(bear_data)

    # Assert that reinitializing this metadata a non-callable raises the
    # expected exception.
    with raises(BeartypeDecorWrappeeException):
        bear_data.reinit(
            func='The fields, the lakes, the forests, and the streams,',
            conf=BeartypeConf(),
        )

    # Assert that reinitializing this metadata with a C-based builtin function
    # raises the expected exception.
    with raises(BeartypeDecorWrappeeException):
        bear_data.reinit(func=iter, conf=BeartypeConf())

    # Assert that reinitializing this metadata with an invalid configuration
    # raises the expected exception.
    with raises(BeartypeDecorWrappeeException):
        bear_data.reinit(
            func=lambda: ...,
            conf='Ocean, and all the living things that dwell',
        )

    # Assert that reinitializing this metadata with invalid class stacks raises
    # the expected exception.
    with raises(BeartypeDecorWrappeeException):
        bear_data.reinit(
            func=lambda: ...,
            conf=BeartypeConf(),
            cls_stack="Shine in the rushing torrents' restless gleam,",
        )
    with raises(BeartypeDecorWrappeeException):
        bear_data.reinit(
            func=lambda: ...,
            conf=BeartypeConf(),
            cls_stack=('Which from those secret chasms in tumult welling',),
        )
