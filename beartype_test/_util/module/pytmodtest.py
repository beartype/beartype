#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Test-specific **Python module detection** utilities.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype._util.cache.utilcachecall import callable_cached

# ....................{ TESTERS ~ lib                      }....................
@callable_cached
def is_package_sphinx() -> bool:
    '''
    :data:`True` only if a reasonably recent version of Sphinx is importable
    under the active Python interpreter.
    '''

    # Defer test-specific imports.
    from beartype.meta import _LIB_DOCTIME_MANDATORY_VERSION_MINIMUM_SPHINX
    from beartype._util.module.utilmodtest import is_module_version_at_least

    # Return true only if this version of this package is importable.
    return is_module_version_at_least(
        'sphinx', _LIB_DOCTIME_MANDATORY_VERSION_MINIMUM_SPHINX)


@callable_cached
def is_package_typing_extensions() -> bool:
    '''
    :data:`True` only if a reasonably recent version of the third-party
    :mod:`typing_extensions` package is importable under the active Python
    interpreter.
    '''

    # Defer test-specific imports.
    from beartype.meta import (
        _LIB_RUNTIME_OPTIONAL_VERSION_MINIMUM_TYPING_EXTENSIONS)
    from beartype._util.module.utilmodtest import is_module_version_at_least

    # Return true only if this version of this package is importable.
    return is_module_version_at_least(
        'typing_extensions',
        _LIB_RUNTIME_OPTIONAL_VERSION_MINIMUM_TYPING_EXTENSIONS,
    )

# ....................{ TESTERS ~ lib : numpy              }....................
@callable_cached
def is_package_numpy() -> bool:
    '''
    :data:`True` only if a reasonably recent version of NumPy is importable
    under the active Python interpreter.
    '''

    # Defer test-specific imports.
    from beartype.meta import _LIB_RUNTIME_OPTIONAL_VERSION_MINIMUM_NUMPY
    from beartype._util.module.utilmodtest import is_module_version_at_least

    # Return true only if this version of this package is importable.
    return is_module_version_at_least(
        'numpy', _LIB_RUNTIME_OPTIONAL_VERSION_MINIMUM_NUMPY)
