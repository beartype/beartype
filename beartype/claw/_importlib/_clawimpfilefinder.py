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

# ....................{ TODO                               }....................
#FIXME: Generalize the _permute_beartype_file_finder_loader_details() function
#to additionally load Python bytecode-compiled modules (i.e., of filetype
#".pyc") with a new beartype-specific bytecode module loader that has yet to be
#defined... but could be! How? By leveraging the third-party "astor" package,
#which provides a code_to_ast() function decompiling arbitrary code objects into
#ASTs. See also this relevant StackOverflow answer by myself:
#    https://stackoverflow.com/a/76641537/2809027

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeClawImportlibException,
    BeartypeClawImportlibStandardFileFinderPathHookNotFoundWarning,
)
from beartype.claw._importlib._clawimpfileloader import BeartypeSourceFileLoader
from beartype._util.func.utilfuncscope import get_func_freevars
from beartype._util.error.utilerrwarn import issue_warning
from beartype._util.module.utilmodimport import import_module_attr_or_none
from beartype._util.utilobjget import get_object_basename_scoped
from collections.abc import Callable
from importlib.abc import Loader
from importlib.machinery import (
    BYTECODE_SUFFIXES,
    SOURCE_SUFFIXES,
    FileFinder,
    SourcelessFileLoader,
)
from sys import path_hooks
from typing import Optional

# ....................{ HINTS                              }....................
FileFinderPathHookAndIndex = tuple[Callable, int]
'''
:pep:`585`-compliant type hint matching any 2-tuple ``(path_hook,
path_hook_index)`` where:

* ``path_hook`` is a **file finder path hook** (i.e., closure created and
  returned by a call to the :meth:`importlib.machinery.FileFinder.path_hook`
  method).
* ``path_hook_index`` is the 0-based index of either:

  * If the global :obj:`sys.path_hooks` list already contains this hook, the
    index of this hook in that list.
  * Else, the index at which the caller should insert this hook into that list.
'''


FileFinderPathHookLoaderDetails = tuple[tuple[type[Loader], list[str]], ...]
'''
:pep:`585`-compliant type hint matching **import hook file finder loader
details** (i.e., tuple-centric data structure associating each Python module
filetype supported by the current platform with a corresponding import hook file
loader class whose instances are responsible for loading Python modules of that
filetype into imported in-memory module objects).
'''

# ....................{ FACTORIES                          }....................
def make_beartype_file_finder_path_hook_index() -> FileFinderPathHookAndIndex:
    '''
    2-tuple ``(path_hook, path_hook_index)`` such that ``path_hook`` is the
    **beartype-specific file finder path hook** (i.e., closure created and
    returned by calling the :meth:`importlib.machinery.FileFinder.path_hook`
    static method with beartype-specific file finder path hook loader details
    permuted from the standard "default" file finder path hook loader details)
    and ``path_hook_index`` is the 0-based index of the global
    :obj:`sys.path_hooks` list to which the caller is recommended to insert this
    path hook into.

    This factory creates and returns a new beartype-specific file finder path
    hook altered from the standard default beartype-specific file finder path
    hook such that:

    * The standard :class:`importlib.machinery.SourceFileLoader` subclass is
      replaced by our non-standard
      :class:`beartype.claw._importlib._clawimpfileloader.BeartypeSourceFileLoader`
      subclass. The latter subclasses the former to additionally transform
      relevant packages and modules with runtime type-checking.

    This factory is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator), as the value returned by this finder is
    volatile and subject to change between calls. Since third-party packages and
    modules frequently modify the global :obj:`sys.path_hooks` list searched by
    this finder, those modifications can (and, in all likelihood, will) modify
    the index of the standard file finder path hook discovered by the first call
    to this finder and that same index discovered by subsequent calls.

    Caveats
    -------
    **This factory is non-thread-safe.** For both simplicity and efficiency, the
    caller is expected to guarantee thread-safety through a higher-level locking
    primitive managed directly by that caller.

    Returns
    -------
    tuple[Callable, int]
        2-tuple ``(path_hook, path_hook_index)`` such that:

        * ``path_hook`` is a beartype-specific file finder path hook.
        * ``path_hook_index`` is the 0-based index of the global
          :obj:`sys.path_hooks` list into which the caller should insert this
          hook (e.g., by calling the :meth:`sys.path_hooks.insert` method).

    Warns
    -----
    BeartypeClawImportlibWarning
        If the global :obj:`sys.path_hooks` list no longer contains the
        standard file finder path hook *and* the active Python interpreter fails
        to define the standard private
        :func:`importlib._bootstrap_external._get_supported_file_loaders`
        getter. Ideally, this should *never* happen. Pragmatically, this *could*
        happen if either:

        * Some previously run third-party package or module maliciously removes
          this path hook from the standard :obj:`sys.path_hooks` list.
        * The active Python interpreter is *not* CPython but instead some
          unexpectedly exotic third-party Python interpreter.
    '''

    # ....................{ LOCALS                         }....................
    # 2-tuple "(standard_path_hook, path_hook_index)" if the global
    # "sys.path_hooks" list still contains the standard file finder path hook
    # *OR* "None" otherwise.
    path_hook_data = _find_standard_file_finder_path_hook_index_or_none()

    # Standard (i.e., beartype-agnostic) file finder path hook loader details
    # defined below.
    standard_loader_details: FileFinderPathHookLoaderDetails = None  # type: ignore[assignment]

    # ....................{ LOADER DETAILS                 }....................
    # If the global "sys.path_hooks" list still contains the standard file
    # finder path hook...
    if path_hook_data is not None:
        # Standard file finder path hook (i.e., closure created and returned by
        # the call to the importlib.machinery.FileFinder.path_hook() method in
        # the standard "importlib._bootstrap_external" module on Python
        # startup) and the 0-based index of that hook in the global
        # "sys.path_hooks" list.
        standard_path_hook, path_hook_index = path_hook_data

        # Standard file finder path hook loader details defined by "importlib".
        standard_loader_details = (
            _get_file_finder_path_hook_loader_details(standard_path_hook))
    # Else, the global "sys.path_hooks" list no longer contains the standard
    # file finder path hook. In this case...
    else:
        # Instruct the caller to insert the beartype-specific file finder path
        # hook created and returned below *AFTER* all other path hooks currently
        # residing on the global "sys.path_hooks" list for safety.
        #
        # Note that the list.insert() method explicitly supports attempts to
        # "insert" a new item into a non-existent index following the last
        # existing index of the current list by merely appending that item to
        # that list: e.g.,
        #     >>> muh_list = []
        #     >>> muh_list.insert(len(muh_list), 'y u so lazy, muh list!?')
        #     >>> muh_list
        #     ['y u so lazy, muh list!?']  # <-- noice
        path_hook_index = len(path_hooks)

        # Standard private _get_supported_file_loaders() getter defined by the
        # standard private "importlib._bootstrap_external" submodule.
        #
        # Note that *ALL* actively maintained CPython interpreters define this
        # getter. Of course, there are no guarantees that either future CPython
        # interpreters *OR* third-party Python interpreters will do so.
        _get_supported_file_loaders = import_module_attr_or_none(
            module_name='importlib._bootstrap_external',
            attr_name='_get_supported_file_loaders',
        )

        # If this getter exists, define the standard file finder path hook
        # loader details as the tuple created and returned by this getter.
        if _get_supported_file_loaders:
            standard_loader_details = _get_supported_file_loaders()
        # Else, this getter does *NOT* exist. In this case...
        else:  # pragma: no cover
            # print('Here!')

            # Fallback to a crude hard-coded facsimile of the standard file
            # finder path hook loader details. This fallback is a proper subset
            # of the actual loader details and thus suitable *ONLY* as a
            # fallback in the event of calamity, which this (sadly) is.
            #
            # Note that:
            # * This edge case is extremely uncommon and thus *NOT* worth
            #   optimizing for. Since this edge case assumes that the active
            #   Python interpreter is *NOT* CPython, even replicating this edge
            #   case in unit tests is (basically) infeasible.
            # * We avoid even attempting to map a beartype-agnostic extension
            #   module loader. Doing so would require importing the private
            #   _imp.extension_suffixes() function. Since this non-standard
            #   Python interpreter fails to define the equally private
            #   _get_supported_file_loaders() function, it almost certainly also
            #   fails to define _imp.extension_suffixes(). It is what it is.
            standard_loader_details = (
                # Beartype-specific source module loader (i.e., file loader
                # loading uncompiled pure-Python modules of the filetype ".py").
                (BeartypeSourceFileLoader, SOURCE_SUFFIXES),

                # Beartype-agnostic bytecode module loader (i.e., file loader
                # loading precompiled pure-Python modules from bytecode files
                # compiled in "__pycache__/" subdirectories that lack uncompiled
                # pure-Python modules of the filetype ".py").
                (SourcelessFileLoader, BYTECODE_SUFFIXES),
            )

            # Issue a warning to notify the caller of this calamity! *OHNOES*.
            issue_warning(
                warning_cls=(
                    BeartypeClawImportlibStandardFileFinderPathHookNotFoundWarning),
                message=(
                    'Standard import file finder path hook not found '
                    '(i.e., importlib.machinery.FileFinder.path_hook() closure '
                    'not found in standard "sys.path_hooks" list) *AND* '
                    'standard private '
                    'importlib._bootstrap_external._get_supported_file_loaders() '
                    'getter undefined. '
                    'This rare edge case occurs when both:\n'
                    '* Some third-party package or module '
                    'maliciously removed that closure from that list.\n'
                    '* The active Python interpreter is an '
                    'unexpectedly exotic third-party interpreter '
                    '(rather than CPython).\n'
                    'The Bear feels sadness yet also deep suspicion that you '
                    'are wading in dark waters, where even Bear dare not swim.'
                )
            )

    # ....................{ PATH HOOK                      }....................
    # Beartype-specific file finder path hook loader details permuting these
    # details so as to runtime type-check on-disk Python modules (by loading
    # these modules with our beartype-specific file loader rather than the
    # beartype-agnostic file loader defined by "importlib" machinery).
    beartype_loader_details = _permute_beartype_file_finder_loader_details(
        standard_loader_details)

    # Beartype-specific file finder path hook instantiated with these details.
    beartype_path_hook = FileFinder.path_hook(*beartype_loader_details)

    # Monkey-patch an arbitrary beartype-specific instance variable into this
    # closure. Doing so significantly aids debugging by enabling logging and
    # print() statements to distinguish between our closure and Python's
    # equivalent default closure.
    beartype_path_hook.__beartype_is_path_hook__ = True  # type: ignore[attr-defined]

    # ....................{ RETURN                         }....................
    # Return this beartype-specific file finder path hook and the 0-based index
    # of the "sys.path_hooks" list at which the caller should insert this hook.
    return beartype_path_hook, path_hook_index

# ....................{ PRIVATE ~ getters                  }....................
#FIXME: Unit test us up, please. *sigh*
def _get_file_finder_path_hook_loader_details(
    path_hook: Callable) -> FileFinderPathHookLoaderDetails:
    '''
    **Import hook file finder loader details** (i.e., tuple-centric data
    structure associating each Python module filetype supported by the current
    platform with a corresponding import hook file loader class whose instances
    are responsible for loading Python modules of that filetype into imported
    in-memory module objects) of the passed **file finder path hook** (i.e.,
    closure created and returned by a prior call to the
    :meth:`importlib.machinery.FileFinder.path_hook` method).

    This getter is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator), as *all* higher-level callables currently
    calling this lower-level callable are already memoized.

    Design
    ------
    This getter currently unconditionally returns the same tuple as created and
    returned by the standard private
    :func:`importlib._bootstrap_external._get_supported_file_loaders` getter
    under all actively maintained Python releases. Technically, this implies
    that this getter could simply be reduced to either trivially returning the
    tuple returned by that getter *or* replaced altogether by that getter.
    Pragmatically, doing so would render this fragile submodule even more
    fragile against upstream changes in Python's standard library.

    Parameters
    ----------
    path_hook : Callable
        File finder path hook to inspect.

    Returns
    -------
    FileFinderPathHookLoaderDetails
        Loader details with which this path hook was originally instantiated.
    '''

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
        raise BeartypeClawImportlibException(  # pragma: no cover
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

# ....................{ PRIVATE ~ getters : standard       }....................
#FIXME: Unit test us up, please. *sigh*
def _get_standard_file_finder_path_hook_basename_scoped() -> str:
    '''
    **Lexically scoped basename** (i.e., ``.``-delimited string unambiguously
    identifying all lexical scopes encapsulating) of the **standard file finder
    path hook** (i.e., closure created and returned by the call to the
    :meth:`importlib.machinery.FileFinder.path_hook` method in the standard
    :mod:`importlib._bootstrap_external` module on Python startup), equivalent
    to the value of the ``__qualname__`` dunder attribute defined on that hook.

    This getter is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator). This getter *should* only be called once
    per active Python process and (in any case) is trivial to recompute.

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

# ....................{ PRIVATE ~ finders                  }....................
#FIXME: Unit test us up, please. *sigh*
def _find_standard_file_finder_path_hook_index_or_none() -> (
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

    # Lexically scoped basename** (i.e., "."-delimited string unambiguously
    # identifying all lexical scopes encapsulating) the standard file finder
    # path hook.
    path_hook_basename = _get_standard_file_finder_path_hook_basename_scoped()

    # For the 0-based index of each import path hook previously registered with
    # the standard "path_hooks" list *AND* that hook...
    for path_hook_index, path_hook in enumerate(path_hooks):
        # Lexically scope basename of the currently visited path hook.
        path_hook_name = get_object_basename_scoped(path_hook)

        # If this basename is that of the standard file finder path hook,
        # short-circuit by returning both this hook and the index of this hook.
        if path_hook_name == path_hook_basename:
            return path_hook, path_hook_index
        # Else, this basename is *NOT* that of the standard file finder path
        # hook. In this case, silently continue to the next path hook.
    # Else, the standard file finder path hook no longer exists.

    # Return "None" as a last-ditch fallback. Truly, we have given up.
    return None

# ....................{ PRIVATE ~ permuters                }....................
#FIXME: Unit test us up, please. *sigh*
def _permute_beartype_file_finder_loader_details(
    loader_details: FileFinderPathHookLoaderDetails) -> (
    FileFinderPathHookLoaderDetails):
    '''
    Permute (i.e., create, modify, and return a new shallow copy of) the passed
    **import hook file finder loader details** (i.e., tuple-centric data
    structure associating each Python module filetype supported by the current
    platform with a corresponding import hook file loader class whose instances
    are responsible for loading Python modules of that filetype into imported
    in-memory module objects) presumably introspected from the **standard file
    finder path hook** (i.e., closure created and returned by the call to the
    :meth:`importlib.machinery.FileFinder.path_hook` method in the standard
    :mod:`importlib._bootstrap_external` module on Python startup).

    This permuter modifies the standard file finder path hook loader details as
    follows:

    * The standard :class:`importlib.machinery.SourceFileLoader` subclass is
      replaced by our non-standard
      :class:`beartype.claw._importlib._clawimpfileloader.BeartypeSourceFileLoader`
      subclass. The latter subclasses the former to additionally transform
      relevant packages and modules with runtime type-checking.

    Parameters
    ----------
    loader_details : FileFinderPathHookLoaderDetails
        Beartype-agnostic file finder path hook loader details.

    Returns
    -------
    FileFinderPathHookLoaderDetails
        Beartype-specific file finder path hook loader details.
    '''
    assert isinstance(loader_details, tuple), (
        f'{repr(loader_details)} not tuple.')
    assert loader_details, 'Loader details empty.'

    # List of all 2-tuples "(loader_type_new, loader_filetypes)" comprising the
    # beartype-specific loader details to be returned as a tuple below.
    loader_details_new = []

    # For each such 2-tuple "(loader_type_old, loader_filetypes)"...
    for loader_details_item in loader_details:
        # Tuple of all filetypes associated with the currently visited loader.
        loader_filetypes = loader_details_item[1]

        # If these filetypes are those identifying on-disk Python modules (e.g.,
        # typically but *NOT* necessarily files of filetype ".py")...
        if loader_filetypes == SOURCE_SUFFIXES:
            # Replace the default "importlib.machinery.SourceFileLoader" type
            # loading on-disk Python modules with this beartype-specific type
            # subclassing that default type.
            loader_details_item = (BeartypeSourceFileLoader, loader_filetypes)
        # Else, these filetypes are *NOT* those identifying on-disk Python
        # modules. In this case, preserve this 2-tuple as is.

        # Append this possibly modified 2-tuple to this list to be returned.
        loader_details_new.append(loader_details_item)

    # Return this list, coerced into a tuple to comply with API expectations.
    return tuple(loader_details_new)
