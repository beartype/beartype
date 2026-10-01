#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Third-party **Coverage.py** integration tests.

This submodule functionally tests the :mod:`beartype` package against the
third-party :mod:`coverage` package.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package, skip

# ....................{ TESTS                              }....................
@skip_unless_package('coverage')
def test_claw_coverage_option_source(tmp_path: 'pathlib.Path') -> None:
    '''
    Integration test validating that :mod:`beartype.claw` import hooks
    integrate cleanly with the ``--source`` option accepted by the popular
    ``coverage`` entry point-based command exposed by the third-party
    :mod:`coverage` package.

    This test attempts to run that entry point against an empty submodule of a
    test package registering such a hook. Although (deceptively) trivial, this
    logic is actually the minimal reproducible example (MRE) that suffices to
    induce *extreme* circular import recursion in the form of an unreadable
    `ImportError` traceback from the :mod:`coverage` package. If this just
    happened to you, please see also the
    :func:`beartype.claw._importlib._clawimpfileloader._init` initializer.

    Parameters
    ----------
    tmp_path : pathlib.Path
        Abstract path encapsulating a temporary directory unique to this test,
        created in the base temporary directory.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.path.utilpathcopy import copy_dir
    from beartype._util.py.utilpyinterpreter import (
        get_interpreter_command_words)
    from beartype_test._util.command.pytcmdrun import (
        run_command_forward_output)
    from beartype_test._util.path.pytpathtest import (
        get_test_func_data_claw_external_coverage_option_source_dir)
    from pytest import MonkeyPatch

    # ....................{ CONSTANTS                      }....................
    # Tuple of all shell words with which to run the external "coverage"
    # command.
    COVERAGE_ARGS = get_interpreter_command_words() + (
        # Fully-qualified name of the "coverage" package to be run.
        '-m', 'coverage',

        # Instruct Coverage.py to measure coverage against...
        'run',

        # *ONLY THIS SPECIFIC SUBMODULE OF THIS TEST PACKAGE.* For unknown
        # reasons (that almost certainly reduce to "importlib" shenanigans),
        # "beartype.claw" import hooks induce Coverage.py import cycles *ONLY*
        # when Coverage.py is instructed to measure coverage for a submodule.
        # When Coverage.py is instructed to measure coverage against an entire
        # project (as is the default), "beartype.claw" import hooks *NEVER*
        # induce Coverage.py import cycles.
        #
        # Don't blame us. We voted for Beardos.
        '--source', 'dismal_rack_of_clouds.and_all_along',
        # '--source="dismal_rack_of_clouds.and_all_along"',

        # Instruct Coverage.py to run "pytest" against the "pytest"-based test
        # suite also bundled with this package.
        '-m', 'pytest', 'dismal_rack_of_clouds_tests/',
    )

    # ....................{ LOCALS                         }....................
    # Path object encapsulating the absolute dirname of the test-specific data
    # directory containing an empty Coverage.py-managed project whose
    # "pyproject.toml" file requires "beartype" as a Coverage.py-specific
    # mandatory runtime dependency.
    project_dir_src = (
        get_test_func_data_claw_external_coverage_option_source_dir())

    # Path object encapsulating the absolute dirname of this same Coverage.py
    # project copied into this temporary directory. Although a symbolic link
    # *MIGHT* suffice as well, we lack faith in Coverage.py. In all likelihood,
    # Coverage.py expects to be able to modify the contents of this directory.
    project_dir_trg = tmp_path / 'coverage_option_source'

    # ....................{ PATHS                          }....................
    # Recursively copy this Coverage.py project into this temporary directory.
    copy_dir(src_dirname=project_dir_src, trg_dirname=project_dir_trg)
    # from os import listdir
    # print(f'src_dirname = "{project_dir_src}"')
    # print(f'trg_dirname = "{project_dir_trg}"')
    # print(f'trg contents = {repr(listdir(project_dir_trg))}')

    # ....................{ COMMANDS                       }....................
    # Inside the equivalent of the "monkeypatch" fixture...
    with MonkeyPatch.context() as monkeypatch:
        # Change the current working directory (CWD) to that of this Coverage.py
        # project.
        monkeypatch.chdir(project_dir_trg)

        # Run the "coverage" command in the current ${PATH} with these options
        # and arguments, raising an exception on subprocess failure while
        # forwarding all standard output and error output by this subprocess to
        # the standard output and error file handles of this parent process.
        run_command_forward_output(command_words=COVERAGE_ARGS)


# @skip('Currently busted, sadly. *sigh*')
@skip_unless_package('coverage')
def test_claw_coverage_line_numbers(tmp_path: 'pathlib.Path') -> None:
    '''
    Integration test validating that :mod:`beartype.claw` import hooks
    preserve line numbers and thus coverage reported by the popular ``coverage``
    entry point exposed by the third-party :mod:`coverage` package.

    This test specifically asserts that Coverage.py reports full coverage for a
    generator function defining a ``for`` loop in a module hooked by a
    :mod:`beartype.claw` import hook.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.path.utilpathcopy import copy_dir
    from beartype._util.py.utilpyinterpreter import (
        get_interpreter_command_words)
    from beartype_test._util.command.pytcmdrun import (
        run_command_forward_output)
    from beartype_test._util.path.pytpathtest import (
        get_test_func_data_claw_external_coverage_line_numbers_dir)
    from pytest import MonkeyPatch

    # ....................{ CONSTANTS                      }....................
    # Tuple of all shell words running the external "coverage" command to
    # measure coverage against a test package.
    COVERAGE_MEASURE_ARGS = get_interpreter_command_words() + (
        # Fully-qualified name of the "coverage" package to be run.
        '-m', 'coverage',

        # Instruct Coverage.py to measure coverage against...
        'run',

        # All possible code branches of (rather than merely the subset of
        # actually executed branches)...
        '--branch',

        # *ONLY THIS SPECIFIC SUBMODULE OF THIS TEST PACKAGE.*
        '--source', 'line_numbers',

        # Instruct Coverage.py to run "pytest" against the "pytest"-based test
        # suite also bundled with this package.
        '-m', 'line_numbers',
    )

    # Tuple of all shell words running the external "coverage" command to
    # generate a report of the coverage measured by the above command.
    COVERAGE_REPORT_ARGS = get_interpreter_command_words() + (
        # Fully-qualified name of the "coverage" package to be run.
        '-m', 'coverage',

        # Instruct Coverage.py to report the coverage measured by the above
        # "coverage" command.
        'report',

        # Instruct Coverage.py to fail with non-zero exit status if coverage is
        # reported as anything less than perfect.
        '--fail-under=100',
    )

    # ....................{ LOCALS                         }....................
    # Path object encapsulating the absolute dirname of the test-specific data
    # directory containing an empty Coverage.py-managed project whose
    # "pyproject.toml" file requires "beartype" as a Coverage.py-specific
    # mandatory runtime dependency.
    project_dir_src = (
        get_test_func_data_claw_external_coverage_line_numbers_dir())

    # Path object encapsulating the absolute dirname of the parent directory of
    # this same Coverage.py project copied into this temporary directory.
    project_dir_trg_parent = tmp_path / 'coverage_line_numbers'

    # Path object encapsulating the absolute dirname of this same Coverage.py
    # project copied into that parent directory. Although a symbolic link
    # *MIGHT* suffice as well, we lack faith in Coverage.py. In all likelihood,
    # Coverage.py expects to be able to modify the contents of this directory.
    project_dir_trg = project_dir_trg_parent / 'line_numbers'

    # ....................{ PATHS                          }....................
    # Recursively copy this Coverage.py project into this temporary directory.
    copy_dir(src_dirname=project_dir_src, trg_dirname=project_dir_trg)
    # from os import listdir
    # print(f'src_dirname = "{project_dir_src}"')
    # print(f'trg_dirname = "{project_dir_trg}"')
    # print(f'trg contents = {repr(listdir(project_dir_trg))}')

    # ....................{ COMMANDS                       }....................
    # Inside the equivalent of the "monkeypatch" fixture...
    with MonkeyPatch.context() as monkeypatch:
        # Change the current working directory (CWD) to that of this Coverage.py
        # project.
        monkeypatch.chdir(project_dir_trg_parent)

        # Run the "coverage" command in the current ${PATH} with these options
        # and arguments, raising an exception on subprocess failure while
        # forwarding all standard output and error output by this subprocess to
        # the standard output and error file handles of this parent process.
        #
        # The first "coverage" run measures coverage against this test package.
        # The final "coverage" run reports this coverage.
        run_command_forward_output(command_words=COVERAGE_MEASURE_ARGS)
        run_command_forward_output(command_words=COVERAGE_REPORT_ARGS)
