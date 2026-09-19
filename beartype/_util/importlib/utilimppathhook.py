#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **import path hook utilities** (i.e., low-level callables
introspecting the standard :pep:`302`-compliant :mod:`sys.path_hooks` list).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
# Intentionally import the root "sys" module rather than attributes of that
# module (e.g., "meta_path", "path_hooks") to account for malicious third-party
# packages that reassign those attributes rather than modifying their contents.
import sys

from beartype._data.typing.datatyping import (
    FileFinderPathHook,
    FileFinderPathHookAndIndex,
)
from beartype._util.cache.func.utilcachefunc import callable_cached
from beartype._util.utilobjget import (
    get_object_basename_scoped,
    get_object_type_name,
)
from importlib.machinery import FileFinder
from typing import Optional

# ....................{ FINDERS                            }....................
#FIXME: Unit test us up, please. *sigh*
def find_standard_file_finder_path_hook_index_or_none() -> (
    Optional[FileFinderPathHookAndIndex]):
    '''
    2-tuple ``(path_hook, path_hook_index)`` such that ``path_hook`` is the
    **standard file finder path hook** (i.e., closure created and returned by
    the call to the :meth:`importlib.machinery.FileFinder.path_hook` method in
    the standard :mod:`importlib._bootstrap_external` module on Python startup)
    and ``path_hook_index`` is the current 0-based index of this hook in the
    global :obj:`sys.path_hooks` list containing this hook if that list contains
    this hook *or* :data:`None` otherwise (i.e., if that list no longer contains
    this path hook).

    This finder is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator), as the value returned by this finder is
    volatile and subject to change between calls. Since third-party packages and
    modules frequently modify the global :obj:`sys.path_hooks` list searched by
    this finder, those modifications can (and, in all likelihood, will) modify
    the index of the standard file finder path hook discovered by the first call
    to this finder and that same index discovered by subsequent calls.

    Caveats
    -------
    **This function is non-thread-safe.** For both simplicity and efficiency,
    the caller is expected to guarantee thread-safety through a higher-level
    locking primitive managed directly by that caller.

    Returns
    -------
    Optional[tuple[Callable, int]]
        Either:

        * If the global :obj:`sys.path_hooks` list still contains the standard
          file finder path hook, then the 2-tuple ``(path_hook,
          path_hook_index)`` where:

          * ``path_hook`` is the standard file finder path hook.
          * ``path_hook_index`` is the current 0-based index of this hook in the
            global :obj:`sys.path_hooks` list containing this hook.

        * Else, that list no longer contains that path hook, in which case this
          finder returns :data:`None`. Ideally, this should *never* happen.
          Pragmatically, this *could* happen if either:

          * Some previously run third-party package or module maliciously
            removed that path hook from that list.
          * The active Python interpreter is *not* CPython but instead some
            unexpectedly exotic third-party Python interpreter.

    Warns
    -----
    BeartypeClawImportlibWarning
        If the global :obj:`sys.path_hooks` list no longer contains the
        **standard file finder path hook.** Ideally, this should *never* happen.
        Pragmatically, this *could* happen if either:

        * Some previously run third-party package or module maliciously removes
          this path hook from the standard :obj:`sys.path_hooks` list.
        * The active Python interpreter is *not* CPython but instead some
          unexpectedly exotic third-party Python interpreter.
    '''
    # print('[_find_standard_file_finder_path_hook_index_or_none]: Begin')

    # For the 0-based index of each import path hook previously registered with
    # the standard "path_hooks" list *AND* that hook...
    for path_hook_index, path_hook in enumerate(sys.path_hooks):
        # print(f'sys.path_hooks[{path_hook_index}] == {repr(path_hook)}')

        # Standard file finder path hook if this path hook either is or is a
        # high-level wrapper encapsulating the standard file finder path hook
        # *OR* "None" otherwise (i.e., if this path hook neither is nor is a
        # high-level wrapper encapsulating the standard file finder path hook).
        standard_file_finder_path_hook = (
            _get_path_hook_if_standard_file_finder_path_hook_or_none(path_hook))

        # If this is the standard file finder path hook, short-circuit by
        # returning both this hook and the index of this hook.
        if standard_file_finder_path_hook:
            return standard_file_finder_path_hook, path_hook_index
        # Else, this is *NOT* the standard file finder path hook. In this case,
        # silently continue to the next path hook.
    # Else, the standard file finder path hook no longer exists.

    # Return "None" as a last-ditch fallback. Truly, we have given up.
    return None

# ....................{ PRIVATE ~ getters                  }....................
#FIXME: Unit test us up, please. *sigh*
@callable_cached
def _get_path_hook_if_standard_file_finder_path_hook_or_none(
    path_hook: FileFinderPathHook) -> Optional[FileFinderPathHook]:
    '''
    Passed **path hook** (i.e., first- or third-party callable on the
    :pep:`302`-compliant :obj:`sys.path_hooks` list) if this hook either is or
    is a high-level wrapper object encapsulating the **standard file finder path
    hook** (i.e., closure created and returned by the call to the
    :meth:`importlib.machinery.FileFinder.path_hook` method in the standard
    :mod:`importlib._bootstrap_external` module on Python startup) *or*
    :data:`None` otherwise (i.e., if the passed path hook neither is *nor* is a
    high-level wrapper object encapsulating the standard file finder path hook).

    This tester is memoized for efficiency.

    Parameters
    ----------
    path_hook : FileFinderPathHook
        Path hook to be tested.

    Returns
    -------
    Optional[FileFinderPathHook]
        Either:

        * If this hook either is or is a high-level wrapper object encapsulating
          the standard file finder path hook, this hook.
        * Else, :data:`None`.
    '''
    assert callable(path_hook), (
        f'"sys.path_hooks" entry {repr(path_hook)} uncallable.')

    # ....................{ API ~ crosshair                }....................
    # Fully-qualified name of the type of this path hook.
    path_hook_type_name = get_object_type_name(path_hook)

    #FIXME: Shift into a new "beartype._util.api.external.utilcrosshair"
    #submodule, please. This is pure balls! Like usual around here. *sigh*
    # If this path hook is actually a non-standard third-party wrapper
    # encapsulating a standard path hook injected into the PEP 302-compliant
    # "sys.path_hooks" list by the CrossHair-specific
    # crosshair.pure_importer.prefer_pure_python_imports() context manager,
    # locally replace the former with the latter for the purposes of sane
    # detection below.  # <-- *lolbro* this is such trash
    if path_hook_type_name == 'crosshair.pure_importer.PreferPureLoaderHook':
        path_hook = path_hook.orig_hook  # type: ignore[attr-defined]
    # Else, this path hook is *NOT* such a non-standard third-party wrapper.
    # Ergo, this path hook is presumably standard.
    #
    # In either case, this path hook *SHOULD* now be standard.

    # ....................{ RETURN                         }....................
    # Lexically scope basename of this path hook.
    path_hook_basename = get_object_basename_scoped(path_hook)

    # Lexically scoped basename of the standard file finder path hook.
    STANDARD_FILE_FINDER_PATH_HOOK_BASENAME = (
        _get_standard_file_finder_path_hook_basename_scoped())

    # Return either...
    return (
        # If the basename of this path hook is that of the standard file finder
        # path hook, this path hook;
        path_hook
        if path_hook_basename == STANDARD_FILE_FINDER_PATH_HOOK_BASENAME else
        # Else, "None".
        None
    )


@callable_cached
def _get_standard_file_finder_path_hook_basename_scoped() -> str:
    '''
    **Lexically scoped basename** (i.e., ``.``-delimited unambiguously
    identifying string of all lexical scopes) of the **standard file finder path
    hook** (i.e., closure created and returned by the call to the
    :meth:`importlib.machinery.FileFinder.path_hook` method in the standard
    :mod:`importlib._bootstrap_external` module on Python startup), equivalent
    to the value of the ``__qualname__`` dunder attribute defined on that hook.

    This getter is memoized for efficiency.

    Design
    ------
    This getter currently unconditionally returns the magic string constant
    ``"FileFinder.path_hook.path_hook_for_FileFinder"`` under all actively
    maintained Python releases. Technically, this implies that this getter could
    simply be reduced to either trivially returning that constant *or* replaced
    altogether by that constant. Pragmatically, doing so would render this
    fragile submodule even more fragile against upstream changes outside our
    control in Python's standard library.

    This name is intentionally defined as the lexically scoped basename (as
    introspected by the :func:`.get_object_basename_scoped` getter called below)
    rather than as the fully-qualified name (as introspected by the
    :func:`beartype._util.utilobjget.get_object_name` getter *not* called
    below). In theory, the latter would be more precisely unambiguous and thus
    preferable. In practice, the latter is unreliable and thus unusable. Why?
    Because the standard :mod:`importlib` package modifies the fully-qualified
    name of the standard file finder path hook it instantiates to pretend to be
    defined by a different module (e.g., :mod:`_frozen_importlib_external`) than
    the module actually defining that hook (e.g.,
    :mod:`importlib._bootstrap_external`). Why? No idea, honestly. It doesn't
    particularly matter, either. It's well beyond our control. All that's in our
    control (and thus all that matters) is the observation that the module name
    and thus the lexically scoped basename of the standard file finder path hook
    can be unambiguously introspected by third-party packages. Consider:

    .. code-block:: python

       >>> from beartype._util.utilobjget import get_object_name
       >>> from importlib.machinery import FileFinder

       # Fully-qualified name of a standard file finder path hook manually
       # instantiated outside the standard "importlib" machinery! This is awful.
       >>> get_object_name(FileFinder.path_hook())
       'importlib._bootstrap_external.FileFinder.path_hook.path_hook_for_FileFinder'

       # Fully-qualified name of a standard file finder path hook automatically
       # instantiated inside the standard "importlib" machinery. *UGH UGH UGH*.
       >>> file_finder_path_hook = _find_standard_file_finder_path_hook()
       >>> get_object_name(file_finder_path_hook)
       '_frozen_importlib_external.FileFinder.path_hook.path_hook_for_FileFinder'
    '''

    # Standard file finder path hook manually instantiated outside the standard
    # "importlib" machinery. Why? Chicken-and-egg issues. Merely finding the
    # standard file finder path hook manually instantiated automatically
    # instantiated inside the standard "importlib" machinery requires magically
    # knowing the magic string constant introspected by this getter. We have no
    # recourse but to create (and then immediately discard) an empty file finder
    # path hook merely to introspect its lexically scoped basename.
    path_hook = FileFinder.path_hook()

    # Lexically scoped basename of this path hook.
    path_hook_name = get_object_basename_scoped(path_hook)

    # Return this lexically scoped basename.
    return path_hook_name
