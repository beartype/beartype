#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
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
def test_is_python_pypy() -> None:
    '''
    Test the :func:`beartype._util.py.utilpyinterpreter.is_python_pypy` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.py.utilpyinterpreter import is_python_pypy

    # Assert this tester returns a boolean.
    IS_PY_PYPY = is_python_pypy()
    assert isinstance(IS_PY_PYPY, bool)


def test_is_python_optimized(monkeypatch: 'pytest.MonkeyPatch') -> None:
    '''
    Test the :func:`beartype._util.py.utilpyinterpreter.is_python_optimized`
    tester.

    Parameters
    ----------
    monkeypatch : MonkeyPatch
        :mod:`pytest` fixture allowing various state associated with the active
        Python process to be temporarily changed for the duration of this test.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.py.utilpyinterpreter import is_python_optimized

    # ....................{ ASSERT                         }....................
    # Assert that the active Python interpreter is currently unoptimized. In
    # theory, tests should *ALWAYS* be run unoptimized. Why? Because
    # optimization destructively elides away (i.e., silently reduces to noops)
    # all "assert" statements, obstructing testing.
    assert is_python_optimized() is False

    # Temporarily zero the ${PYTHONOPTIMIZE} environment variable.
    monkeypatch.setenv('PYTHONOPTIMIZE', '0')

    # Assert that the active Python interpreter remains unoptimized.
    assert is_python_optimized() is False

    # Temporarily set this variable to an arbitrary positive integer.
    monkeypatch.setenv('PYTHONOPTIMIZE', '1')

    # Assert that the active Python interpreter is now kinda "optimized."
    assert is_python_optimized() is True

    # Temporarily set this variable to an arbitrary string that *CANNOT* be
    # coerced into an integer.
    monkeypatch.setenv('PYTHONOPTIMIZE', (
        'Bright in the lustre of their own fond joy.'))

    # Assert that the active Python interpreter is yet again unoptimized.
    assert is_python_optimized() is False

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
