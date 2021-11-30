#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Project-wide functional importation tests.**

This submodule functionally tests the this project's behaviour with respect to
imports of both internal subpackages and submodules (unique to this project)
*and* external third-party packages and modules.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
#FIXME: Non-trivial to implement. For import isolation, we'll need to:
#* First fork a CLI command resembling:
#    run_python_forward_output(python_args=(
#       '-c', '''
#    from beartype import beartype
#    from sys import modules
#    print(modules)
#    '''))
#* Then parse that output for harmful modules.
def test_import_isolation() -> None:
    '''
    Test that importing the top-level lightweight :mod:`beartype` package does
    *not* accidentally import from one or more heavyweight (sub)packages.

    This test ensures that the fix cost of the first importation of the
    :mod:`beartype` package itself remains low -- if not ideally negligible.
    '''

    pass
