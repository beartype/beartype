#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Test-specific **Python module detection** utilities.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype._util.cache.utilcachecall import callable_cached

# ....................{ TESTERS ~ numpy                   }....................
@callable_cached
def is_package_numpy() -> bool:
    '''
    ``True`` only if a reasonably recent version of NumPy is importable under
    the active Python interpreter.
    '''

    # Defer heavyweight imports.
    from beartype.meta import _LIB_RUNTIME_OPTIONAL_VERSION_MINIMUM_NUMPY
    from beartype._util.mod.utilmodtest import is_module_version_at_least

    # Return true only if this version of this package is importable.
    return is_module_version_at_least(
        'numpy', _LIB_RUNTIME_OPTIONAL_VERSION_MINIMUM_NUMPY)


@callable_cached
def is_package_numpy_typing_ndarray_supported() -> bool:
    '''
    ``True`` only if the :attr:`numpy.typing.NDArray` type hint is supported by
    the :func:`beartype.beartype` decorator under the active Python
    interpreter.

    Specifically, this tester returns true only if:

    * A reasonably recent version of NumPy is importable under the active
      Python interpreter.
    * Either:

      * This interpreter targets Python >= 3.9 and thus provides the
        :attr:`typing.Annotated` type hint internally required by
        :func:`beartype.beartype` to support this hint.
        * A reasonably recent version of the third-party
          :mod:`typing_extensions` package is importable under this interpreter
          and thus provides the alternative :attr:`typing_extensions.Annotated`
          type hint internally required by :func:`beartype.beartype` to support
          this hint.
    '''

    # Defer heavyweight imports.
    from beartype._util.mod.utilmodtest import is_module_typing_any_attr

    # Return true only if the "numpy.typing.NDArray" is supported.
    return is_package_numpy() and is_module_typing_any_attr('Annotated')

# ....................{ TESTERS ~ typing                  }....................
@callable_cached
def is_package_typing_extensions() -> bool:
    '''
    ``True`` only if a reasonably recent version of the third-party
    :mod:`typing_extensions` package is importable under the active Python
    interpreter.
    '''

    # Defer heavyweight imports.
    from beartype.meta import (
        _LIB_RUNTIME_OPTIONAL_VERSION_MINIMUM_TYPING_EXTENSIONS)
    from beartype._util.mod.utilmodtest import is_module_version_at_least

    # Return true only if this version of this package is importable.
    return is_module_version_at_least(
        'typing_extensions',
        _LIB_RUNTIME_OPTIONAL_VERSION_MINIMUM_TYPING_EXTENSIONS,
    )
