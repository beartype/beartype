#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **import hook path hook registrars** (i.e., high-level functions both
adding and removing our beartype import path hook singleton to and from the
front of the standard :mod:`sys.path_hooks` list, which when added recursively
applies the :func:`beartype.beartype` decorator to all well-typed callables and
classes defined by all submodules of all packages previously registered by a
call to a public :func:`beartype.claw` import hook).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.claw._importlib._clawimpload import BeartypeSourceFileLoader
from importlib import invalidate_caches
from importlib.machinery import (
    BYTECODE_SUFFIXES,
    SOURCE_SUFFIXES,
    FileFinder,
    ExtensionFileLoader,
    SourcelessFileLoader,
)
from sys import (
    path_hooks,
    path_importer_cache,
)

# Intentionally violate privacy encapsulate in the standard Python library,
# because there is *NO* valid alternative. This low-level private getter
# function returns a tuple of the filetypes of *ALL* C extensions supported by
# the current platform (e.g., as shared libraries).
from _imp import extension_suffixes

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
    -------
    **This function is non-thread-safe.** For both simplicity and efficiency,
    the caller is expected to guarantee thread-safety through a higher-level
    locking primitive managed directly by that caller.

    See Also
    --------
    :class:`beartype.claw._importlib._clawimpload.BeartypeSourceFileLoader`
        Class docstring detailing the motivation for this function exclusively
        leveraging the lower-level :attr:`sys.path_hooks` mechanism for
        declaring import hooks rather than both that *and* the higher-level
        :attr:`sys.meta_path` mechanism. If confused, read that first. Yeah!
    https://stackoverflow.com/a/43573798/2809027
        StackOverflow answer strongly inspiring the low-level implementation of
        this function with respect to inscrutable :mod:`importlib` machinery.
    '''

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype.claw._clawstate import claw_state

    # ....................{ PREAMBLE                       }....................
    #FIXME: Attempt to import "_clawimpsmoke" in exactly two places below,
    #please! To do so, let's:
    #* Define a new private _warn_if_beartype_pathhook_inactive() warner below.
    #  Note that that function intentionally issues non-fatal warnings rather
    #  than raising fatal exceptions. Why? Because "beartype.claw" import hooks
    #  are *NOT* the most import hooks in the Python ecosystem. They're nice, to
    #  be sure. Runtime type-checking is valuable -- but it's not
    #  *MISSION-CRITICAL* per say. If it doesn't work, that's a shame -- but
    #  it's hardly worth destroying the world over. Consider the following
    #  comment (harvested from below):
    #     "Consider PyInstaller, for example. PyInstaller-bundled executable
    #     binary files necessarily prepend the PyInstaller-specific
    #     "PyiFrozenFinder" finder to the front of this list as well.
    #     PyInstaller-bundled executables bundling one or more third-party
    #     modules registering one or more "beartype.claw" import hooks then
    #     transitively call this function. Doing so (accidentally) overrode the
    #     PyInstaller-specific bundled module importation performed by that
    #     "PyiFrozenFinder" finder, catastrophically preventing all modules
    #     bundled with those executables from being subsequently imported!"
    #
    #  This warner should resemble:
    #      def _warn_if_beartype_pathhook_inactive() -> None:
    #          try:
    #              from beartype.claw._importlib import _clawimpsmoke
    #          except _BeartypeClawImportHookActive:
    #              return
    #
    #          #FIXME: Dynamically improve this message as follows:
    #          #* Iteratively construct an ordered list of the names all
    #          #  third-party "sys.meta_path" hooks that are currently active.
    #          #  Standard "sys.meta_path" hooks should be ignored, of course.
    #          #* Iteratively construct a *SEPARATE* list of the names all
    #          #  third-party "sys.path_hooks" that are currently active
    #          #  *AND* precede our beartype-specific "sys.path_hooks" hook.
    #          #  Standard "sys.path_hooks" should be ignored, of course.
    #          #* Define a new join_bulleted() string-joining function in the
    #          #  existing "beartype._util.text.utiltextjoin" submodule. This
    #          #  function should precede each of the passed strings by the
    #          #  prefix "\n* ", probably by trivially deferring to the existing
    #          #  join_delimited() joiner. *shrug*
    #          #* For each of these lists that is non-empty, coerce these
    #          #  non-empty lists into a string by deferring to that new
    #          #  join_bulleted() joiner.
    #          #* Define the "meta_path_items_nonstandard" and
    #          #  "path_hooks_items_nonstandard" local variables interpolated
    #          #  into the message below accordingly, please. What a huge job!
    #          warning_message = (
    #              f'"beartype.claw"-based runtime type-checking inactive. '
    #              f'Competing third-party packages or modules already '
    #              f'registered their own import hooks incompatibly overriding '
    #              f'"beartype.claw"-based import hooks responsible for '
    #              f'performing runtime type-checking. '
    #              f'Competing high-level "sys.meta_path" hooks include:\n'
    #              f'{meta_path_items_nonstandard}\n'
    #              f'Competing low-level "sys.path_hooks" hooks include:\n'
    #              f'{path_hooks_items_nonstandard}\n'
    #              f'Python currently lacks standards governing import hook '
    #              f'interoperability, thus fostering this ugly breed of '
    #              f'last-come-first-served dining philosophers feeding frenzy '
    #              f'between competing third-party import hooks. '
    #              f'In short, Python's standard "importlib" machinery sucks. '
    #              f'You now have three sucky options at your disposal. '
    #              f'Either:\n'
    #              f'* (Recommended) Contact the authors of the competing
    #              f'third-party packages or modules listed above. '
    #              f'Kindly request they improve the compatibility of '
    #              f'their import hooks with other import hooks registered by '
    #              f'other packages and modules -- especially '
    #              f'those registered by the "beartype.claw" subpackage. '
    #              f'Please ping @leycec '
    #              f'(the principal @beartype maintainer) on all relevant '
    #              f'issues so that he can nod respectfully and pretend to '
    #              f'render assistance.\n'
    #              f'* (Not recommended) Uselessly complain to us about this on '
    #              f'the @beartype issue tracker at:\n'
    #              f'\t{URL_ISSUES}\n'
    #              f'This is usually useless. '
    #              f'There is probably nothing @beartype itself can do. '
    #              f'We have no meaningful control or leverage over '
    #              f'competing third-party packages or modules. '
    #              f'We cannot force others to improve the interoperability '
    #              f'of the incompatible import hooks they themselves define. '
    #              f'We can only heckle them with animated GIFs. '
    #              f'Do this only if you want us to heckle somebody '
    #              f'with animated GIFs.\n'
    #              f'* (Desperation move) Globally silence this warning by '
    #              f'adding to your top-level "{{muh_package}}.__init__" submodule:\n'
    #              f'\tfrom beartype.roar import BeartypeClawImportHookInactiveWarning\n'
    #              f'\tfrom warnings import filterwarnings\n'
    #              f'\tfilterwarnings(action="ignore", category=BeartypeClawImportHookInactiveWarning)\n'
    #          )
    #
    #          issue_warning(
    #              warning_cls=BeartypeClawImportHookInactiveWarning,
    #              message=warning_message,
    #          )
    #* Call that warner:
    #  * First here like so:
    #        if claw_state.beartype_pathhook is not None:
    #            _warn_if_beartype_pathhook_inactive()
    #            return
    #  * Then again below like so:
    #        else:  # pragma: no cover
    #            path_hooks.append(loader_factory)
    #
    #        _warn_if_beartype_pathhook_inactive()
    #* Generalize the BeartypeSourceFileLoader.get_code() method to:
    #  * Detect whether the passed module name is
    #    "BEARTYPE_CLAW_SMOKE_TEST_SUBMODULE_NAME".
    #  * If so, raise "_BeartypeClawImportHookActive".

    # If this adder has already been called at least once by a third-party
    # reverse dependency of beartype under the active Python interpreter...
    if claw_state.beartype_pathhook is not None:
        # Silently reduce to a noop.
        return
    # Else, this adder has yet to be called.

    # ....................{ LOCALS                         }....................
    # Factory closure that, when called by standard "importlib" machinery during
    # the importation process, instantiates a new "FileFinder" instance invoking
    # our beartype-specific loader.
    #
    # Note that we intentionally ignore mypy complaints here. Why? Because mypy
    # erroneously believes this method accepts 2-tuples whose first items are
    # loader *INSTANCES* (e.g., "tuple[Loader, list[str]]"). In fact, this
    # method accepts 2-tuples whose first items are loader *TYPES* (e.g.,
    # "tuple[type[Loader], list[str]]"). This is why we can't have nice things.
    loader_factory = FileFinder.path_hook(*_LOADERS_DETAILS)  # type: ignore[arg-type]

    # Monkey-patch an arbitrary beartype-specific instance variable into this
    # closure. Doing so significantly aids debugging by enabling logging and
    # print() statements to distinguish between our closure and Python's
    # equivalent default closure.
    loader_factory.__beartype_is_path_hook__ = True  # type: ignore[attr-defined]

    # Fully-qualified (i.e., absolute) name of this closure. Under CPython, this
    # is expected to be the following magic string constant:
    #     >>> loader_factory.__qualname__
    #     'FileFinder.path_hook.<locals>.path_hook_for_FileFinder'
    loader_factory_name = loader_factory.__qualname__

    # ....................{ SEARCH                         }....................
    # Iteratively search for an index of the system-wide "path_hooks" list to
    # insert this closure at. Previously, this function unconditionally
    # prepended this closure to the front of this list. Doing so sufficed for
    # the common case but failed for popular edge cases. Consider PyInstaller,
    # for example. PyInstaller-bundled executable binary files necessarily
    # prepend the PyInstaller-specific "PyiFrozenFinder" finder to the front of
    # this list as well. PyInstaller-bundled executables bundling one or more
    # third-party modules registering one or more "beartype.claw" import hooks
    # then transitively call this function. Doing so (accidentally) overrode the
    # PyInstaller-specific bundled module importation performed by that
    # "PyiFrozenFinder" finder, catastrophically preventing all modules bundled
    # with those executables from being subsequently imported!
    #
    # This function is now *MUCH* more careful. Rather than unconditionally
    # prepending this closure to the front of this list, we now conditionally
    # search this list for an existing closure with the same name. That closure
    # *MUST* be Python's default closure instantiating a new "FileFinder"
    # instance invoking Python's default loader. Since this closure is a drop-in
    # replacement for that default closure, we insert this closure at the index
    # immediately preceding that default closure in this list with surgical
    # precision. This preserves *ALL* custom import path hooks already prefixing
    # this list, including but *NOT* limited to PyInstaller's "PyiFrozenFinder".
    #
    # This function thus safeguards compatibility with competing third-party
    # import hooks -- which, presumably, are more mission-critical than runtime
    # type-checking. Equivalently, this function shifts the burden of
    # responsibility for safeguarding compatibility from this package onto *ALL*
    # third-party packages attempting to install competing import hooks. Those
    # third-party packages are expected to preserve compatibility with runtime
    # type-checking by sequentially running the path hook we install below
    # either before or after the third-party path hooks they install.
    # Third-party packages that fail to do so are incompatible with runtime
    # type-checking and should be reported as such to their issue trackers. Yo!

    # 0-based index of the "path_hooks" list at which our beartype-specific
    # import path hook closure instantiated above is to be inserted below,
    # intentionally localized *OUTSIDE* the "for" loop performed below to
    # account for extreme edge cases in which the "path_hooks" list is empty.
    path_hook_index = 0

    # # FIXME: Uncomment as needed to debug the existing contents of the
    # # "path_hooks" list. *shrug*
    # print('[BEFORE] sys.path_hooks:\n')
    # for path_hook_index, path_hook in enumerate(path_hooks):
    #     print(f'path_hook {path_hook_index}: {repr(path_hook)}')
    #     print(f'\tqualname: {path_hook.__qualname__}')
    #     print(f'\ttype: {type(path_hook)}')
    #     print(f'\tdir: {dir(path_hook)}')

    # For the 0-based index of each previously registered import path hook *AND*
    # that hook residing in the "path_hooks" list...
    for path_hook_index, path_hook in enumerate(path_hooks):
        # If this previously registered import path hook has the same
        # fully-qualified name as our beartype-specific import path hook closure
        # instantiated above, the current hook *MUST* be Python's default
        # closure instantiating a new "FileFinder" instance invoking Python's
        # default loader. In this case...
        if path_hook.__qualname__ == loader_factory_name:
            # Insert our closure *BEFORE* Python's default closure. See above!
            path_hooks.insert(path_hook_index, loader_factory)

            # Immediately halt iteration.
            break
    # Else, Python's default closure no longer exists on the "path_hooks" list.
    # This should (probably) *NEVER* happen under CPython, but could conceivably
    # happen under more exotic alternative Python interpreters. In this case,
    # simply append our closure to this list. It is what it is. *shrug*
    else:  # pragma: no cover
        path_hooks.append(loader_factory)

    # # FIXME: Uncomment as needed to debug the existing contents of the
    # # "path_hooks" list. *shrug*
    # print('\n\n[AFTER] sys.path_hooks:\n')
    # for path_hook_index, path_hook in enumerate(path_hooks):
    #     print(f'path_hook {path_hook_index}: {repr(path_hook)}')
    #     print(f'\tqualname: {path_hook.__qualname__}')
    #     print(f'\ttype: {type(path_hook)}')
    #     print(f'\tdir: {dir(path_hook)}')

    #FIXME: Uncomment as needed to debug the contents of the "path_hooks" list.
    #Looks like we've actually done this at least twice. Memento: QA Edition.
    #Maybe I should just tattoo this logic onto my forearm already.
    # print(f'path_hooks: {path_hooks}')
    # for path_hook in path_hooks:
    #     try:
    #         file_finder = path_hook('/usr/lib/python3.11')
    #         print(f'file_finder: {file_finder} [{file_finder._loaders}]')
    #     except Exception:
    #         pass

    # ....................{ CACHE                          }....................
    # Prevent subsequent calls to this function from erroneously re-adding
    # duplicate copies of this path hook immediately *AFTER* successfully adding
    # the first such path hook.
    #
    # Note that we intentionally avoid globalizing this path hook until *AFTER*
    # successfully having done so. Why? Negligible safety. The companion
    # remove_beartype_pathhook() function raises a non-human-readable exception
    # if this global is non-"None" but *NOT* in the "path_hooks" list.
    claw_state.beartype_pathhook = loader_factory

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
    -------
    **This function is non-thread-safe.** For both simplicity and efficiency,
    the caller is expected to provide thread-safety through a higher-level
    locking primitive managed by the caller.
    '''

    # Avoid circular import dependencies.
    from beartype.claw._clawstate import claw_state

    # If the add_beartype_pathhook() function has *NOT* yet been called under
    # the active Python interpreter, silently reduce to a noop.
    if claw_state.beartype_pathhook is None:
        return
    # Else, that function has already been called under this interpreter.

    # Remove the prior path hook added by that function *OR* raise a
    # non-human-readable "ValueError" exception if this global is non-"None" but
    # *NOT* in the "path_hooks" list (which should *NEVER* happen, but it will).
    path_hooks.remove(claw_state.beartype_pathhook)

    # Allow subsequent calls to the add_beartype_pathhook() to re-add a new
    # instance of this path hook immediately *AFTER* successfully removing the
    # first such path hook.
    claw_state.beartype_pathhook = None

    # Lastly, clear *ALL* import path hook caches for safety.
    _clear_importlib_caches()

# ....................{ PRIVATE ~ globals                  }....................
_LOADERS_DETAILS = (
    # Beartype-agnostic C extension loader details. Since C extensions *CANNOT*
    # (by definition) be decompiled into an abstract syntax tree (AST), beartype
    # has *NO* means of decorating C extensions. Ergo, we necessarily defer to
    # Python's default C extension loader.
    (ExtensionFileLoader, extension_suffixes()),

    # Beartype-specific **source module loader** (i.e., file loader loading
    # uncompiled pure-Python modules of the filetype ".py").
    (BeartypeSourceFileLoader, SOURCE_SUFFIXES),

    #FIXME: Generalize this into a beartype-specific bytecode module loader.
    #How? By leveraging the third-party "astor" package, which provides a
    #code_to_ast() function decompiling arbitrary code objects into ASTs. See
    #also this relevant StackOverflow answer by myself:
    #    https://stackoverflow.com/a/76641537/2809027

    # Beartype-agnostic **bytecode module loader** (i.e., file loader loading
    # precompiled pure-Python modules from bytecode files compiled in
    # "__pycache__/" subdirectories that lack corresponding uncompiled
    # pure-Python modules of the filetype ".py").
    (SourcelessFileLoader, BYTECODE_SUFFIXES),
)
'''
Tuple of all **file-based module loader details** (i.e., 2-tuple ``(file_loader,
filetypes)`` of the undocumented format expected by the
:meth:`FileFinder.path_hook` class method called by the
:func:`beartype.claw._importlib.clawimpmain.add_beartype_pathhook` function,
associating each file-based module loader with the platform-specific filetypes
of all modules loaded by that module).

We didn't do it. Don't blame the bear.

See Also
--------
:func:`importlib.machinery._get_supported_file_loaders`
    Low-level private getter function strongly inspiring the definition of this
    global, which implements nearly identical functionality (albeit in a
    :mod:`beartype`-specific manner).
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
