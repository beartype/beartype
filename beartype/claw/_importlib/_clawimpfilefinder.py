#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **import hook file finders** (i.e., factory functions creating and
returning :mod:`importlib.machinery`-compliant objects suitable for
instantiating new items of the standard :obj:`sys.path_hooks` list with).

This private submodule is *not* intended for importation by downstream callers.
'''

#FIXME: Our hardcoded definition of "_LOADERS_DETAILS" below is *SUPER*
#non-ideal. In 2026, we should *ABSOLUTELY* instead be dynamically deferring to
#the technically private (but who cares)
#importlib._bootstrap_external._get_supported_file_loaders() getter. Of course,
#actually directly calling that getter *ANYWHERE* in @beartype would be even
#more *SUPER* non-ideal. Instead:
#* Rename the existing "_clawimpload" submodule to "_clawimpfileloader".
#* Define a new "_clawimpfilefinder" submodule in this same subpackage.
#* In this new submodule:
#  * Define a new get_file_finder_loader_details() getter with signature:
#        from collections.abc import Sequence
#
#        _FileFinderLoaderDetails = tuple[tuple[str, Sequence[str]], ...]
#
#        @callable_cached
#        def make_file_finder_loader_details() -> _FileFinderLoaderDetails:
#            ...
#  * Implement this getter as follows:
#    * Actually, just see "mopy.py". I've specced out a working
#      implementation there. Works fine under both Python 3.10 and 3.15! \o/
#    * Note that even that isn't *QUITE* enough. Inside this getter, we lastly
#      need to do this. This logic kinda looks like it should reside in a new
#      private _permute_file_finder_loader_details() function internally called
#      by this make_file_finder_loader_details() function. The signature should
#      probably resemble:
#          def _permute_file_finder_loader_details(
#              loader_details: _FileFinderLoaderDetails) -> _FileFinderLoaderDetails:
#              ...
#
#      Implement _permute_file_finder_loader_details() as follows, please:
#      * Define a new list "loader_details_new_list = []" to be returned.
#      * Iterate over the items of the found "loader_details" tuple.
#      * For each such item, which is a 2-tuple
#        "(loader_type, loader_filetypes)":
#        * If the current "loader_filetypes == SOURCE_SUFFIXES", then:
#          * Replace "loader_type = BeartypeSourceFileLoader" in this 2-tuple.
#        * Else, preserve this 2-tuple as is.
#        * In either case, append this 2-tuple to "loader_details_new_list".
#      * Return "tuple(loader_details_new_list)". W00t. \o/
#    * Old unfinished approach:
#      * Search "sys.path_hooks" for the standard "FileFinder". We should
#        probably just hardcode:
#        * Its wierdo "__qualname__" as a new magic string constant in the
#          "dataclawmagic" submodule.
#        * Find the first "sys.path_hooks" item whose "__qualname__" is equal
#          to that magic string.
#      * If we fail to find the standard "FileFinder", raise an exception.
#        This is bad news. So, it's best to just hard-fail there.
#      * Else, we found the standard "FileFinder". Great!
#  * *DEFINITELY UNIT TEST UP THAT GETTER*. Should be trivial. The unit test
#    should just:
#    * Call that getter.
#    * Iterate over the returned object and validate that it's a tuple data
#      structure whose contents match the "_FileFinderLoaderDetails" hint
#      defined above. *shrug*
#  * Define a new make_file_finder_path_hook() factory with signature:
#        from importlib.machinery import (
#            # BYTECODE_SUFFIXES,
#            # SOURCE_SUFFIXES,
#            FileFinder,
#            # ExtensionFileLoader,
#            # SourcelessFileLoader,
#        )
#
#        def make_file_finder_path_hook() -> FileFinder:
#            file_finder_loader_details = get_file_finder_loader_details()
#            file_finder = FileFinder.path_hook(file_finder_loader_details)
#            return file_finder
#* Refactor this function to import and call the make_file_finder() factory
#  defined above. *more shrugging*

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeClawImportlibException
from beartype._data.claw.dataclawmagic import (
    STANDARD_FILE_FINDER_PATH_HOOK_NAME)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.func.utilfuncscope import get_func_freevars
from beartype._util.utilobjget import get_object_name
from collections.abc import (
    Callable,
    Sequence,
)
from importlib.machinery import (
   SOURCE_SUFFIXES,
   FileFinder,
)
from sys import path_hooks

# ....................{ HINTS                              }....................
FileFinderPathHookLoaderDetails = tuple[tuple[str, Sequence[str]], ...]
'''
:pep:`585`-compliant type hint matching **import hook file finder loader
details** (i.e., tuple-centric data structure associating each Python module
filetype supported by the current platform with a corresponding import hook file
loader class whose instances are responsible for loading Python modules of that
filetype into imported in-memory module objects).
'''

# ....................{ FACTORIES                          }....................
#FIXME: Uncomment once worky, yo. *sigh*
# @callable_cached
# def make_beartype_file_finder_path_hook_loader_details() -> (
#     FileFinderPathHookLoaderDetails):
#     '''
#     **Beartype import hook file finder loader details** (i.e., tuple-centric
#     data structure associating each Python module filetype supported by the
#     current platform with a corresponding import hook file loader class whose
#     instances are responsible for loading Python modules of that filetype into
#     imported in-memory module objects).
#
#     This factory creates and returns a new tuple-centric data structure
#     identical to the **default import hook file finder loader details** (i.e.,
#     tuple instantiating the default import hook file finder path hook by being
#     passed to the :meth:`importlib.machinery.FileFinder.path_hook` method in the
#     standard :mod:`importlib._bootstrap_external` module on Python startup) with
#     one critical exception:
#
#     * The standard :class:`importlib.machinery.SourceFileLoader` subclass is
#       replaced by our non-standard
#       :class:`beartype.claw._importlib._clawimpfileloader.BeartypeSourceFileLoader`
#       subclass. The latter subclasses the former to additionally transform
#       relevant packages and modules with runtime type-checking.
#
#     This factory is memoized for efficiency.
#     '''
#
#     pass

# ....................{ PRIVATE ~ getters                  }....................
#FIXME: Unit test us up, please!
#FIXME: Docstring us up, please!
#FIXME: Call us up elsewhere, please!
def _get_standard_file_finder_path_hook_loader_details() -> (
    FileFinderPathHookLoaderDetails):
    '''
    '''

    # Standard file finder path hook (i.e., closure created and returned by the
    # call to the importlib.machinery.FileFinder.path_hook() method in the
    # standard "importlib._bootstrap_external" module on Python startup).
    path_hook = _find_standard_file_finder_path_hook()

    # Closure scope (i.e., dictionary mapping from the name to value of each
    # closure-scoped local attribute defined in the body of the parent callable
    # also defining and returning the passed closure) for this closure.
    path_hook_freevars = get_func_freevars(path_hook)
    # print(f'path_hook_file_finder_freevars: {path_hook_file_finder_freevars}')

    # Value of the "*loader_details" variadic positional parameter accepted by
    # that prior call to the importlib.machinery.FileFinder.path_hook() method
    # that created and returned this closure if any *OR* "None" otherwise (e.g.,
    # if that method has since been refactored by a future CPython release to no
    # longer accept a variadic positional parameter with this name).
    path_hook_loader_details = path_hook_freevars.get('loader_details', None)

    # If the importlib.machinery.FileFinder.path_hook() method has since been
    # refactored by a future CPython release to no longer accept a
    # "*loader_details" variadic positional parameter, raise an exception.
    if path_hook_loader_details is None:
        raise BeartypeClawImportlibException(
            'Standard file finder path hook loader details not found '
            '(i.e., importlib.machinery.FileFinder.path_hook() closure '
            'in standard "sys.path_hooks" list not passed '
            '"*loader_details" variadic positional parameter, presumably '
            'due to standard "importlib._bootstrap_external" submodule '
            "refactoring that method out from under @beartype's delicate paws)."
        )
    # Else, that method still conforms to API expectations.

    # Return the value of that "*loader_details" variadic positional parameter.
    return path_hook_loader_details

# ....................{ PRIVATE ~ finders                  }....................
#FIXME: Unit test us up, please!
def _find_standard_file_finder_path_hook() -> Callable:
    '''
    **Standard file finder path hook** (i.e., closure created and returned by
    the call to the :meth:`importlib.machinery.FileFinder.path_hook` method in
    the standard :mod:`importlib._bootstrap_external` module on Python startup).

    This finder is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator), as *all* higher-level callables currently
    calling this lower-level callable are already memoized.

    Raises
    ------
    BeartypeClawImportlibException
        If finder fails to find the **standard file finder path hook.** Ideally,
        this should *never* happen. Pragmatically, this *could* happen if some
        previously run third-party package or module maliciously removes this
        path hook from the standard :obj:`sys.path_hooks` list.
    '''

    # For each previously registered path hook...
    for path_hook in path_hooks:
        # Fully-qualified name of the currently visited path hook.
        path_hook_name = get_object_name(path_hook)

        # If this name is that of the standard file finder path hook,
        # immediately return this path hook.
        if path_hook_name == STANDARD_FILE_FINDER_PATH_HOOK_NAME:
            return path_hook
        # Else, this name is *NOT* that of the standard file finder path hook.
        # In this case, silently continue to the next path hook.
    # Else, the standard file finder path hook no longer exists.

    # Raise an exception to notify the caller of this execrable calamity! OHNO.
    raise BeartypeClawImportlibException(
        'Standard file finder path hook not found '
        '(i.e., importlib.machinery.FileFinder.path_hook() closure not found '
        'in standard "sys.path_hooks" list, presumably due to some '
        'third-party package or module '
        'maliciously removing this closure from this list).'
    )
