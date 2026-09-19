#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide **intraprocess import hook CrossHair integration tests** (i.e.,
validating :mod:`beartype.claw` import hooks with respect to the third-party
CrossHair API within the active Python process).
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
from beartype_test._util.mark.pytskip import skip_unless_package  #, skip

# ....................{ TESTS                              }....................
# @skip('Currently broken. *sigh*')
@skip_unless_package('crosshair')
@pytest.mark.run_in_subprocess
def test_claw_crosshair() -> None:
    '''
    Test :mod:`beartype.claw` import hooks against a CrossHair-specific data
    subpackage in this test suite exercising these hooks against the third-party
    CrossHair API. Official CrossHair documentation encourages users to run
    CrossHair via external ``crosshair check`` and ``crosshair watch`` commands
    at the command line. These commands unconditionally replace *all* existing
    **path hooks** (i.e., low-level import hooks added to the standard
    :pep:`302`-compliant :mod:`sys.path_hooks` list) with non-standard
    pseudocallable :class:`crosshair.pure_importer.PreferPureLoaderHook`
    instances. Due to being non-standard, these instances are non-trivial to
    introspect and thus hostile to import hooks published by competing
    third-party packages, including :mod:`beartype`.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.claw import beartype_package
    from beartype.claw._clawstate import reinit_claw_state
    from crosshair.pure_importer import prefer_pure_python_imports

    # ....................{ ASSERTS                        }....................
    # Thread-safely reinitialize *ALL* beartype import hook state. Crucially,
    # doing so also removes the beartype-specific "sys.path_hooks" entry
    # previously added to that list by a prior beartype import hook registered
    # by a prior test (if any). Doing so ensures that the beartype import hook
    # registered below will necessarily attempt to add this entry back to this
    # list. Since doing *THAT* requires introspecting that list, this altogether
    # ensures that the call to that beartype import hook below will raise an
    # exception unless beartype has correctly implemented support for
    # CrossHair-specific introspection-hostile "sys.path_hooks". It's hard, fam.
    reinit_claw_state()

    # In a CrossHair-specific context manager temporarily replacing *ALL*
    # introspection-friendly "sys.path_hooks" with CrossHair-specific
    # introspection-hostile "sys.path_hooks"...
    with prefer_pure_python_imports():
        # Subject a CrossHair-specific data package to a beartype import hook,
        # configured by the default beartype configuration.
        #
        # Note that merely attempting to register a beartype path hook under
        # this introspection-hostile context manager *WILL* raise an exception
        # unless the "beartype.claw" subpackage explicitly supports CrossHair.
        beartype_package('beartype_test.a90_func.data.claw.external.crosshair')

        # Import all submodules of the package hooked above, exercising that
        # these submodules are subject to that import hook *AND* satisfy all
        # integration tests implemented as assertion statements in these
        # submodules.
        from beartype_test.a90_func.data.claw.external.crosshair import (
            data_claw_crosshair)

        # Thread-safely reinitialize *ALL* beartype import hook state... yet
        # again. Why? Because the CrossHair-specific
        # prefer_pure_python_imports() context manager called above internally
        # asserts that *ALL* "sys.path_hooks" entries are still instances of the
        # third-party "crosshair.pure_importer.PreferPureLoaderHook" type, which
        # that context manager ensures upon entry. Of course, the above logic
        # violated that simple constraint by injecting our own beartype import
        # hook into the "sys.path_hooks" list *AFTER* that context manager had
        # already wrapped all prior "sys.path_hooks" entries in instances of
        # that type. This is insane. Blame CrossHair and its malignancy.
        reinit_claw_state()
        # print('After test!')
