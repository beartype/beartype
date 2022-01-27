#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator dataclass unit tests.**

This submodule unit tests the :func:`beartype._decor._call` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_decor_data() -> None:
    '''
    Test usage of the :func:`beartype._decor._call.BeartypeCall` dataclass.
    '''

    # Defer heavyweight imports.
    from beartype import BeartypeConf
    from beartype.roar import BeartypeDecorWrappeeException
    from beartype._decor._call import BeartypeCall
    from pytest import raises

    # Arbitrary beartype metadata.
    bear_data = BeartypeCall()

    # Assert this metadata to be unhashable.
    with raises(TypeError):
        hash(bear_data)

    # Assert that reinitializing this metadata with invalid parameters raises
    # the expected exceptions.
    with raises(BeartypeDecorWrappeeException):
        bear_data.reinit(
            func='The fields, the lakes, the forests, and the streams,',
            conf=BeartypeConf(),
        )
    with raises(BeartypeDecorWrappeeException):
        bear_data.reinit(
            func=lambda: ...,
            conf='Ocean, and all the living things that dwell',
        )
    with raises(BeartypeDecorWrappeeException):
        bear_data.reinit(func=iter, conf=BeartypeConf())
