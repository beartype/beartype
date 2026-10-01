#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype-hostile import hook intraprocess unit tests** (i.e., validating edge
cases of :mod:`beartype.claw` import hooks unique to **beartype-hostile
import hooks** (i.e., external import hooks mimicking existing competing import
hooks published by real-world third-party packages and modules, which silently
override :func:`beartype.claw` import hooks and thus silently prevent
:mod:`beartype` from applying runtime type-checking to *any* submodules of this
subpackage) within the active Python process).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: Isolate each unit test defined below to its own subprocess. Why?
# Module imports. Since each unit test defined below tends to reimport the same
# (or, at least, similar) modules as previously run unit tests defined below,
# module imports and thus unit tests *MUST* be isolated to their own
# subprocesses to ensure these tests may be run in any arbitrary order.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import pytest

# ....................{ TESTS                              }....................
@pytest.mark.run_in_subprocess
def test_claw_intraprocess_claw_hostile() -> None:
    '''
    Test the :mod:`beartype.claw.beartype_package` import hook against a single
    data subpackage in this test suite exercising *all* edge cases associated
    with this import hook unique to **beartype-hostile import hooks** (i.e.,
    external import hooks mimicking existing competing import hooks published by
    real-world third-party packages and modules, which silently override
    :func:`beartype.claw` import hooks and thus silently prevent :mod:`beartype`
    from applying runtime type-checking to *any* submodules of this subpackage).
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.claw import (
        beartype_package,
        warn_if_beartype_claw_inactive,
    )
    from beartype.claw._importlib._clawimpfilefinder import (
        is_beartype_file_finder_path_hook)
    from beartype.roar import (
        BeartypeClawImportlibFileFinderPathHookInactiveWarning)
    from importlib.machinery import PathFinder
    from pytest import (
        MonkeyPatch,
        warns,
    )

    # Mimic imports performed in the "importlib._bootstrap_external" submodule.
    import sys
    import warnings as _warnings

    # ....................{ SUBCLASSES                     }....................
    class PathFinderBeartypeHater(PathFinder):
        '''
        **Beartype-hostile meta path hook** (i.e., :class:`.PathFinder` subclass
        explicitly ignoring *only* :mod:`beartype.claw` import hooks, intended
        to be injected as a drop-in replacement of the standard
        :mod:`beartype`-friendly :class:`.PathFinder` into the global
        :obj:`sys.meta_path` list).

        Caveats
        -------
        **This path finder is probably non-thread-safe.** This path finder is
        thus suitable for use only in a single-threaded test suite.
        '''

        @staticmethod
        def _path_hooks(path: str) -> object:
            '''
            Search the global :obj:`sys.path_hooks` list for an applicable path
            hook suitable for importing the Python package or module with the
            passed absolute or relative pathname.

            This override of the standard :meth:`.FileFinder._path_hooks` method
            monkey-patches that method to explicitly ignore *only*
            :mod:`beartype.claw` import hooks and thus be beartype-hostile.
            '''

            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # CAUTION: This code is copied verbatim from the standard
            # implementation of this method in the Python standard library.
            # Avoid modifying, yo!
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if sys.path_hooks is not None and not sys.path_hooks:
                _warnings.warn('sys.path_hooks is empty', ImportWarning)
            for hook in sys.path_hooks:
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # MINIMALIST MONKEY-PATCH: You Begin Now!
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # If this path hook is the beartype-specific file finder path
                # hook added by the call to the beartype_this_package() import
                # hook below, simulate a real-world beartype-hostile meta path
                # hook by silently ignoring this path hook.
                if is_beartype_file_finder_path_hook(hook):
                    continue
                # Else, this path hook is *NOT* beartype-specific. In this case,
                # defer to this path hook in the standard PEP 302-compliant way.
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # MINIMALIST MONKEY-PATCH: You End Now. What? Already!?
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # CAUTION: This code is copied verbatim from the standard
            # implementation of this method in the Python standard library.
            # Avoid modifying, yo!
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                try:
                    return hook(path)
                except ImportError:
                    continue
            else:
                return None

    # ....................{ LOCALS                         }....................
    # Name of the single package defining submodules defining callables and
    # types subjected to one or more beartype-hostile import hooks, which we
    # attempt (but fails) to also subject to beartype import hooks below.
    PACKAGE_NAME = (
        'beartype_test.a00_unit.data.claw.intraprocess.hookable_package.claw_hostile')

    # ....................{ ASSERTS                        }....................
    # Inside the equivalent of the "monkeypatch" fixture...
    with MonkeyPatch.context() as monkeypatch:
        # ....................{ META PATH                  }....................
        # Shallow copy of the standard "sys.meta_path" list.
        meta_path_new = sys.meta_path[:]

        # Inject the beartype-hostile meta path hook defined above into this
        # list the most hostile way possible, which is also (sadly) the most
        # common use pattern for registering *ANY* hook. Specifically, override
        # *ALL* competing path hooks by shoving straight to the front of the
        # line. Beartype hate: "It feels bad."
        meta_path_new.insert(0, PathFinderBeartypeHater)

        # Temporarily replace the standard "sys.meta_path" list required to
        # import packages and modules with this beartype-hostile list.
        #
        # Note that doing so, of course, prevents "beartype.claw" import hooks
        # from automatically runtime type-checking *ANY* subsequently imported
        # package or module for the duration of this monkey-patch.
        monkeypatch.setattr(sys, 'meta_path', meta_path_new)

        # ....................{ WARNINGS                   }....................
        #FIXME: Uncomment this once we successfully resolve feature request #674
        #*AND* uncomment the following call in add_beartype_path_hook():
        #    warn_if_beartype_claw_inactive()
        # with warns(BeartypeClawImportlibFileFinderPathHookInactiveWarning):
        #     beartype_package(PACKAGE_NAME)

        # Subject this single package to a default beartype import hook.
        beartype_package(PACKAGE_NAME)

        # Assert that this warner issues the expected warning that that beartype
        # import hook is actually inactive.
        with warns(BeartypeClawImportlibFileFinderPathHookInactiveWarning):
            warn_if_beartype_claw_inactive()

        # Import that package, which then imports all submodules of that package,
        # validating that these submodules were *NOT* transitively subject to
        # "beartype.claw" import hooks due to the beartype-hostile import hook
        # registered above.
        from beartype_test.a00_unit.data.claw.intraprocess.hookable_package import (
            claw_hostile)
