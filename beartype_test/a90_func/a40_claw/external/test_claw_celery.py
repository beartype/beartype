#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **intraprocess import hook Celery integration tests** (i.e.,
exercising :mod:`beartype.claw` import hooks specific to the third-party
Celery API within the active Python process).
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
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
@pytest.mark.run_in_subprocess
@skip_unless_package('celery')
def test_claw_celery() -> None:
    '''
    Test :mod:`beartype.claw` import hooks against a Celery-specific data
    subpackage in this test suite exercising these hooks against the third-party
    Celery API known to publish decorator-hostile decorators.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.claw import beartype_package

    # ....................{ LOCALS                         }....................
    # Name of the single package to be subject to beartype import hooks below.
    PACKAGE_NAME = 'beartype_test.a90_func.data.claw.celery'

    # ....................{ PASS                           }....................
    # Explicitly subject this single package to a beartype import hook
    # configured by the default beartype configuration.
    beartype_package(PACKAGE_NAME)

    # Import all submodules of the package hooked above, exercising that these
    # submodules are subject to that import hook *AND* satisfy all integration
    # tests implemented as assertion statements in these submodules.
    from beartype_test.a90_func.data.claw.celery.data_claw_celery import (
        amazed_and_full_of_fear)
    # print('[data_claw_celery] amazed_and_full_of_fear:')
    # celery_task = amazed_and_full_of_fear.__class__.__mro__[-2]
    # print(celery_task.__module__)
    # print(celery_task.__qualname__)
    # print(celery_task.__name__)
    # print(amazed_and_full_of_fear.__module__)
    # print(amazed_and_full_of_fear.__qualname__)
    # print(amazed_and_full_of_fear.__class__.__module__)
    # print(amazed_and_full_of_fear.__class__.__name__)
    # print(amazed_and_full_of_fear.__class__.__qualname__)
    # print(amazed_and_full_of_fear.__class__.__mro__)
    # print(dir(amazed_and_full_of_fear))
    # print(dir(amazed_and_full_of_fear.__class__))

    # Implicitly assert that the @beartype decorator avoids raising exceptions
    # (typically by internally reducing to a noop) when decorating uncallable
    # objects produced by Celery-specific decorator-hostile decorators.
    amazed_and_full_of_fear_beartyped = beartype(amazed_and_full_of_fear)

    # Assert that the @beartype decorator actually did reduce to a noop.
    assert amazed_and_full_of_fear is amazed_and_full_of_fear_beartyped
