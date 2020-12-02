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
from beartype_test.util.mark import pytmark
from collections.abc import Mapping, Sequence
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
    assert isinstance(reason, str), '"{!r}" not string.'.format(reason)

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
        f'{repr(minimum_version)} not string.')

    # Defer heavyweight imports.
    from beartype.meta import _convert_version_str_to_tuple

    # Machine-readable minimum version of Python as a tuple of integers.
    minimum_version_tuple = _convert_version_str_to_tuple(minimum_version)

    # Skip this test if the current Python version is less than this minimum.
    return skip_if(
        _PYTHON_VERSION_TUPLE < minimum_version_tuple,
        reason=f'Python {_PYTHON_VERSION_STR} < {minimum_version}.')

# ....................{ SKIP ~ py : module                }....................
def skip_unless_package(
    package_name: str, minimum_version: 'Optional[str]' = None):
    '''
    Skip the decorated test or fixture if the package with the passed name is
    **unsatisfied** (i.e., either dynamically unimportable *or* importable but
    of a version less than the passed minimum version if non-``None``).

    Parameters
    ----------
    package_name : str
        Fully-qualified name of the package to be skipped.
    minimum_version : Optional[str]
        Optional minimum version of this package as a dot-delimited string
        (e.g., ``0.4.0``) to be tested for if any *or* ``None`` otherwise, in
        which case any version is acceptable. Defaults to ``None``.

    Returns
    ----------
    pytest.skipif
        Decorator describing these requirements if unmet *or* the identity
        decorator reducing to a noop otherwise.
    '''
    assert isinstance(package_name, str), (
        f'{repr(package_name)} not string.')

    # Skip the decorated test or fixture unless the requisite dunder submodule
    # declared by this package satisfies these requirements.
    return skip_unless_module(
        module_name=f'{package_name}.__init__',
        minimum_version=minimum_version,
    )


def skip_unless_module(
    module_name: str, minimum_version: 'Optional[str]' = None):
    '''
    Skip the decorated test or fixture if the module with the passed name is
    **unsatisfied** (i.e., either dynamically unimportable *or* importable but
    of a version less than the passed minimum version if non-``None``).

    Caveats
    ----------
    **This decorator should never be passed the fully-qualified name of a
    package.** Consider calling the :func:`skip_unless_package` decorator
    instead to skip unsatisfied packages. Calling this decorator with package
    names guarantees those packages to be skipped, as packages are *not*
    directly importable as modules.

    Parameters
    ----------
    module_name : str
        Fully-qualified name of the module to be skipped.
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
        f'{repr(module_name)} not string.')
    assert isinstance(minimum_version, (str, _NoneType)), (
        f'{repr(minimum_version)} neither string nor "None".')

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
    args: 'Optional[Sequence]' = None,
    kwargs: 'Optional[Mapping]' = None,
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
    args : Optional[Sequence]
        Sequence of all positional arguments to unconditionally pass to the
        passed callable if any *or* ``None`` otherwise. Defaults to ``None``.
    kwargs : Optional[Mapping]
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

    # Validate *AFTER* defaulting these arguments.
    assert isinstance(exception_type, type), (
        f'{repr((exception_type))} not type.')
    assert callable(func), '{repr()} uncallable.'
    assert isinstance(args, Sequence), '{repr(args)} not sequence.'
    assert isinstance(kwargs, Mapping), '{repr(kwargs)} not mapping.'

    # Attempt to call this callable with these arguments.
    try:
        func(*args, **kwargs)
    # If this callable raises an expected exception, skip this test.
    except exception_type as exception:
        return skip(str(exception))
    # Else if this callable raises an unexpected exception, fail this test by
    # permitting this exception to unwind the current call stack.

    # Else, this callable raised no exception. Silently reduce to a noop.
    return pytmark.noop
