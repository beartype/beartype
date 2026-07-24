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
from beartype.roar import BeartypeClawImportlibFileFinderPathHookInactiveWarning
from beartype.roar._roarexc import (
    _BeartypeClawImportlibIsPathHookActiveException)
from beartype.claw._importlib._clawimpfilefinder import (
    make_beartype_file_finder_path_hook_index)
from beartype._metaverse import URL_ISSUES
from beartype._util.error.utilerrwarn import issue_warning
from importlib import invalidate_caches
from sys import (
    path_hooks,
    path_importer_cache,
)

# ....................{ ADDERS                             }....................
#FIXME: Unit test us up, please.
def add_beartype_path_hook() -> None:
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
    :class:`beartype.claw._importlib._clawimpfileloader.BeartypeSourceFileLoader`
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
    #          #* Define the "meta_path_external_names" and
    #          #  "path_hooks_external_names" local variables interpolated
    #          #  into the message below accordingly, please. What a huge job!
    #          warning_message = (
    #              f'"beartype.claw"-based runtime type-checking inactive. '
    #              f'Competing third-party packages or modules already '
    #              f'registered their own import hooks incompatibly overriding '
    #              f'"beartype.claw"-based import hooks responsible for '
    #              f'performing runtime type-checking. '
    #              f'Competing high-level "sys.meta_path" hooks include:\n'
    #              f'{meta_path_external_names}\n'
    #              f'Competing low-level "sys.path_hooks" hooks include:\n'
    #              f'{path_hooks_external_names}\n'
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
    #        if claw_state.beartype_path_hook is not None:
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
    if claw_state.beartype_path_hook is not None:
        # Silently reduce to a noop.
        return
    # Else, this adder has yet to be called.

    # ....................{ PATH HOOK                      }....................
    # Beartype-specific file finder path hook created by this factory and the
    # 0-based index of the "sys.path_hooks" list into which this path hook
    # should be inserted by the caller.
    path_hook, path_hook_index = make_beartype_file_finder_path_hook_index()

    # Insert this beartype-specific file finder path hook into the desired index
    # of the global "sys.path_hooks" list -- typically, immediately *BEFORE* the
    # default beartype-agnostic file finder path hook.
    path_hooks.insert(path_hook_index, path_hook)

    # ....................{ CACHE                          }....................
    # Prevent subsequent calls to this function from erroneously re-adding
    # duplicate copies of this path hook immediately *AFTER* successfully adding
    # the first such path hook.
    #
    # Note that we intentionally avoid globalizing this path hook until *AFTER*
    # successfully having done so. Why? Negligible safety. The companion
    # remove_beartype_path_hook() function raises a non-human-readable exception
    # if this global is non-"None" but *NOT* in the "path_hooks" list.
    claw_state.beartype_path_hook = path_hook

    # Lastly, clear *ALL* import path hook caches for safety.
    _clear_importlib_caches()

# ....................{ REMOVERS                           }....................
#FIXME: Unit test us up, please.
def remove_beartype_path_hook() -> None:
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

    # If the add_beartype_path_hook() function has *NOT* yet been called under
    # the active Python interpreter, silently reduce to a noop.
    if claw_state.beartype_path_hook is None:
        return
    # Else, that function has already been called under this interpreter.

    # Remove the prior path hook added by that function *OR* raise a
    # non-human-readable "ValueError" exception if this global is non-"None" but
    # *NOT* in the "path_hooks" list (which should *NEVER* happen, but it will).
    path_hooks.remove(claw_state.beartype_path_hook)

    # Allow subsequent calls to the add_beartype_path_hook() to re-add a new
    # instance of this path hook immediately *AFTER* successfully removing the
    # first such path hook.
    claw_state.beartype_path_hook = None

    # Lastly, clear *ALL* import path hook caches for safety.
    _clear_importlib_caches()

# ....................{ PRIVATE ~ warners                  }....................
#FIXME: Unit test us up, please. *sigh*
#FIXME: *CRITICAL*. Only issue this warning *ONCE* per active Python process.
#Note that we've already done this sort of warning caching elsewhere. Grep the
#codebase for 'issue_warning\(' to decide where. The point is, though, that we
#should just automate this at this point. Specifically:
#* Generalize issue_warning() to accept this new optional parameter:
#      is_oneshot: bool = False,
#* Pass "is_oneshot=True" below to that call of issue_warning().
#* Improve issue_warning() as follows:
#  * Define a private "_issue_warning_types_oneshot: set[BeartypeWarning]"
#    global in the same submodule.
#  * If "is_oneshot", then:
#    * Trivially avoid concurrency issues by properly locking. *IMPORTANT*. If
#      we can trivially avoid concurrency issues, we should. *shrug*
#    * Cache into that "_issue_warning_types_oneshot" set. Trivial, yo. \o/
#* Pass "is_oneshot=True" throughout the codebase. Honestly, most calls of
#  issue_warning() should probably be passing that.
def _warn_if_beartype_pathhook_inactive() -> None:
    '''
    Issue a non-fatal warning if the **beartype-specific file finder path hook**
    (i.e., closure created and returned by calling the
    :meth:`importlib.machinery.FileFinder.path_hook` static method with
    beartype-specific file finder path hook loader details permuted from the
    standard "default" file finder path hook loader details) is inactive despite
    having been added by the parent :func:`.add_beartype_path_hook` caller to
    the global :obj:`sys.path_hooks` list, typically due to a third-party
    package or module injecting a competing import hook into an earlier index of
    either that list *or* the higher-level global :obj:`sys.meta_path` list.

    This warning implies *all* :mod:`beartype.claw` import hooks registered by
    *all* third-party packages and modules to be inactive, effectively disabling
    *all* automated runtime type-checking for the duration of the current Python
    process. Clearly, this connotes a significant QA failure. In theory, this
    non-fatal warning should instead be promoted into a fatal exception. In
    practice, doing so would break most of the Python ecosystem. Why? Because
    the beartype-specific file finder path hook has been intentionally designed
    so as to deprioritize itself in favour of competing import hooks authored by
    third-party packages and modules. Why? Because many of those import hooks
    are mission-critical. PyInstaller-specific import hooks, for example, load
    imported modules bundled inside PyInstaller-frozen apps. While unavoidable,
    this permissiveness is a double-edged sword. Deprioritizing
    :mod:`beartype.claw` import hooks does maximize compatibility and
    interoperability across the Python ecosystem -- but also the likelihood of
    :mod:`beartype.claw` import hooks being inactivated and thus ignored.

    Caveats
    -------
    **This function is non-thread-safe.** For both simplicity and efficiency,
    the caller is expected to guarantee thread-safety through a higher-level
    locking primitive managed directly by that caller.

    Warns
    -----
    BeartypeClawImportlibFileFinderPathHookInactiveWarning
        If the beartype-specific file finder path hook is inactive.
    '''

    # ~~~~~~~~~~~~~~~~~[ LEYCEC'S POLYCHROMATIC HOOK ELICITOR ]~~~~~~~~~~~~~~~~~
    # Attempt to import the beartype-specific import hook activation smoke test
    # (i.e., private empty submodule isolated to the "beartype" codebase
    # facilitating a crude smoke test). If the beartype-specific file finder
    # path hook previously added by the add_beartype_path_hook() function is
    # still active, then (in order):
    # * That hook will load that submodule using our beartype-specific source
    #   file loader (i.e., "BeartypeSourceFileLoader" instance).
    # * That loader will then:
    #   * Detect that the submodule being loaded is our beartype-specific import
    #     hook activation smoke test.
    #   * Respond by raising the beartype-specific private
    #     "_BeartypeClawImportlibIsPathHookActiveException" raised *ONLY* by
    #     this specific use case.
    #
    # There thus exists a one-to-one mapping between "beartype.claw" import
    # hooks being active and catching that exception when importing that
    # submodule. Namely, if importing that submodule raises that exception, then
    # it *MUST* be the case that "beartype.claw" import hooks are active; else,
    # it *MUST* be the case that "beartype.claw" import hooks are inactive. And
    # we refer to this one-to-one mapping as...
    #
    # Leycec's Polychromatic Hook Elicitor! *BEHOLD THE TERROR AND CRY*. \o/
    try:
        from beartype.claw._importlib import _clawimpsmoke
    # If importing the beartype-specific import hook activation smoke test
    # raises the beartype-specific private exception raised *ONLY* by this
    # specific use case, "beartype.claw" import hooks are active. In this case,
    # silently reduce to a noop. See the above discussion.
    except _BeartypeClawImportlibIsPathHookActiveException:
        return
    # Else, importing the beartype-specific import hook activation smoke test
    # failed to raise the beartype-specific private exception! "beartype.claw"
    # import hooks *MUST* be inactive. Thus, issue a non-fatal warning below.

    # ....................{ LOCALS                         }....................
    #FIXME: Define these strings properly as suggested below, please. *sigh*

    # "*"-delimited string listing the fully-qualified names of all competing
    # import hooks on the global "sys.meta_path" list defined by third-party
    # packages or modules, initialized to the empty string.
    meta_path_external_names = ''

    # "*"-delimited string listing the fully-qualified names of all competing
    # import hooks on the global "sys.path_hooks" list defined by third-party
    # packages or modules , initialized to the empty string.
    path_hooks_external_names = ''

    # ....................{ MESSAGE                        }....................
    #FIXME: Dynamically improve this message as follows:
    #* Iteratively construct an ordered list of the names all
    #  third-party "sys.meta_path" hooks that are currently active.
    #  Standard "sys.meta_path" hooks should be ignored, of course.
    #* Iteratively construct a *SEPARATE* list of the names all
    #  third-party "sys.path_hooks" that are currently active
    #  *AND* precede our beartype-specific "sys.path_hooks" hook.
    #  Standard "sys.path_hooks" should be ignored, of course.
    #* Define a new join_bulleted() string-joining function in the
    #  existing "beartype._util.text.utiltextjoin" submodule. This
    #  function should precede each of the passed strings by the
    #  prefix "\n* ", probably by trivially deferring to the existing
    #  join_delimited() joiner. *shrug*
    #* For each of these lists that is non-empty, coerce these
    #  non-empty lists into a string by deferring to that new
    #  join_bulleted() joiner.
    #* Define the "meta_path_external_names" and
    #  "path_hooks_external_names" local variables interpolated
    #  into the message below accordingly, please. What a huge job!

    # Warning message to be issued below.
    warning_message = (
        f'"beartype.claw"-based runtime type-checking erroneously disabled. '
        f'Beartype is unable to automatically runtime type-check any '
        f'packages or modules under the active Python app stack. '
        f'Competing third-party packages or modules in this stack already '
        f'registered incompatible import hooks silently overriding '
        f'"beartype.claw" import hooks (e.g., beartype_this_package()).\n'
    )

    # If the global "sys.meta_path" list contains one or more competing import
    # hooks defined by third-party packages or modules, append this warning
    # message with a human-readable substring enumerating the fully-qualified
    # names of these hooks.
    if meta_path_external_names:
        warning_message += (
            f'Competing high-level "sys.meta_path" hooks include:\n'
            f'{meta_path_external_names}\n'
        )
    # Else, the global "sys.meta_path" list is still the default such list and
    # thus *CANNOT* be to blame for "beartype.claw" import hooks being inactive.

    # If the global "sys.path_hooks" list contains one or more competing import
    # hooks defined by third-party packages or modules, append this warning
    # message with a human-readable substring enumerating the fully-qualified
    # names of these hooks.
    if path_hooks_external_names:
        warning_message += (
            f'Competing low-level "sys.path_hooks" hooks include:\n'
            f'{path_hooks_external_names}\n'
        )
    # Else, the global "sys.path_Hooks" list is still the default such list and
    # thus *CANNOT* be to blame for "beartype.claw" import hooks being inactive.

    # Finalize this warning message with verbose advice that makes gerbils weep.
    warning_message += (
        f"This is mostly Python's fault. "
        f'Python lacks standards governing import hook interoperability. '
        f'In the absence of sane standards, '
        f'Python import hooks are currently an '
        f'unhinged Wild West feeding frenzy of '
        f'competing third-party import hooks that love to eat each other. '
        f"In short, Python's standard \"importlib\" machinery sucks. "
        f'You now have three sucky options. Either:\n'
        f'* (Recommended) Contact the authors of the competing '
        f'third-party packages or modules listed above. '
        f'Kindly request they improve the compatibility of '
        f'their import hooks with other import hooks registered by '
        f'other packages and modules -- especially '
        f'those registered by the "beartype.claw" subpackage. '
        f'Please ping @leycec '
        f'(the principal @beartype maintainer) on all relevant '
        f'issues so that he can nod respectfully and pretend to '
        f'render assistance.\n'
        f'* (Not recommended) Complain to us about '
        f"other people's problems on the @beartype issue tracker at:\n"
        f'\t{URL_ISSUES}\n'
        f'  This is usually useless. '
        f'There is probably nothing @beartype itself can do. '
        f'We have no meaningful control or leverage over '
        f'competing third-party packages or modules. '
        f'We cannot force others to improve the interoperability '
        f'of the incompatible import hooks they themselves define. '
        f'We can only heckle them with animated GIFs. '
        f'Do this only if you want us to heckle somebody '
        f'with animated GIFs.\n'
        f'* (Desperation move) Globally silence this warning by '
        f'adding to your top-level "{{muh_package}}.__init__" submodule:\n'
        f'\tfrom beartype.roar import BeartypeClawImportlibFileFinderPathHookInactiveWarning\n'
        f'\tfrom warnings import filterwarnings\n'
        f'\tfilterwarnings(action="ignore", category=BeartypeClawImportlibFileFinderPathHookInactiveWarning)\n'
    )

    # Issue this non-fatal warning.
    issue_warning(
        warning_cls=BeartypeClawImportlibFileFinderPathHookInactiveWarning,
        message=warning_message,
    )

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
