#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **import hook file finder** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype.claw._importlib._clawimpfilefinder` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_make_beartype_file_finder_path_hook_index() -> None:
    '''
    Test the
    :func:`beartype.claw._importlib._clawimpfilefinder.make_beartype_file_finder_path_hook_index`
    factory.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    import sys
    from importlib import _bootstrap_external
    from pytest import MonkeyPatch

    # ....................{ ASSERTS                        }....................
    # Assert that the make_beartype_file_finder_path_hook_index() factory
    # function behaves as expected under the standard (i.e., non-monkey-patched)
    # Python environment.
    _assert_make_beartype_file_finder_path_hook_index()

    # Inside the equivalent of the "monkeypatch" fixture...
    with MonkeyPatch.context() as monkeypatch:
        # Temporarily destroy the standard "sys.path_hooks" list required to
        # import packages and modules, triggering edge case logic in this
        # factory.
        #
        # Note that doing so, of course, prevents *ANY* package or module that
        # has not already been imported from being imported for the duration of
        # this monkey-patch.
        monkeypatch.setattr(sys, 'path_hooks', [])

        # Assert that the make_beartype_file_finder_path_hook_index() factory
        # function behaves as expected under this non-standard (i.e.,
        # monkey-patched) Python environment.
        _assert_make_beartype_file_finder_path_hook_index()

    #FIXME: Test one additional edge case, please. Unfortunately, we have *NO*
    #idea how. We tried below. Didn't work. It does nothing. It might not even
    #be feasible to test this edge case. Nonetheless:
    #* While still applying the above "sys.path_hooks" monkey-patch,
    #  monkey-patch the "importlib._bootstrap_external" submodule by deleting
    #  the _get_supported_file_loaders() getter. Look. Just do it! \o/

    # # Inside the equivalent of the "monkeypatch" fixture...
    # with MonkeyPatch.context() as monkeypatch:
    #     # Temporarily destroy the standard "sys.path_hooks" list required to
    #     # import packages and modules, triggering edge case logic in this
    #     # factory.
    #     #
    #     # Note that doing so, of course, prevents *ANY* package or module that
    #     # has not already been imported from being imported for the duration of
    #     # this monkey-patch.
    #     monkeypatch.setattr(sys, 'path_hooks', [])
    #     monkeypatch.setattr(sys, 'modules', [])
    #     monkeypatch.delattr(_bootstrap_external, '_get_supported_file_loaders')
    #
    #
    #     # Assert that the make_beartype_file_finder_path_hook_index() factory
    #     # function behaves as expected under this non-standard (i.e.,
    #     # monkey-patched) Python environment.
    #     _assert_make_beartype_file_finder_path_hook_index()

# ....................{ PRIVATE ~                          }....................
def _assert_make_beartype_file_finder_path_hook_index() -> None:
    '''
    Assert that the 
    :func:`beartype.claw._importlib._clawimpfilefinder.make_beartype_file_finder_path_hook_index`
    factory behaves as expected under the current Python environment, including
    any temporary monkey-patches applied to that environment by the parent
    :func:`.test_make_beartype_file_finder_path_hook_index` unit test
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.claw._importlib._clawimpfilefinder import (
        make_beartype_file_finder_path_hook_index)
    from beartype.claw._importlib._clawimpfileloader import (
        BeartypeSourceFileLoader)
    from beartype_test._util.path.pytpathmain import get_main_dir
    from importlib.machinery import (
        FileFinder,
        ModuleSpec,
    )
    from sys import path_hooks

    # ....................{ PATH HOOK                      }....................
    # Beartype-specific file finder path hook created by this factory and the
    # 0-based index of the "sys.path_hooks" list into which this path hook
    # should be inserted by the caller.
    path_hook, path_hook_index = make_beartype_file_finder_path_hook_index()

    # Assert that this path hook is callable.
    assert callable(path_hook)

    # Assert that this index is a non-negative integer in this inclusive range.
    assert isinstance(path_hook_index, int)
    assert 0 <= path_hook_index <= len(path_hooks) + 1

    # Absolute dirname of an arbitrary directory guaranteed to both exist *AND*
    # contain ".py"-suffixed Python source modules: namely, the top-level
    # directory defining the "beartype" package.
    package_dirname = str(get_main_dir())

    # ....................{ FILE FINDER                    }....................
    # Beartype-specific file finder created by this passing this path hook the
    # absolute dirname of an arbitrary directory guaranteed to exist. Why?
    # Because the file finder path hook API is... odd, frankly. If passed
    # *ANYTHING* other than the absolute dirname of an existing directory, the
    # closure called here (created and returned by the FileFinder.path_hook()
    # method called by the above call to the
    # make_beartype_file_finder_path_hook_index() factory) raises the
    # non-human-readable exception:
    #     ImportError: only directories are supported
    file_finder = path_hook(package_dirname)

    # Assert that this object is a file finder.
    assert isinstance(file_finder, FileFinder)

    # ....................{ MODULE SPEC                    }....................
    # Module spec encapsulating the importation of the "beartype" package by
    # this file finder.
    module_spec = file_finder.find_spec('beartype')

    # Assert that this object is a module spec.
    assert isinstance(module_spec, ModuleSpec)

    # ....................{ FILE LOADER                    }....................
    # Assert that this file finder instructs Python to load the "beartype"
    # package via our beartype-specific source file loader.
    assert isinstance(module_spec.loader, BeartypeSourceFileLoader)
