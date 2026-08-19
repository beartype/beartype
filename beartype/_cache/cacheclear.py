#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **cache clearerers** (i.e., low-level callables safely resetting
global caches distributed throughout the :mod:`beartype` codebase).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: *URGH*. clear_caches() is currently non-thread-safe, which... isn't
#great. If that callable is called by the higher-level
#_uncache_beartype_if_type_redefined() function called by *MUCH* the
#higher-level beartype_type() decorator. This is *NOT* going to be easy to
#resolve. The easiest way is probably as follows:
#* Add a *SUPER-HUGE BANNER* both to the docstring *AND* the internal body of
#  the clear_caches_global() function defined below. This is a note to ourselves
#  notifying ourselves that we *MUST* manually protect every reference to every
#  dictionary global cleared by this function inside a thread-safe lock. See
#  above for the simplistic one-liner. *shrug*
#* Now here's the hard part. None of the above was hard. *THIS* is hard. We now
#  need to iteratively grep through the codebase for every reference to *ANY*
#  dictionary global referenced by the clear_caches_global() function defined
#  below. For each such reference, we now need to:
#  * Wrap the *ENTIRE* body (in most cases) of the function referencing that
#    dictionary global in a new thread-safe lock resembling:
#        with cache_global_lock:
#
#  However, note that there is an obvious exception to this refactoring:
#  * All dictionary globals that are already internally locked (e.g., by being
#    "CacheMegaStrongCaller" instances) are obviously exempt from this wrapping.
#FIXME: *BOLD NEW IDEA*. Also, the right idea. Ignore most of the prior comment:
#* Shift *ALL* cache globals listed below into a new sibling "cacheglobal"
#  submodule of this subpackage.
#* Import *ALL* such cache globals from "cacheglobal" directly into the global
#  scope of this module. Just. Do. It. \o/
#* Define a new private "_CACHE_GLOBALS" frozenset manually listing *ALL* such
#  imported cache globals.
#* Refactor each such cache global into a "CacheMegaStrongCaller" instance.
#* Refactor clear_caches() to iterate over "_CACHE_GLOBALS" and, for each such
#  cache global, call that cache global's clear_cache() method.
#
#*HMM.* Might not be possible due to import issues, though? No idea. Certainly
#worth a try, anyway. *shrug*

#FIXME: *FASCINATING*, huh? The above suggests we should probably refactor *ALL*
#raw low-level thread-unsafe dictionary globals used below into full-blown
#high-level thread-safe "CacheMegaStrongCaller"-like objects. They don't have
#to *EXACTLY* be "CacheMegaStrongCaller" instances, of course. They just need
#to be instances of something *LIKE* "CacheMegaStrongCaller".

#FIXME: *GULP*. We also need to resolve potential race conditions in
#"fwdrefmeta". See that submodule for further deets, yo. *sigh*

# ....................{ CLEARERS                           }....................
def clear_caches() -> None:
    '''
    Clear (i.e., empty) *all* internal caches leveraged throughout the
    :mod:`beartype` codebase, enabling callers to reset this codebase to its
    initial state.

    This function is typically cleared on detecting a **hot reload** (i.e.,
    attempt by the end user to reimport a presumably redefined user-defined
    module, type, or other object commonly cached by :mod:`beartype`).
    '''
    # print('Clearing all \"beartype._check\" caches...')

    # Defer possibly heavyweight imports. Whereas importing this submodule is a
    # common occurrence, cache clearing and thus calls to this function are a
    # comparatively rarer occurrence. We optimize for the common case.
    from beartype.door._cls.doormeta import _hint_to_wrapper
    from beartype.door._func.doorfunc import (
        _hint_data_to_func_raiser,
        _hint_data_to_func_tester,
    )
    from beartype._check.code.codemain import _HINT_CONF_TO_CHECK_EXPR
    from beartype._check.code.codescope import _tuple_union_to_tuple_union
    from beartype._check.convert._convcoerce import _hint_repr_to_hint
    from beartype._check.forward.reference._cls.fwdrefmeta import (
        _ref_proxy_to_resolved_hint,
        _ref_proxy_to_resolved_type,
    )
    from beartype._check.cls.hint.hintsane import _HINT_TO_HINTSANE
    from beartype._util.bear.utilbearblack import (
        _object_to_is_blacklisted)
    from beartype._util.cache.utilcacheobjattr import clear_object_attr_caches

    #FIXME: Refactor into a global once feature complete. See above, yo!
    # Frozen set of all thread-safe global caches to be cleared below.
    _CACHE_GLOBALS = (
        _hint_to_wrapper,
        _hint_repr_to_hint,
    )

    # For each thread-safe global cache to be cleared...
    for cache_global in _CACHE_GLOBALS:
        # Clear this cache thread-safely.
        cache_global.clear_cache()

    #FIXME: Refactor each of these caches into a "CacheABC" instance, please!
    #Sadly, we're out of time for the moment. Leaving these caches as raw
    #dictionary globals invites subtle race conditions with this function. Ugh.
    #When time permits, the most important of these that should *ABSOLUTELY* be
    #refactored first are:
    #* The pair of "_ref_proxy_to_resolved_*" dictionaries. These are indirectly
    #  exposed to end users via @beartype's forward reference resolvers.

    # Clear all relevant caches used throughout this subpackage.
    _hint_data_to_func_raiser.clear()
    _hint_data_to_func_tester.clear()
    _HINT_TO_HINTSANE.clear()
    _HINT_CONF_TO_CHECK_EXPR.clear()
    _tuple_union_to_tuple_union.clear()
    _ref_proxy_to_resolved_hint.clear()
    _ref_proxy_to_resolved_type.clear()
    _object_to_is_blacklisted.clear()
    clear_object_attr_caches()
