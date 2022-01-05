#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python interpreter** utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar._roarexc import (
    _BeartypeUtilPathException,
    _BeartypeUtilPythonException,
)
from beartype._util.cache.utilcachecall import callable_cached
from platform import python_implementation
from sys import executable as sys_executable

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ TESTERS                           }....................
@callable_cached
def is_py_pypy() -> bool:
    '''
    ``True`` only if the active Python interpreter is **PyPy**.

    This tester is memoized for efficiency.
    '''

    return python_implementation() == 'PyPy'

# ....................{ GETTERS                           }....................
def get_interpreter_filename() -> str:
    '''
    Absolute filename of the executable binary underlying the active Python
    interpreter if Python successfully queried this filename *or* raise an
    exception otherwise.

    Raises
    ----------
    _BeartypeUtilPathException
        If Python successfully queried this filename but no such file exists.
    _BeartypeUtilPythonException
        If Python failed to query this filename.
    '''

    # Avoid circular import dependencies.
    # from beartype._util.path.utilfile import 

    # If Python failed to query this filename, raise an exception.
    #
    # Note that this test intentionally matches both the empty string and
    # "None", as the official documentation for "sys.executable" states:
    #     If Python is unable to retrieve the real path to its executable,
    #     sys.executable will be an empty string or None.
    if not sys_executable:
        raise _BeartypeUtilPythonException(
            'Absolute filename of Python interpreter unknown.')
    # Else, Python successfully queried this filename.

    #FIXME: Actually implement this up. Doing so will require declaring a
    #new beartype._util.path.utilfile.die_unless_file_executable() tester. For
    #simplicity, we currently assume Python knows what it's talking about here.
    # # If no such file exists, raise an exception.
    # die_unless_file_executable(sys_executable)
    # # Else, this file exists, raise an exception.

    # Return this filename as is.
    return sys_executable
