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
from beartype.typing import Optional
from beartype._data.datatyping import ImportPathHook
from importlib import invalidate_caches
from importlib.machinery import (
    SOURCE_SUFFIXES,
    FileFinder,
)
from sys import (
    path_hooks,
    path_importer_cache,
)

# ....................{ ADDERS                             }....................
#FIXME: Unit test us up, please.
def add_beartype_pathhook() -> None:
    '''
    Add our **beartype import path hook singleton** (i.e., single callable
    guaranteed to be inserted at most once to the front of the standard
    :mod:`sys.path_hooks` list recursively applying the
    :func:`beartype.beartype` decorator to all well-typed callables and classes
    defined by all submodules of all packages previously registered by a call to
    a public :func:`beartype.claw` function) if this path hook has yet to be
    added *or* silently reduce to a noop otherwise (i.e., if this path hook has
    already been added).

    Caveats
    ----------
    **This function is non-thread-safe.** For both simplicity and efficiency,
    the caller is expected to provide thread-safety through a higher-level
    locking primitive managed by the caller.

    See Also
    ----------
    https://stackoverflow.com/a/43573798/2809027
        StackOverflow answer strongly inspiring the low-level implementation of
        this function with respect to inscrutable :mod:`importlib` machinery.
    '''

    # Global variables reassigned below.
    global _beartype_pathhook

    # If this function has already been called under the active Python
    # interpreter, silently reduce to a noop.
    if _beartype_pathhook is not None:
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
    # "Tuple[Type[Loader], List[str]]"). This is why we can't have nice things.
    loader_factory = FileFinder.path_hook(LOADER_DETAILS)  # type: ignore[arg-type]

    # Prepend a new path hook (i.e., factory closure encapsulating this loader)
    # *BEFORE* all other path hooks.
    path_hooks.insert(0, loader_factory)

    # Prevent subsequent calls to this function from erroneously re-adding
    # duplicate copies of this path hook immediately *AFTER* successfully adding
    # the first such path hook.
    #
    # Note that we intentionally avoid globalizing this path hook until *AFTER*
    # successfully having done so. Why? Negligible safety. The companion
    # remove_beartype_pathhook() function raises a non-human-readable exception
    # if this global is non-"None" but *NOT* in the "path_hooks" list.
    _beartype_pathhook = loader_factory

    # Lastly, clear *ALL* import path hook caches for safety.
    _clear_importlib_caches()

# ....................{ REMOVERS                           }....................
#FIXME: Unit test us up, please.
def remove_beartype_pathhook() -> None:
    '''
    Remove our **beartype import path hook singleton** (i.e., single callable
    guaranteed to be inserted at most once to the front of the standard
    :mod:`sys.path_hooks` list recursively applying the
    :func:`beartype.beartype` decorator to all well-typed callables and classes
    defined by all submodules of all packages previously registered by a call to
    a public :func:`beartype.claw` function) if this path hook has already been
    added *or* silently reduce to a noop otherwise (i.e., if this path hook has
    yet to be added).

    Caveats
    ----------
    **This function is non-thread-safe.** For both simplicity and efficiency,
    the caller is expected to provide thread-safety through a higher-level
    locking primitive managed by the caller.
    '''

    # Global variables reassigned below.
    global _beartype_pathhook

    # If the add_beartype_pathhook() function has *NOT* yet been called under
    # the active Python interpreter, silently reduce to a noop.
    if _beartype_pathhook is None:
        return
    # Else, that function has already been called under this interpreter.

    # Remove the prior path hook added by that function *OR* raise a
    # non-human-readable "ValueError" exception if this global is non-"None" but
    # *NOT* in the "path_hooks" list (which should *NEVER* happen, but it will).
    path_hooks.remove(_beartype_pathhook)

    # Allow subsequent calls to the add_beartype_pathhook() to re-add a new
    # instance of this path hook immediately *AFTER* successfully removing the
    # first such path hook.
    _beartype_pathhook = None

    # Lastly, clear *ALL* import path hook caches for safety.
    _clear_importlib_caches()

# ....................{ PRIVATE ~ globals                  }....................
_beartype_pathhook: Optional[ImportPathHook] = None
'''
**Beartype import path hook singleton** (i.e., factory closure creating and
returning a new :class:`importlib.machinery.FileFinder` instance itself creating
and leveraging a new :class:`.BeartypeSourceFileLoader` instance) if the
:func:`.add_beartype_pathhook` function has been previously called at least once
under the active Python interpreter and the :func:`.remove_beartype_pathhook`
function has not been called more recently *or* :data:`None` otherwise.
'''

# ....................{ PRIVATE ~ cachers                  }....................
#FIXME: Unit test us up, please.
def _clear_importlib_caches() -> None:
    '''
    Clear *all* :mod:`sys`- and :mod:`importlib`-specific caches pertaining to
    **import path hooks** (i.e., the standard :mod:`sys.path_hooks` list).

    This function is typically called immediately *after* our beartype import
    path hook singleton is either added to or removed from the path hooks list.
    '''

    # Uncache *ALL* competing loaders cached by prior importations. Just do it!
    path_importer_cache.clear()

    # Clear *ALL* "importlib" caches as well for safety.
    invalidate_caches()
