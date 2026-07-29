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
from beartype._data.claw.dataclawmagic import (
    BEARTYPE_CLAW_FILE_FINDER_PATH_HOOK_ATTR_NAME,
    STANDARD_META_PATH_ITEM_NAMES,
    STANDARD_PATH_HOOKS_ITEM_NAMES,
)
from beartype._metaverse import URL_ISSUES
from beartype._util.error.utilerrwarn import issue_warning
from beartype._util.text.utiltextjoin import join_strings_bulleted_unnumbered
from beartype._util.utilobjget import get_object_name
from importlib import invalidate_caches
from sys import (
    meta_path,
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

    Warns
    -----
    BeartypeClawImportlibFileFinderPathHookInactiveWarning
        If our beartype-specific file finder path hook is inactive even after
        adding that hook to the global :mod:`sys.path_hooks` list.

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

    # ....................{ GUARD                          }....................
    # If this adder has yet to be called...
    if claw_state.beartype_path_hook is None:
        # ....................{ PATH HOOK                  }....................
        # Beartype-specific file finder path hook created by this factory and
        # the 0-based index of the "sys.path_hooks" list into which this path
        # hook should be inserted by the caller.
        path_hook, path_hook_index = make_beartype_file_finder_path_hook_index()

        # Insert this beartype-specific file finder path hook into the desired
        # index of the global "sys.path_hooks" list -- typically, immediately
        # *BEFORE* the default beartype-agnostic file finder path hook.
        path_hooks.insert(path_hook_index, path_hook)

        # ....................{ CACHE                      }....................
        # Prevent subsequent calls to this function from erroneously re-adding
        # duplicate copies of this path hook immediately *AFTER* successfully
        # adding the first such path hook.
        #
        # Note that we intentionally avoid globalizing this path hook until
        # *AFTER* successfully having done so. Why? Negligible safety. The
        # companion remove_beartype_path_hook() function raises a
        # non-human-readable exception if this global is non-"None" but *NOT* in
        # the global "sys.path_hooks" list.
        claw_state.beartype_path_hook = path_hook

        # Clear all import path hook caches for safety *AFTER* adding our path
        # hook to the global "sys.path_hooks" list above.
        _clear_importlib_caches()
    # Else, this adder has already been called at least once by a third-party
    # reverse dependency of beartype under the active Python interpreter. Avoid
    # erroneously re-adding our beartype-specific file finder path hook to the
    # "sys.path_hooks" list multiple times.

    # ....................{ WARN                           }....................
    # If our beartype-specific file finder path hook previously added by
    # that prior call of this adder is no longer active (e.g., due to
    # another third-party package or module having since added one or more
    # competing hooks overriding our own), issue a non-fatal warning.
    _warn_if_beartype_pathhook_inactive()
    # Else, our beartype-specific file finder path hook previously added by
    # that prior call of this adder is still active. Go, Bear! Go, Bear!

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

# ....................{ PRIVATE ~ globals                  }....................
_is_warned_if_beartype_pathhook_inactive: bool = False
'''
:data:`True` only if the :func:`_warn_if_beartype_pathhook_inactive` function
has already issued a non-fatal warning under the active Python interpreter.

That function internally guards against issuing the same warning multiple times
with this crude cache. That warning is extremely verbose and thus likely to
incite more bad than good in end users overly exposed to that warning.
'''

# ....................{ PRIVATE ~ warners                  }....................
#FIXME: Unit test us up, please. *sigh*
def _warn_if_beartype_pathhook_inactive() -> None:
    '''
    Issue a non-fatal warning if our **beartype-specific file finder path hook**
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

    **This function issues this warning at most only once per Python process.**
    Technically, that isn't a caveat. That is a good thing. This warning is
    extremely verbose and thus likely to incite more bad than good in end users
    overly exposed to this warning.

    Warns
    -----
    BeartypeClawImportlibFileFinderPathHookInactiveWarning
        If our beartype-specific file finder path hook is inactive.
    '''

    # ....................{ NOOP                           }....................
    # Enable this global to be assigned to below.
    global _is_warned_if_beartype_pathhook_inactive

    # If this function has already issued this warning, avoid doing so again.
    # This warning is verbose and thus likely to incite anger in users. We know.
    # Instead, silently reduce to a noop by returning immediately.
    if _is_warned_if_beartype_pathhook_inactive:
        return
    # Else, this function has *NOT* already issued this warning.

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

    # Record that this function has now issued this warning, preventing
    # subsequent calls from uselessly doing so again.
    #
    # Note that we intentionally assign this global early rather than late
    # (i.e., after calling the issue_warning() function below). Why? To reduce
    # the likelihood of issuing this warning multiple times in the event that
    # the caller fails to call this function from a thread-safe context. That
    # should never happen. Since assigning this global early is trivial,
    # however, we do so to avoid suffering in both users and in us. No pain!
    _is_warned_if_beartype_pathhook_inactive = True

    # ....................{ META PATH                      }....................
    #FIXME: Shift this logic into a new _get_meta_path_hook_custom_names_str()
    #getter, please! *sigh*

    # List of the fully-qualified names of all competing meta path hooks on the
    # global "sys.meta_path" list defined by third-party packages or modules,
    # iteratively appended to by the iteration performed below.
    meta_path_hook_custom_names_list = []

    # For each meta path hook registered in the global "sys.meta_path" list...
    for meta_path_hook in meta_path:
        # Fully-qualified name of either:
        # * If this meta path hook is either a callable *OR* class, this
        #   callable or class as is.
        # * Else (i.e., this meta path hook is neither a callable *NOR* class),
        #   the type of this meta path hook. This fallback is required. Some
        #   custom meta path hooks defined by third-party packages and modules
        #   (e.g., the third-party "distutils"-specific meta path hook) are
        #   neither callables nor classes but simply arbitrary objects
        #   technically satisfying the PEP 302-compliant "meta_path" hook API.
        meta_path_hook_name = get_object_name(
            obj=meta_path_hook, is_fallback_type_name=True)

        # If fully-qualified name of this meta path hook is *NOT* that of a
        # standard meta path hook (i.e., predefined by the active Python
        # interpreter at interpreter startup), append this name to this list.
        if meta_path_hook_name not in STANDARD_META_PATH_ITEM_NAMES:
            meta_path_hook_custom_names_list.append(meta_path_hook_name)
        # Else, fully-qualified name of this meta path hook is that of a
        # standard meta path hook. In this case, silently ignore this meta path
        # hook and continue to the next.

    # Bullet point-delimited string listing the fully-qualified names of all
    # competing meta path hooks on the global "sys.meta_path" list defined by
    # third-party packages or modules.
    meta_path_hook_custom_names = join_strings_bulleted_unnumbered(
        strings=meta_path_hook_custom_names_list, is_double_quoted=True)

    # ....................{ PATH HOOKS                     }....................
    #FIXME: Shift this logic into a new _get_path_hook_custom_names_str()
    #getter, please! *sigh*

    # List of the fully-qualified names of all competing path hooks on the
    # global "sys.path_hooks" list defined by third-party packages or modules,
    # iteratively appended to by the iteration performed below.
    path_hook_custom_names_list = []

    # For each path hook registered in the global "sys.path_hooks" list...
    for path_hook in path_hooks:
        # Fully-qualified name of either:
        # * If this path hook is either a callable *OR* class, this callable or
        #   class as is.
        # * Else (i.e., this path hook is neither a callable *NOR* class), the
        #   type of this path hook. See above for further discussion.
        path_hook_name = get_object_name(
            obj=path_hook, is_fallback_type_name=True)

        # If fully-qualified name of this path hook is *NOT* that of a standard
        # path hook (i.e., predefined by the active Python interpreter at
        # interpreter startup)...
        if path_hook_name not in STANDARD_PATH_HOOKS_ITEM_NAMES:
            # If this path hook defines the beartype-specific dunder attribute
            # uniquely monkey-patched into the beartype-specific file finder
            # path hook created and returned by the low-level
            # make_beartype_file_finder_path_hook_index() factory function, this
            # path hook *SHOULD* be that path hook. Since the higher-level
            # add_beartype_path_hook() function intentionally adds that path
            # hook immediately before Python's own standard file finder path
            # hook *AND* since preceding path hooks assume precedence over
            # subsequent path hooks, the beartype-specific file finder path hook
            # assumes precedence over and thus effectively inactivates *ALL*
            # subsequent path hooks. Ergo, *ALL* subsequent path hooks are
            # irrelevant. If some competing path hook inactivated the
            # beartype-specific file finder path hook, that competing path hook
            # *MUST* already have been appended to this list. Appending any
            # further path hook names to this list would only uselessly confound
            # this already confounding issue. Immediately halt appending, yo!
            if getattr(
                path_hook,
                BEARTYPE_CLAW_FILE_FINDER_PATH_HOOK_ATTR_NAME,
                False,
            ):
                break
            # Else, this path hook is *NOT* the beartype-specific file finder
            # path hook. This hook precedes that hook and *COULD* thus be the
            # culprit responsible for inactivating that hook.

            # Append this name to this list.
            path_hook_custom_names_list.append(path_hook_name)
        # Else, fully-qualified name of this path hook is that of a standard
        # path hook. In this case, silently ignore this path hook and continue
        # to the next.

    # Bullet point-delimited string listing the fully-qualified names of all
    # competing path hooks on the global "sys.path_hooks" list defined by
    # third-party packages or modules.
    path_hook_custom_names = join_strings_bulleted_unnumbered(
        strings=path_hook_custom_names_list, is_double_quoted=True)

    # ....................{ MESSAGE                        }....................
    # Warning message to be issued below.
    warning_message = (
        '"beartype.claw"-based runtime type-checking erroneously disabled. '
        'Beartype is unable to automatically runtime type-check any '
        'packages or modules under the active Python app stack. '
        'Competing third-party packages or modules in this stack already '
        'registered incompatible import hooks silently overriding '
        '"beartype.claw" import hooks (e.g., beartype_this_package()).\n'
    )

    # If the global "sys.meta_path" list contains one or more competing import
    # hooks defined by third-party packages or modules, append this warning
    # message with a human-readable substring enumerating the fully-qualified
    # names of these hooks.
    if meta_path_hook_custom_names:
        warning_message += (
            f'Competing high-level "sys.meta_path" hooks include:'
            f'{meta_path_hook_custom_names}\n'
        )
    # Else, the global "sys.meta_path" list is still the default such list and
    # thus *CANNOT* be to blame for "beartype.claw" import hooks being inactive.

    # If the global "sys.path_hooks" list contains one or more competing import
    # hooks defined by third-party packages or modules, append this warning
    # message with a human-readable substring enumerating the fully-qualified
    # names of these hooks.
    if path_hook_custom_names:
        warning_message += (
            f'Competing low-level "sys.path_hooks" hooks include:'
            f'{path_hook_custom_names}\n'
        )
    # Else, the global "sys.path_Hooks" list is still the default such list and
    # thus *CANNOT* be to blame for "beartype.claw" import hooks being inactive.

    # Finalize this warning message with verbose advice that makes gerbils weep.
    warning_message += (
        f'You now have three equally sucky options. Either:\n'
        f'* (Desperation move) Globally silence this warning by adding to '
        f'your top-level "{{your_package}}.__init__" submodule:\n'
        f'\tfrom beartype.roar import BeartypeClawImportlibFileFinderPathHookInactiveWarning\n'
        f'\tfrom warnings import filterwarnings\n'
        f'\tfilterwarnings(action="ignore", category=BeartypeClawImportlibFileFinderPathHookInactiveWarning)\n'
        f'* (Recommended) Kindly submit an issue to the issue tracker of '
        f'whichever of the competing third-party import hooks (listed above) '
        f'is directly responsible for ignoring "beartype.claw" import hooks. '
        f'Good luck identifying the culprit. '
        f'Request they improve the compatibility of '
        f'their import hooks with '
        f'other PEP 302-compliant import hooks registered by '
        f'other packages and modules -- especially '
        f'those registered by the "beartype.claw" subpackage. '
        f'Please ping @leycec (the principal @beartype maintainer) on '
        f'all relevant issues so that he can '
        f'nod respectfully at everyone and pretend to render assistance.\n'
        f'* (Not recommended) Complain to us about '
        f"other people's problematic code on the @beartype issue tracker at:\n"
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
        f'This is mostly the fault of Python itself, which '
        f'lacks standards governing import hook interoperability. '
        f"The import hook ecosystem is an "
        f'unscoped Battle Royale-esque feeding frenzy of '
        f'internecine API masochists committed to '
        f'flagellating one other, themselves, and Python itself with '
        f'explosive burlap sacks all reading:\n'
        f'\t"WARNING: Pythonista! '
        f'Domain Specific Languages (DSL) may '
        f'cause permanent ruptures in the code-space plenum. '
        f'Break only in case of emergency."\n'
        f"You are now experiencing that emergency. We've all had better days."
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
