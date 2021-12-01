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
def test_package_import_isolation() -> None:
    '''
    Test that importing the top-level lightweight :mod:`beartype` package does
    *not* accidentally import from one or more heavyweight (sub)packages.

    This test ensures that the fix cost of the first importation of the
    :mod:`beartype` package itself remains low -- if not ideally negligible.
    '''

    # Defer heavyweight imports.
    from beartype_test.util.cmd.pytcmdrun import (
        run_python_forward_stderr_return_stdout)

    # Python code printing all imports (i.e., the contents of the standard
    # "sys.modules" list) *AFTER* importing the @beartype decorator.
    _CODE_PRINT_IMPORTS_AFTER_IMPORTING_BEARTYPE = '''
# Import the core @beartype decorator and requisite "sys" machinery.
from beartype import beartype
from sys import modules

# Print a newline-delimited list of the fully-qualified names of all modules
# transitively imported by the prior "import" statements.
print('\\n'.join(module_name for module_name in modules.keys()))
'''

    # Tuple of all arguments to be passed to an external Python command,
    # running this code isolated to a Python subprocess.
    _PYTHON_ARGS = ('-c', _CODE_PRINT_IMPORTS_AFTER_IMPORTING_BEARTYPE,)

    # Run this code isolated to a Python subprocess, raising an exception on
    # subprocess failure while both forwarding all standard error output by
    # this subprocess to the standard error file handle of the active Python
    # process *AND* capturing and returning all subprocess stdout.
    module_names = run_python_forward_stderr_return_stdout(
        python_args=_PYTHON_ARGS)

    #FIXME: Actually parse "module_names" for bad entries here, please.
    # print(module_names)
