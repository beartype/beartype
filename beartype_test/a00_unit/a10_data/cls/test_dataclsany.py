#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **any analog class hierarchy** unit tests.

This submodule unit tests the public API of the public
:mod:`beartype._data.cls.dataclsany` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_beartype_any() -> None:
    '''
    Test the :obj:`beartype._data.cls.dataclsany.BeartypeAny` type.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._data.cls.dataclsany import BeartypeAny
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert that *ANY* arbitrary object is an instance of this type.
    assert isinstance(object(), BeartypeAny) is True

    # Assert that *ANY* arbitrary type is a subclass of this type.
    assert issubclass(object, BeartypeAny) is True

    # ....................{ FAIL                           }....................
    # Assert that *ANY* arbitrary non-type is *NOT* a subclass of this type but
    # instead raises the standard "TypeError" exception expected to be raised by
    # the issubclass() builtin in this common edge case.
    with raises(TypeError):
        issubclass(object(), BeartypeAny)
