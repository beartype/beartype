#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **terminal tester** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.os.utilostty` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_is_stdout_terminal() -> None:
    '''
    Test the :func:`beartype._util.os.utilostty.is_stdout_terminal` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.os.utilostty import is_stdout_terminal

    # Assert this tester returns a boolean.
    IS_STDOUT_TERMINAL = is_stdout_terminal()
    assert isinstance(IS_STDOUT_TERMINAL, bool)
