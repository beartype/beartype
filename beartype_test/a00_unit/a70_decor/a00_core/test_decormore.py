#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Unmemoized beartype decorator unit tests.**

This submodule unit tests low-level functionality of the private
:mod:`beartype._decor.decorcore` submodule *not* already tested by higher-level
unit tests defined elsewhere.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_beartype_descriptor_decorator_builtin() -> None:
    '''
    Test the subset of the private
    :func:`beartype._decor._decormore.beartype_descriptor_decorator_builtin`
    decorator *not* already tested by higher-level unit tests defined elsewhere.

    See Also
    ----------
    ``test_decor_wrappee_type_decorator_builtin()``
        Higher-level unit test already exercising *most* of the functionality of
        this decorator, which this test (sensibly) avoids repeating.
    '''

    # Defer test-specific imports.
    from beartype import BeartypeConf
    from beartype.roar import BeartypeDecorWrappeeException
    from beartype._decor._decormore import beartype_descriptor_decorator_builtin
    from pytest import raises

    # Assert this decorator raises the expected exception when passed an object
    # that is neither a class, property, *NOR* static method descriptor.
    with raises(BeartypeDecorWrappeeException):
        beartype_descriptor_decorator_builtin(
            descriptor='Music, when soft voices die,',
            conf=BeartypeConf(),
        )
