#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PyTorch** integration tests.

This submodule functionally tests the :mod:`beartype` package against the
third-party PyTorch package.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
@skip_unless_package('torch')
def test_torch() -> None:
    '''
    Functional test validating that the :mod:`beartype` package raises *no*
    unexpected exceptions when imported by the third-party PyTorch package.

    To do so, this test externally imports the :mod:`torch` package against a
    minimal-length Python snippet exercising all known edge cases.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.py.utilpyinterpreter import (
        get_interpreter_command_words)
    from beartype_test._util.command.pytcmdrun import run_command_forward_output

    # ....................{ LOCALS                         }....................
    # Tuple of all arguments to be passed to the active Python interpreter rerun
    # as an external command.
    _PYTHON_ARGS = get_interpreter_command_words() + ('-c', 'import torch',)

    # ....................{ PASS                           }....................
    # Run this command, raising an exception on subprocess failure while
    # forwarding all standard output and error output by this subprocess to the
    # standard output and error file handles of the active Python process.
    run_command_forward_output(command_words=_PYTHON_ARGS)
