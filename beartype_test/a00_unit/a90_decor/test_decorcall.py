#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator dataclass unit tests.**

This submodule unit tests the :func:`beartype._decor._decorcall` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_decor_data() -> None:
    '''
    Test usage of the :func:`beartype._decor._decorcall.BeartypeCall` dataclass.
    '''

    # Defer heavyweight imports.
    from beartype import BeartypeConf
    from beartype.roar import BeartypeDecorWrappeeException
    from beartype._decor._decorcall import BeartypeCall
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
            func_conf=BeartypeConf(),
        )

    # Assert that reinitializing this metadata with a C-based builtin function
    # raises the expected exception.
    with raises(BeartypeDecorWrappeeException):
        bear_data.reinit(func=iter, func_conf=BeartypeConf())

    # Assert that reinitializing this metadata with a non-configuration raises
    # the expected exception.
    with raises(BeartypeDecorWrappeeException):
        bear_data.reinit(
            func=lambda: ...,
            func_conf='Ocean, and all the living things that dwell',
        )

    # Assert that reinitializing this metadata with a non-class raises the
    # expected exception.
    with raises(BeartypeDecorWrappeeException):
        bear_data.reinit(
            func=lambda: ...,
            func_conf=BeartypeConf(),
            cls_owner="Shine in the rushing torrents' restless gleam,",
        )
