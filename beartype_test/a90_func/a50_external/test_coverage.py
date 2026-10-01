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
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
@skip_unless_package('coverage')
def test_coverage_beartype_claw_generator_branch(
    tmp_path: 'pathlib.Path',
) -> None:
    '''A hooked, fully consumed generator has no missing exit branch.'''
    from os import environ, pathsep
    from pathlib import Path
    from subprocess import run
    from sys import executable
    import beartype

    package_dir = tmp_path / 'pkg'
    package_dir.mkdir()
    (package_dir / '__init__.py').write_text(
        'from collections.abc import Iterator\n'
        'from beartype import beartype\n'
        '\n'
        '@beartype\n'
        'def values() -> Iterator[int]:\n'
        '    for value in (1, 2):\n'
        '        yield value\n'
    )
    (tmp_path / 'run.py').write_text(
        'from beartype.claw import beartype_package\n'
        'beartype_package("pkg")\n'
        'from pkg import values\n'
        'assert list(values()) == [1, 2]\n'
    )

    # Make the checkout available when the child process runs outside it.
    beartype_parent = str(Path(beartype.__file__).resolve().parent.parent)
    child_env = dict(environ)
    child_env['PYTHONPATH'] = pathsep.join(filter(None, (
        beartype_parent, child_env.get('PYTHONPATH', ''))))
    run(
        (executable, '-m', 'coverage', 'run', '--branch', '--source=pkg',
         'run.py'),
        cwd=tmp_path, env=child_env, check=True, capture_output=True,
        text=True,
    )
    run(
        (executable, '-m', 'coverage', 'report', '--fail-under=100'),
        cwd=tmp_path, env=child_env, check=True, capture_output=True,
        text=True,
    )


@skip_unless_package('coverage')
def test_coverage_beartype_claw(tmp_path: 'pathlib.Path') -> None:
    '''
    Integration test validating that :func:`beartype.claw` import hooks
    integrate cleanly with the popular ``coverage`` entry point exposed by the
    third-party :mod:`coverage` package.

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
        get_test_func_data_external_coverage_dir)
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
    # "pyproject.toml" file requires "beartype" as a Coverage.py-specific mandatory
    # runtime dependency.
    project_dir_src = get_test_func_data_external_coverage_dir()

    # Path object encapsulating the absolute dirname of this same Coverage.py
    # project copied into this temporary directory. Although a symbolic link
    # *MIGHT* suffice as well, we lack faith in Coverage.py. In all likelihood,
    # Coverage.py expects to be able to modify the contents of this directory.
    project_dir_trg = tmp_path / 'coverage'

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
