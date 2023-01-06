#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **platform tester** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.os.utilostest` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_is_os_macos() -> None:
    '''
    Test the :func:`beartype._util.os.utilostest.is_os_macos` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.os.utilostest import is_os_macos

    # Assert this tester returns a boolean.
    IS_OS_MACOS = is_os_macos()
    assert isinstance(IS_OS_MACOS, bool)


def test_is_os_windows_vanilla() -> None:
    '''
    Test the :func:`beartype._util.os.utilostest.is_os_windows_vanilla` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.os.utilostest import is_os_windows_vanilla

    # Assert this tester returns a boolean.
    IS_OS_WINDOWS_VANILLA = is_os_windows_vanilla()
    assert isinstance(IS_OS_WINDOWS_VANILLA, bool)
