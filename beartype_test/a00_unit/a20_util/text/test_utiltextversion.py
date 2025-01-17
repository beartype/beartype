#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **version string utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.text.utiltextversion` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_convert_str_version_to_tuple() -> None:
    '''
    Test the
    :func:`beartype._util.text.utiltextversion.convert_str_version_to_tuple`
    exception-raiser.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilTextVersionException
    from beartype._util.text.utiltextversion import convert_str_version_to_tuple
    from pytest import raises

    # ....................{ PASS ~ undelimited             }....................
    # Assert that this converter converts a valid version string containing *NO*
    # "." delimiter comprising zero to the expected tuple.
    assert convert_str_version_to_tuple('0') == (0,)

    # Assert that this converter converts a valid version string containing *NO*
    # "." delimiter comprising a single positive integer to the expected tuple.
    assert convert_str_version_to_tuple('26') == (26,)

    # Assert that this converter converts a valid version string containing *NO*
    # "." delimiter comprising a single positive integer suffixed by a non-empty
    # substring that is *NOT* a non-negative integer to the expected tuple.
    assert convert_str_version_to_tuple('26rc1') == (26,)

    # ....................{ PASS ~ delimited               }....................
    # Assert that this converter converts a valid version string comprising one
    # or more "."-delimited non-negative integers to the expected tuple.
    assert convert_str_version_to_tuple('0.26.05') == (0, 26, 5,)

    # Assert that this converter converts a valid version string comprising one
    # or more "."-delimited non-negative integers suffixed by a non-empty
    # substring that is *NOT* a non-negative integer to the expected tuple.
    assert convert_str_version_to_tuple('0.26.05rc1') == (0, 26, 5,)

    # ....................{ FAIL                           }....................
    # Assert that this converter raises the expected exception when passed an
    # invalid version string containing *NO* "." delimiter comprising a single
    # non-empty substring that is *NOT* a non-negative integer.
    with raises(_BeartypeUtilTextVersionException):
        convert_str_version_to_tuple('rc1')

    # Assert that this converter raises the expected exception when passed an
    # invalid version string containing *NO* "." delimiter comprising a single
    # negative integer.
    with raises(_BeartypeUtilTextVersionException):
        convert_str_version_to_tuple('-15')

    # Assert that this converter raises the expected exception when passed an
    # invalid version string comprising (in order):
    # 1. One or more "."-delimited non-negative integers followed by...
    # 2. A "."-delimited negative integer.
    with raises(_BeartypeUtilTextVersionException):
        convert_str_version_to_tuple('0.-15')

    # Assert that this converter raises the expected exception when passed an
    # invalid version string comprising (in order):
    # 1. One or more "."-delimited non-negative integers followed by...
    # 2. A "."-delimited substring that is *NOT* a non-negative integer followed
    #    by...
    # 3. One or more "."-delimited non-negative integers.
    with raises(_BeartypeUtilTextVersionException):
        convert_str_version_to_tuple('0.15rc1.2')
