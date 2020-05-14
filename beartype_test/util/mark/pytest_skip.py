#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**:mod:`pytest` test-skipping decorators.**

This submodule provides decorators conditionally marking their decorated tests
as skipped depending on whether the conditions signified by the passed
parameters are satisfied (e.g., the importability of the passed module name).
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import platform, pytest, sys
from beartype_test.util.mark import pytest_mark
from collections.abc import (
    Mapping as Mapping,
    Sequence as Sequence,
)
from types import FunctionType

# Sadly, the following imports require private modules and packages.
from _pytest.runner import Skipped

# ....................{ GLOBALS                           }....................
_NoneType = type(None)
'''
Type of the ``None`` singleton, duplicated from the possibly unsafe
:mod:`beartype.cave` submodule to avoid raising exceptions from the early
testing-time decorators defined by this utility submodule.
'''

# ....................{ GLOBALS ~ constants               }....................
_PYTHON_VERSION_TUPLE = sys.version_info[:3]
'''
Machine-readable version of the active Python interpreter as a tuple of
integers.

See Also
----------
:mod:`beartype.meta`
    Similar logic performed at :mod:`beartype` importation time.
'''


_PYTHON_VERSION_STR = '.'.join(
    str(version_part) for version_part in sys.version_info[:3])
'''
Human-readable version of the active Python interpreter as a dot-delimited
string.

See Also
----------
:mod:`beartype.meta`
    Similar logic performed at :mod:`beartype` importation time.
'''

# ....................{ SKIP                              }....................
skip_if = pytest.mark.skipif
'''
Conditionally skip the decorated test or fixture with the passed human-readable
justification if the passed boolean is ``False``.

Parameters
----------
boolean : bool
    Boolean to be tested.
reason : str
    Human-readable message justifying the skipping of this test or fixture.
'''


def skip(reason: str):
    '''
    Unconditionally skip the decorated test with the passed human-readable
    justification.

    This decorator is intended to be called both directly as a function *and*
    indirectly as a decorator, which differs from both:

    * :func:`pytest.skip`, intended to be called only directly as a function.
      Attempting to call that function indirectly as a decorator produces
      extraneous ignorable messages on standard output resembling
      ``"SKIP [1] beartype_test/unit/test_import.py:66: could not import
      'xdist'"``, for unknown (and probably uninteresting) reasons.
    * :func:`pytest.mark.skip`, intended to be called only indirectly as a
      decorator. Attempting to call that decorator directly as a function
      reduces to a noop, for unknown (and probably uninteresting) reasons.

    Parameters
    ----------
    reason : str
        Human-readable message justifying the skipping of this test.

    Returns
    ----------
    pytest.skipif
        Decorator skipping the decorated test with this justification.
    '''
    assert isinstance(reason, str), '"{!r}" not a string.'.format(reason)

    return skip_if(True, reason=reason)

# ....................{ SKIP ~ py                         }....................
def skip_if_pypy():
    '''
    Skip the decorated test or fixture if the active Python interpreter is the
    PyPy, a third-party implementation emphasizing Just In Time (JIT) bytecode
    optimization.

    Returns
    ----------
    pytest.skipif
        Decorator skipping this text or fixture if this interpreter is PyPy
        *or* the identity decorator reducing to a noop otherwise.
    '''

    # Skip this test if the active Python interpreter is PyPy.
    return skip_if(
        platform.python_implementation() == 'PyPy', reason='PyPy.')


def skip_if_python_version_less_than(minimum_version: str):
    '''
    Skip the decorated test or fixture if the version of the active Python
    interpreter is strictly less than the passed minimum version.

    Parameters
    ----------
    minimum_version : str
        Minimum version of the Python interpreter required by this test or
        fixture as a dot-delimited string (e.g., ``3.5.0``)

    Returns
    ----------
    pytest.skipif
        Decorator describing these requirements if unmet *or* the identity
        decorator reducing to a noop otherwise.

    See Also
    ----------
    :mod:`beartype.meta`
        Similar logic performed at :mod:`beartype` importation time.
    '''
    assert isinstance(minimum_version, str), (
        '"{!r}" not a string.'.format(minimum_version))

    # Defer heavyweight imports.
    from beartype.meta import _convert_version_str_to_tuple

    # Machine-readable minimum version of Python as a tuple of integers.
    minimum_version_tuple = _convert_version_str_to_tuple(minimum_version)

    # Skip this test if the current Python version is less than this minimum.
    return skip_if(
        _PYTHON_VERSION_TUPLE < minimum_version_tuple,
        reason='Python {} < {}.'.format(minimum_version, _PYTHON_VERSION_STR))

# ....................{ SKIP ~ py : module                }....................
def skip_unless_module(module_name: str, minimum_version: str = None):
    '''
    Skip the decorated test or fixture if the module with the passed name is
    unimportable *or* importable but of a version less than the passed minimum
    version if non-``None``.

    Parameters
    ----------
    module_name : str
        Fully-qualified name of the module to be tested for.
    minimum_version : Optional[str]
        Optional minimum version of this module as a dot-delimited string
        (e.g., ``0.4.0``) to be tested for if any *or* ``None`` otherwise, in
        which case any version is acceptable. Defaults to ``None``.

    Returns
    ----------
    pytest.skipif
        Decorator describing these requirements if unmet *or* the identity
        decorator reducing to a noop otherwise.
    '''
    assert isinstance(module_name, str), (
        '"{!r}" not a string.'.format(module_name))
    assert isinstance(minimum_version, (str, _NoneType)), (
        '"{!r}" not a string.'.format(minimum_version))

    return _skip_if_callable_raises_exception(
        exception_type=Skipped,
        func=pytest.importorskip,
        args=(module_name, minimum_version),
    )

# ....................{ SKIP ~ private                    }....................
def _skip_if_callable_raises_exception(
    # Mandatory parameters.
    exception_type: type,
    func: FunctionType,

    # Optional parameters.
    args: (Sequence, _NoneType) = None,
    kwargs: (Mapping, _NoneType) = None,
):
    '''
    Skip the decorated test or fixture if calling the passed callable with the
    passed positional and keyword arguments raises an exception of the passed
    type.

    Specifically, if calling this callable raises:

    * The passed type of exception, this test is marked as skipped.
    * Any other type of exception, this test is marked as a failure.
    * No exception, this test continues as expected.

    Parameters
    ----------
    exception_type : type
        Type of exception expected to be raised by this callable.
    func : FunctionType
        Callable to be called.
    args : (Sequence, _NoneType)
        Sequence of all positional arguments to unconditionally pass to the
        passed callable if any *or* ``None`` otherwise. Defaults to ``None``.
    kwargs : (Mapping, _NoneType)
        Mapping of all keyword arguments to unconditionally pass to the passed
        callable if any *or* ``None`` otherwise. Defaults to ``None``.

    Returns
    ----------
    pytest.skipif
        Decorator skipping this test if this callable raises this exception
        *or* the identity decorator reducing to a noop otherwise.
    '''

    # Default all unpassed arguments to sane values.
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}
    assert isinstance(exception_type, type), (
        '"{!r}" not a type.'.format(exception_type))
    assert isinstance(func, FunctionType), (
        '"{!r}" not a function.'.format(func))
    assert isinstance(args, Sequence), '"{!r}" not a sequence.'.format(args)
    assert isinstance(kwargs, Mapping), '"{!r}" not a mapping.'.format(kwargs)

    # Attempt to call this callable with these arguments.
    try:
        func(*args, **kwargs)
    # If this callable raises an expected exception, skip this test.
    except exception_type as exception:
        return skip(str(exception))
    # Else if this callable raises an unexpected exception, fail this test by
    # permitting this exception to unwind the current call stack.

    # Else, this callable raised no exception. Silently reduce to a noop.
    return pytest_mark.noop
