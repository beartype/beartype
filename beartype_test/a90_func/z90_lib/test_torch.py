#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
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
from beartype_test._util.mark.pytskip import (
    skip,
    skip_unless_package,
)

# ....................{ TESTS                              }....................
#FIXME: Remove this unconditional skip *AFTER* we resolve outstanding issues
#surrounding PyTorch installation on various platforms, including:
#* Gentoo Linux, where @leycec currently receives this well-known exception on
#  attempting to import PyTorch:
#      NameError: name '_C' is not defined
#  Note that this *ONLY* occurs under "pytest". PyTorch remains importable
#  outside of "pytest", which is all manner of bizarre. *shrug*
#* GitHub Actions-based continuous integration (CI), where similar issues are
#  likely to arise under macOS and/or Windows.
@skip('Currently ignored, due to the non-triviality of installing PyTorch.')
# @skip_unless_package('torch')
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

    # ....................{ LOCAL                          }....................
    # Tuple of all arguments to be passed to the active Python interpreter rerun
    # as an external command.
    _PYTHON_ARGS = get_interpreter_command_words() + ('-c', 'import torch',)

    # ....................{ PASS                           }....................
    # Run this command, raising an exception on subprocess failure while
    # forwarding all standard output and error output by this subprocess to the
    # standard output and error file handles of the active Python process.
    run_command_forward_output(command_words=_PYTHON_ARGS)
