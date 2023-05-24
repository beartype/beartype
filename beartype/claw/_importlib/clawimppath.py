#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype all-at-once low-level package name cache.**

This private submodule caches package names on behalf of the higher-level
:func:`beartype.claw.beartype_package` function. Beartype import
path hooks internally created by that function subsequently lookup these package
names from this cache when deciding whether or not (and how) to decorate a
submodule being imported with :func:`beartype.beartype`.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.claw._importlib._clawimpload import BeartypeSourceFileLoader
from importlib import invalidate_caches as clear_importlib_caches
from importlib.machinery import (
    SOURCE_SUFFIXES,
    FileFinder,
)
from sys import (
    path_hooks,
    path_importer_cache,
)

# ....................{ PRIVATE ~ adders                   }....................
def add_path_hook_if_needed() -> None:
    '''
    Add our **beartype import path hook singleton** (i.e., single callable
    guaranteed to be inserted at most once to the front of the standard
    :mod:`sys.path_hooks` list recursively applying the
    :func:`beartype.beartype` decorator to all well-typed callables and classes
    defined by all submodules of all packages previously registered by a call to
    the :func:`beartype.claw._pkg.clawpkgmain.add_packages` function) if this
    path hook has yet to be added *or* silently reduce to a noop otherwise
    (i.e., if this path hook has already been added).

    See Also
    ----------
    https://stackoverflow.com/a/43573798/2809027
        StackOverflow answer strongly inspiring the low-level implementation of
        this function with respect to inscrutable :mod:`importlib` machinery.
    '''

    # Global variables reassigned below.
    global _is_path_hook_added

    # If this function has already been called under the active Python
    # interpreter, silently reduce to a noop.
    if _is_path_hook_added:
        return
    # Else, this function has *NOT* yet been called under this interpreter.

    # 2-tuple of the undocumented format expected by the FileFinder.path_hook()
    # class method called below, associating our beartype-specific source file
    # loader with the platform-specific filetypes of all sourceful Python
    # packages and modules. We didn't do it. Don't blame the bear.
    LOADER_DETAILS = (BeartypeSourceFileLoader, SOURCE_SUFFIXES)

    # Closure instantiating a new "FileFinder" instance invoking this loader.
    #
    # Note that we intentionally ignore mypy complaints here. Why? Because mypy
    # erroneously believes this method accepts 2-tuples whose first items are
    # loader *INSTANCES* (e.g., "Tuple[Loader, List[str]]"). In fact, this
    # method accepts 2-tuples whose first items are loader *TYPES* (e.g.,
    # "Tuple[Type[Loader], List[str]]"). This is why we can't have nice.
    loader_factory = FileFinder.path_hook(LOADER_DETAILS)  # type: ignore[arg-type]

    # Prepend a new path hook (i.e., factory closure encapsulating this loader)
    # *BEFORE* all other path hooks.
    path_hooks.insert(0, loader_factory)

    # Prevent subsequent calls to this function from erroneously re-adding
    # duplicate copies of this path hook immediately *AFTER* successfully adding
    # the first such path hook.
    _is_path_hook_added = True

    # Uncache *ALL* competing loaders cached by prior importations. Just do it!
    path_importer_cache.clear()
    clear_importlib_caches()

# ....................{ PRIVATE ~ globals                  }....................
_is_path_hook_added = False
'''
:data:`True` only if the :func:`._add_path_hook_if_needed` function has been
previously called at least once under the active Python interpreter.
'''
