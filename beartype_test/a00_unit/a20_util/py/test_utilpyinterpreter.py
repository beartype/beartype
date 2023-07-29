#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python interpreter** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.py.utilpyinterpreter` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ testers                    }....................
def test_is_py_pypy() -> None:
    '''
    Test the :func:`beartype._util.py.utilpyinterpreter.is_py_pypy` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.py.utilpyinterpreter import is_py_pypy

    # Assert this tester returns a boolean.
    IS_PY_PYPY = is_py_pypy()
    assert isinstance(IS_PY_PYPY, bool)

# ....................{ TESTS ~ getters                    }....................
def test_get_interpreter_command() -> None:
    '''
    Test the
    :func:`beartype._util.py.utilpyinterpreter.get_interpreter_command_words` getter.
    '''

    # Defer test-specific imports.
    from beartype._util.py.utilpyinterpreter import get_interpreter_command_words
    from collections.abc import Iterable

    # Iterable of all interpreter shell words.
    interpreter_command = get_interpreter_command_words()

    # Assert that this iterable is non-empty.
    assert isinstance(interpreter_command, Iterable)
    assert bool(interpreter_command)

    #FIXME: Additionally assert that this command is successfully runnable.


def test_get_interpreter_filename() -> None:
    '''
    Test the
    :func:`beartype._util.py.utilpyinterpreter.get_interpreter_filename` getter.
    '''

    # Defer test-specific imports.
    from beartype._util.py.utilpyinterpreter import get_interpreter_filename

    # Absolute filename of the executable binary underlying this interpreter.
    interpreter_filename = get_interpreter_filename()

    # Assert that this filename is a non-empty string.
    assert isinstance(interpreter_filename, str)
    assert bool(str)
