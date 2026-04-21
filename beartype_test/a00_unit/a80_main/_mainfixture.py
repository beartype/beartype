#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **main type-checking unit test fixtures** (i.e., :mod:`pytest`-specific
context managers passed as parameters to unit tests validating the main
:func:`beartype.beartype` decorator and related type-checking functions).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import fixture

# ....................{ FIXTURES ~ equality                }....................
@fixture(autouse=True, scope='function')
def fail_if_output(capsys: 'pytest.capsys') -> None:
    '''
    Validate that the current test emitted *no* standard output or error. This
    validation guards against debugging-specific :func:`print` statements in the
    main :mod:`beartype` codebase accidentally uncommented during debugging.

    Note that this unit test-scoped fixture is implicitly performed *before*
    each unit test transitively defined in sibling and child submodules of the
    subpackage directly containing this submodule. Why? Because failing to do so
    would invite subtle but easily reproducible issues in the main codebase.

    Parameters
    ----------
    capsys : pytest.capsys
        Fixture enabling tests to selectively capture standard output and error.
    '''

    # Dataclass providing all standard output and error erroneously emitted by
    # this test.
    captured = capsys.readouterr()

    # Assert that this test emitted *NO* standard output or error.
    assert captured.out == ''
    assert captured.err == ''
