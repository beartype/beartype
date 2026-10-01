#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **import path hook utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.importlib.utilimppathhook` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_get_standard_file_finder_path_hook_basename_scoped() -> None:
    '''
    Test the
    :func:`beartype._util.importlib.utilimppathhook._get_standard_file_finder_path_hook_basename_scoped`
    getter.
    '''

    # Defer test-specific imports.
    from beartype._util.importlib.utilimppathhook import (
        _get_standard_file_finder_path_hook_basename_scoped)

    # Lexically scoped basename of the standard file finder path hook.
    path_hook_basename = _get_standard_file_finder_path_hook_basename_scoped()

    # Assert that this basename is a non-empty string. That's it! We done, yo.
    assert isinstance(path_hook_basename, str)
    assert path_hook_basename
