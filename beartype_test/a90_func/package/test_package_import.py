#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Project-wide functional importation tests.**

This submodule functionally tests the this project's behaviour with respect to
imports of both internal subpackages and submodules (unique to this project)
*and* external third-party packages and modules.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_package_import_isolation() -> None:
    '''
    Test that importing the top-level lightweight :mod:`beartype` package does
    *not* accidentally import from one or more heavyweight (sub)packages.

    This test ensures that the fix cost of the first importation of the
    :mod:`beartype` package itself remains low -- if not ideally negligible.
    '''

    # Defer test-specific imports.
    from beartype._util.py.utilpyinterpreter import (
        get_interpreter_command_words)
    from beartype_test._util.command.pytcmdrun import (
        run_command_forward_stderr_return_stdout)
    from re import (
        compile as re_compile,
        search as re_search,
    )

    #FIXME: *FRAGILE.* Manually hardcoding module names here invites
    #desynchronization, particularly with optional third-party dependencies.
    #Instead, the names of optional third-party packages should be dynamically
    #constructed from the contents of the "beartype.meta" submodule.

    # Tuple of uncompiled regular expressions, each matching the
    # fully-qualified name of *ANY* heavyweight (sub)module or package whose
    # importation violates our self-imposed constraint of fast importation of
    # our core @beartype.beartype decorator.
    #
    # Note that:
    # * The third-party "typing_extensions" module has been profiled across
    #   all supported CPython versions to import either faster or only slightly
    #   slower than the standard "typing" module. In either case, both modules
    #   implement sufficiently rapidly as to be ignorable with respect to
    #   importation costs here. See also @posita's stunning profiling work at:
    #       https://github.com/beartype/beartype/pull/103#discussion_r815027198
    _HEAVY_MODULE_NAME_RAW_REGEXES = (
        r'beartype\.abby',
        r'beartype\.cave',
        r'beartype\.vale',
        r'numpy',
    )

    # Uncompiled regular expressions synthesized from this tuple.
    _HEAVY_MODULE_NAME_RAW_REGEX = '|'.join(_HEAVY_MODULE_NAME_RAW_REGEXES)

    # Compiled regular expression synthesized from this tuple.
    _HEAVY_MODULE_NAME_REGEX = re_compile(
        fr'^({_HEAVY_MODULE_NAME_RAW_REGEX})\b')
    # print(f'_HEAVY_MODULE_NAME_REGEX: {_HEAVY_MODULE_NAME_REGEX}')

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

    # Tuple of all arguments to be passed to the active Python interpreter rerun
    # as an external command.
    _PYTHON_ARGS = get_interpreter_command_words() + (
        '-c',
        _CODE_PRINT_IMPORTS_AFTER_IMPORTING_BEARTYPE,
    )

    # Run this code isolated to a Python subprocess, raising an exception on
    # subprocess failure while both forwarding all standard error output by this
    # subprocess to the standard error file handle of the active Python process
    # *AND* capturing and returning all subprocess stdout.
    module_names_str = run_command_forward_stderr_return_stdout(
        command_words=_PYTHON_ARGS)

    #FIXME: Actually parse "module_names" for bad entries here, please.
    # print(module_names)

    # List of the fully-qualified names of all modules transitively imported by
    # importing the @beartype decorator in an isolated Python interpreter.
    module_names = module_names_str.splitlines()

    # For each such name, assert this name is *NOT* that of a heavyweight
    # (sub)module or package enumerated above.
    #
    # Note that this iteration could, of course, also be more efficiently
    # implementable as a single composite regex match on the newline-delimited
    # "module_names_str" string. However, doing so would entirely defeat the
    # purpose of this iteration: to offer unambiguous and human-readable error
    # messages in the common event of an importation violation.
    for module_name in module_names:
        assert re_search(_HEAVY_MODULE_NAME_REGEX, module_name) is None, (
            f'@beartype.beartype improperly imports heavyweight module '
            f'"{module_name}" from global scope.'
        )
