#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
High-level **beartype integration tests.**

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
def test_beartype_import_isolation() -> None:
    '''
    Integration test ensuring that importing the top-level lightweight
    :mod:`beartype` package does *not* accidentally import from one or more
    heavyweight (sub)packages or third-party packages.

    This integration test assists the :mod:`beartype` package minimize the fixed
    cost of its first importation by downstream consumers.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.py.utilpyinterpreter import (
        get_interpreter_command_words)
    from beartype_test._util.command.pytcmdrun import (
        run_command_forward_stderr_return_stdout)
    from re import (
        compile as re_compile,
        search as re_search,
    )

    # ....................{ LOCALS                         }....................
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
    HEAVY_MODULE_NAME_RAW_REGEXES = (
        r'beartype\.bite',
        r'beartype\.cave',
        r'beartype\.claw',
        r'beartype\.door',
        r'beartype\.peps',
        r'beartype\.vale',
        r'numpy',
    )

    # Uncompiled regular expressions synthesized from this tuple.
    HEAVY_MODULE_NAME_RAW_REGEX = '|'.join(HEAVY_MODULE_NAME_RAW_REGEXES)

    # Compiled regular expression synthesized from this tuple.
    HEAVY_MODULE_NAME_REGEX = re_compile(
        fr'^({HEAVY_MODULE_NAME_RAW_REGEX})\b')
    # print(f'_HEAVY_MODULE_NAME_REGEX: {_HEAVY_MODULE_NAME_REGEX}')

    # Python code snippet printing all imports (i.e., the contents of the
    # standard "sys.modules" list) *AFTER* importing the @beartype decorator.
    CODE_IMPORT_BEARTYPE_AND_PRINT_IMPORTED_MODULES = '''
# Import the core @beartype decorator and requisite "sys" machinery.
from beartype import beartype
from sys import modules

# Print a newline-delimited list of the fully-qualified names of all modules
# transitively imported by the prior "import" statements.
print('\\n'.join(module_name for module_name in modules.keys()))
'''

    # Tuple of all arguments to be passed to the active Python interpreter rerun
    # as an external command.
    PYTHON_ARGS = get_interpreter_command_words() + (
        '-c', CODE_IMPORT_BEARTYPE_AND_PRINT_IMPORTED_MODULES)

    # ....................{ PASS                           }....................
    # Run this code isolated to a Python subprocess, raising an exception on
    # subprocess failure while both forwarding all standard error output by this
    # subprocess to the standard error file handle of the active Python process
    # *AND* capturing and returning all subprocess stdout.
    module_names_str = run_command_forward_stderr_return_stdout(
        command_words=PYTHON_ARGS)

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
        assert re_search(HEAVY_MODULE_NAME_REGEX, module_name) is None, (
            f'@beartype.beartype improperly imports heavyweight module '
            f'"{module_name}" from global scope.'
        )


def test_beartype_optimized(monkeypatch: 'pytest.MonkeyPatch') -> None:
    '''
    Integration test ensuring that the :func:`beartype.beartype` decorator
    behaves as expected under **Python optimization** (e.g., by the
    CPython-specific ``PYTHONOPTIMIZE=1`` environment variable).

    Parameters
    ----------
    monkeypatch : MonkeyPatch
        :mod:`pytest` fixture allowing various state associated with the active
        Python process to be temporarily changed for the duration of this test.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.py.utilpyinterpreter import (
        get_interpreter_command_words)
    from beartype_test._util.command.pytcmdrun import (
        run_command_forward_output)

    # ....................{ LOCALS                         }....................
    # Python code snippet importing, configuring, and applying the @beartype
    # decorator to an arbitrary user-defined callable.
    CODE_OPTIMIZE_BEARTYPE = '''
# ....................{ IMPORTS                            }....................
from beartype import beartype, BeartypeConf
from beartype.roar import BeartypeCallHintParamViolation
from beartype.typing import Union
from beartype._util.py.utilpyinterpreter import is_python_optimized
from pytest import raises

# ....................{ MAIN                               }....................
towertype = beartype(conf=BeartypeConf(is_pep484_tower=True))
"""
Custom :func:`beartype.beartype` decorator configured with non-default options.
"""

@towertype
def towering_func(int_or_float: float) -> float:
    """
    Arbitrary callable decorated by the custom :func:`beartype.beartype`
    decorator defined above, validating that :func:`beartype.beartype` supports
    optimized Python interpreters in configuration mode.
    """

    # Make a gibberish mathematical operation transparently supporting both
    # integers and floating-point numbers so, Ensign Bear!
    return int_or_float ** int_or_float ^ round(int_or_float)


@beartype
def untowering_func(int_or_float: Union[int, float]) -> Union[int, float]:
    """
    Arbitrary callable decorated by the standard :func:`beartype.beartype`
    decorator imported above, validating that :func:`beartype.beartype` supports
    optimized Python interpreters in decoration mode.
    """

    # Make a gibberish mathematical operation transparently supporting both
    # integers and floating-point numbers so, Ensign Bear!
    return int_or_float ** int_or_float ^ round(int_or_float)

# ....................{ ASSERTS                            }....................
# Assert these callables when passed valid input return the expected result.
assert towering_func(3) == 24
assert untowering_func(3) == 24

# Type of exception expected to be raised by passing this callable invalid
# input, defined as either...
exception_type_expected = (
    # If the active Python interpreter is optimized, the expected low-level
    # builtin CPython runtime exception;
    TypeError
    if is_python_optimized() else
    # Else, the active Python interpreter is unoptimized. In this case, the
    # expected @beartype-specific type-checking violation.
    BeartypeCallHintParamViolation
)

# Assert these callables when passed invalid input raise the expected exception.
with raises(exception_type_expected):
    towering_func("Until he reach'd the great main cupola;")
with raises(exception_type_expected):
    untowering_func('There standing fierce beneath, he stampt his foot,')
'''

    # Tuple of all arguments to be passed to the active Python interpreter rerun
    # as an external command.
    PYTHON_ARGS = get_interpreter_command_words() + (
        '-c', CODE_OPTIMIZE_BEARTYPE,)

    # ....................{ PASS                           }....................
    # For all relevant values of the "${PYTHONOPTIMIZE}" environment variable,
    # where:
    # * A value of "0" disables Python optimization.
    # * A value of "1" enables the lowest level of Python optimization.
    for python_optimize_value in ('0', '1',):
        # Temporarily set the Python optimization state by setting the
        # "${PYTHONOPTIMIZE}" environment variable to this string value.
        monkeypatch.setenv('PYTHONOPTIMIZE', python_optimize_value)

        # Run this code isolated to a (possibly optimized) Python subprocess,
        # raising an exception on subprocess failure while both forwarding all
        # standard output and error output by this subprocess to the standard
        # output and error file handles of the active Python process.
        run_command_forward_output(command_words=PYTHON_ARGS)
