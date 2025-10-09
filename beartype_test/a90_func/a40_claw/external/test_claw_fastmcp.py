#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **intraprocess import hook FastMCP integration tests** (i.e.,
exercising :mod:`beartype.claw` import hooks specific to the third-party
FastMCP API within the active Python process).
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
from beartype_test._util.mark.pytskip import (
    skip_unless_os_linux,
    skip_unless_package,
)

# ....................{ TESTS                              }....................
# Explicitly skip this integration test under both vanilla Microsoft Windows
# *AND* macOS, where this test inexplicably erupts in unreadable pickling errors
# resembling:
#     _pickle.PicklingError: Can't pickle <function test_claw_fastmcp at
#     0x000001DCDB47AA20>: it's not the same object as
#     beartype_test.a90_func.a40_claw.external.test_claw_fastmcp.test_claw_fastmcp
#
# Clearly, this relates to coroutines. Private OS-specific implementations of
# the standard "pickle" module fail to cope with coroutines, apparently. *shrug*
@skip_unless_package('fastmcp')
@skip_unless_os_linux()
@pytest.mark.run_in_subprocess
async def test_claw_fastmcp() -> None:
    '''
    Test :mod:`beartype.claw` import hooks against a FastMCP-specific data
    subpackage in this test suite exercising these hooks against the third-party
    FastMCP API known to publish decorator-hostile decorators.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.claw import beartype_package

    # ....................{ LOCALS                         }....................
    # Name of the single package to be subject to beartype import hooks below.
    PACKAGE_NAME = 'beartype_test.a90_func.data.claw.fastmcp'

    # ....................{ PASS                           }....................
    # Explicitly subject this single package to a beartype import hook
    # configured by the default beartype configuration.
    beartype_package(PACKAGE_NAME)

    # Import all submodules of the package hooked above, exercising that these
    # submodules are subject to that import hook.
    from beartype_test.a90_func.data.claw.fastmcp.data_claw_fastmcp import (
        data_claw_fastmcp_main,
        with_stride_colossal,
    )

    # Asynchronously run the main public coroutine exported by that submodule,
    # thus asserting that *ALL* integration tests (implemented as assertion
    # statements) in that submodule are satisfied.
    await data_claw_fastmcp_main()
    # print('[test_claw_fastmcp] with_stride_colossal:')
    # print(with_stride_colossal.__module__)
    # print(with_stride_colossal.__class__.__name__)

    # Implicitly assert that the @beartype decorator avoids raising exceptions
    # (typically by internally reducing to a noop) when decorating uncallable
    # objects produced by FastMCP-specific decorator-hostile decorators.
    with_stride_colossal_beartyped = beartype(with_stride_colossal)

    # Assert that the @beartype decorator actually did reduce to a noop.
    assert with_stride_colossal is with_stride_colossal_beartyped
