#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide **intraprocess import hook Python optimization integration tests**
(i.e., validating :mod:`beartype.claw` import hooks with respect to optimization
of the active Python interpreter by either the ``-O`` command-line option *or*
the ``${PYTHONOPTIMIZE}`` environment variable).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: Isolate each integration test defined below to its own subprocess.
# Why? Module imports. Since each integration test defined below tends to
# reimport the same (or, at least, similar) modules as previously run unit tests
# defined below, module imports and thus unit tests *MUST* be isolated to their
# own subprocesses to ensure these tests may be run in any arbitrary order.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import pytest

# ....................{ TESTS                              }....................
@pytest.mark.run_in_subprocess
def test_claw_optimized() -> None:
    '''
    Test :mod:`beartype.claw` import hooks against a Python
    optimization-specific data subpackage in this test suite exercising these
    hooks against **Python optimization** (i.e., the ``-O`` command-line option
    *and* ``${PYTHONOPTIMIZE}`` environment variable).

    Note that what *should* be a single integration test is intentionally
    subdivided into two integration tests -- this and the sibling
    :func:`.test_claw_unoptimized` test. Although unifying both into a single
    integration test would certainly be preferable, doing so is complicated by
    the need to reload the Python optimization-specific data package to which
    :mod:`beartype.claw` import hooks are applied. Since Python lacks any
    official support for module reloading, these two integration tests are
    instead isolated to subprocesses -- trivially circumventing the need for
    module reloading in the first place.

    See Also
    --------
    :func:`.test_claw_unoptimized`
        Companion integration test.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.claw import beartype_package
    from pytest import MonkeyPatch

    # ....................{ PASS                           }....................
    # Inside the equivalent of the "monkeypatch" fixture...
    with MonkeyPatch.context() as monkeypatch:
        # Temporarily set the Python optimization state by setting the
        # "${PYTHONOPTIMIZE}" environment variable to a positive integer.
        monkeypatch.setenv('PYTHONOPTIMIZE', '1')

        # Subject a Python optimization-specific data package to a beartype
        # import hook, configured by the default beartype configuration.
        beartype_package('beartype_test.a90_func.data.claw.internal.optimized')

        # Import all submodules of the package hooked above, exercising that
        # these submodules are subject to that import hook *AND* satisfy all
        # integration tests implemented as assertion statements in these
        # submodules.
        from beartype_test.a90_func.data.claw.internal.optimized import (
            data_claw_optimized)


@pytest.mark.run_in_subprocess
def test_claw_unoptimized() -> None:
    '''
    Test :mod:`beartype.claw` import hooks against a Python
    optimization-specific data subpackage in this test suite exercising these
    hooks against a lack of **Python optimization** (i.e., the ``-O``
    command-line option *and* ``${PYTHONOPTIMIZE}`` environment variable).

    See Also
    --------
    :func:`.test_claw_optimized`
        Companion integration test.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.claw import beartype_package

    # ....................{ PASS                           }....................
    # Subject a Python optimization-specific data package to a beartype
    # import hook, configured by the default beartype configuration.
    #
    # Note that, since this test suite is *ALWAYS* run unoptimized and this
    # integration test inherits that state, this integration test is also
    # implicitly run unoptimized. So it goes in Python world. \o/
    beartype_package('beartype_test.a90_func.data.claw.internal.optimized')

    # Import all submodules of the package hooked above, exercising that
    # these submodules are subject to that import hook *AND* satisfy all
    # integration tests implemented as assertion statements in these
    # submodules.
    from beartype_test.a90_func.data.claw.internal.optimized import (
        data_claw_optimized)
