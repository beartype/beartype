#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
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

# ....................{ TESTERS ~ beartype                 }....................
@callable_cached
def is_package_beartype_vale_usable() -> bool:
    '''
    :data:`True` only if **beartype validators** (i.e., subscriptions of public
    classes declared by the :class:`beartype.vale` subpackage) are creatable
    under the active Python interpreter.

    Specifically, this tester returns true only if either:

    * This interpreter targets Python >= 3.9 and thus provides the
      :attr:`typing.Annotated` type hint required by beartype validators.
    * This interpreter targets Python >= 3.8 *and* a reasonably recent version
      of the third-party :mod:`typing_extensions` package is importable under
      this interpreter and thus provides the alternative
      :attr:`typing_extensions.Annotated` type hint required by beartype
      validators.
    '''

    # Defer test-specific imports.
    from beartype._util.module.lib.utiltyping import is_typing_attr

    # Return true only if the "Annotated" type hint is importable from either
    # the official "typing" or third-party "typing_extensions" modules.
    return is_typing_attr('Annotated')

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


@callable_cached
def is_package_numpy_typing_ndarray_deep() -> bool:
    '''
    :data:`True` only if :attr:`numpy.typing.NDArray` type hints are deeply
    supported by the :func:`beartype.beartype` decorator under the active
    Python interpreter.

    Specifically, this tester returns true only if:

    * A reasonably recent version of NumPy is importable under the active
      Python interpreter.
    * Beartype validators are usable under the active Python interpreter, as
      :func:`beartype.beartype` internally reduces these hints to equivalent
      beartype validators. See :func:`.is_package_beartype_vale_usable`.
    '''

    # Return true only if...
    return (
        # A recent version of NumPy is importable *AND*...
        is_package_numpy() and
        # Beartype validators are usable under the active Python interpreter.
        is_package_beartype_vale_usable()
    )
