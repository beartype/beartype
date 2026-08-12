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
#    "CacheVastStrong" instances) are obviously exempt from this wrapping.
#FIXME: *BOLD NEW IDEA*. Also, the right idea. Ignore most of the prior comment:
#* Shift *ALL* cache globals listed below into a new sibling "cacheglobal"
#  submodule of this subpackage.
#* Import *ALL* such cache globals from "cacheglobal" directly into the global
#  scope of this module. Just. Do. It. \o/
#* Define a new private "_CACHE_GLOBALS" frozenset manually listing *ALL* such
#  imported cache globals.
#* Refactor each such cache global into a "CacheVastStrong" instance.
#* Refactor clear_caches() to iterate over "_CACHE_GLOBALS" and, for each such
#  cache global, call that cache global's clear_cache() method.
#
#*HMM.* Might not be possible due to import issues, though? No idea. Certainly
#worth a try, anyway. *shrug*

#FIXME: *FASCINATING*, huh? The above suggests we should probably refactor *ALL*
#raw low-level thread-unsafe dictionary globals used below into full-blown
#high-level thread-safe "CacheVastStrong"-like objects. They don't have
#to *EXACTLY* be "CacheVastStrong" instances, of course. They just need
#to be instances of something *LIKE* "CacheVastStrong".
#FIXME: That said, our issue with "CacheVastStrong" was always the syntax.
#Seriously. We should use that thing everywhere. We currently do *NOT* use
#that thing everywhere for the simple (yet horrible) reason that its syntax is
#so sucky we can't bear to use it anywhere. An alternative would be to design
#some completely new alternative that reads sanely with Pythonic syntax: e.g.,
#    # Instead of unreadable syntax like this...
#    wrapper: 'beartype.door.TypeHint' = (
#        _hint_to_wrapper.cache_or_get_cached_func_return_arg(  # type: ignore[assignment]
#            # Cache this wrapper singleton under this hint.
#            key=hint,
#            # If a wrapper singleton has yet to be instantiated for this
#            # hint, do so by calling this private factory method...
#            value_factory=cls._make_wrapper,  # type: ignore[arg-type]
#            # ...with this hint passed as the sole parameter to that method.
#            arg=hint,
#        ))
#
#    # ...readably syntax like this would be *MAGICAL*:
#    wrapper: 'beartype.door.TypeHint' = None  # type: ignore[assignment]
#    with _hint_to_wrapper[hint] as wrapper:
#         _hint_to_wrapper[hint] = wrapper = cls._make_wrapper(hint)
#
#Significantly easier to read. Still not perfect, of course... but nothing is
#perfect. The perfect is the enemy *BLAH BLAH*.
#
#So how does that actually work, then? The idea:
#* The "dict" subclass (of which "_hint_to_wrapper" is an instance) overrides
#  both the __getitem__() dunder method *AND* the dict.get() method to
#  return... uh, what? New context manager objects? Sounds expensive.
#  Basically, it depends on whether this is locked behind a "Lock" or "RLock".
#  If:
#  * A "Lock", we can efficiently and safely reuse a single private context
#    manager bound in the subclass __init__() constructor to the current
#    "dict" subclass instance. Simple.
#  * An "RLock", we're kinda screwed. We'd have to inefficiently create and
#    return one now context manager object on each __getitem__() call. Sucky.
#    Kinda defeats the entire point of caching. *sigh*
#    Oh, right. We could internally cache and maintain a private *POOL* (i.e.,
#    list) of all previously created context manager objects returned by each
#    prior __getitem__() call. Would totally work. And because access to that
#    pool is locked behind a threadsafe "RLock", we wouldn't have to worry
#    about locking that pool. Just append to and pop from a private list
#    unique to each subclass.
#
#Lastly, note that that class should obviously *NOT* be an actual "dict"
#subclass. It just behaves like a "dict" subclass. Useful names for the two
#obvious class variants of this core idea include:
#* "beartype._util.kind.map.utilmaplock.DictLocked".
#* "beartype._util.kind.map.utilmaplock.DictRLocked".
#
#Note that we're *NOT* bothering with the obsolete "beartype._util.cache.maplike"
#subpackage. Too antiquated. The *ONLY* thing we should do with that
#subpackage is to explicitly note in the docstrings of existing classes like
#"CacheBoundedStrong" is that this class has been *OBSOLETED* by the
#substantially newer and more Pythonic "Dict(R|)Locked" family of classes.
#
#Lastly lastly:
#* The Dict(R|)Locked.__getitem__() should raise an exception if called inside
#  an existing "with" block of this class. Maintain an internal
#  "self._is_entered: bool = False" instance variable to track this. *shrug*
#* The Dict(R|)Locked.__setitem__() dunder method should raise an exception if
#  *NOT* inside an existing "with" block.
#FIXME: *OH*. The above design doesn't work, sadly. Why? Because context
#managers are currently required to "yield". They can't *NOT* "yield". Which
#means the body of the "with...:" block would *ALWAYS* get executed, which
#totally defeats the purpose of caching. Oh, well. Guess we gotta use
#"CacheVastStrong" and friends, huh? That's fine. Python leaves us no
#alternative. The point is thread-safe efficiency. This is the *ONLY* way to get
#that. It is what it is. *sigh*

# ....................{ CLEARERS                           }....................
def clear_caches() -> None:
    '''
    Clear (i.e., empty) *all* internal caches leveraged throughout the
    :mod:`beartype` codebase, enabling callers to reset this codebase to its
    initial state.

    This function is typically cleared on detecting a **hot reload** (i.e.,
    attempt by the end user to reimport a presumably redefined user-defined
    module, type, or other object commonly cached by :mod:`beartype`). Notably,
    this function clears:

    * The :func:`beartype.door.die_if_unbearable` **cache** (i.e., private
      :data:`beartype.door._func.doorfunc._HINT_CONF_EXCEPTION_PREFIX_TO_FUNC_RAISER`
      dictionary).
    * The :func:`beartype.door.is_bearable` **cache** (i.e., private
      :data:`beartype.door._func.doorfunc._HINT_CONF_EXCEPTION_PREFIX_TO_FUNC_TESTER`
      dictionary).
    * The **annotations dictionary cache** (i.e., private
      :data:`beartype._util.hint.pep.proposal.pep749.pep649749annotate._MODULE_NAME_TO_HINTABLE_BASENAME_TO_ANNOTATIONS`
      dictionary).
    * All **forward reference proxy caches** (i.e., private
      :data:`beartype._check.forward.reference._cls.fwdrefmeta._ref_proxy_to_resolved_hint`
      and
      :data:`beartype._check.forward.reference._cls.fwdrefmeta._ref_proxy_to_resolved_type`
      dictionaries).
    * The **sanified type hint metadata cache** (i.e., private
      :data:`beartype._check.cls.hint.hintsane._HINT_TO_HINTSANE`
      dictionary).
    * The **tuple union cache** (i.e., private
      :data:`beartype._check.code.codescope._tuple_union_to_tuple_union`
      dictionary).
    * The **type hint code factory cache** (i.e., private
      :data:`beartype._check.code.codemain import _HINT_CONF_TO_CHECK_EXPR`
      dictionary).
    * The **type hint coercion cache** (i.e., private
      :data:`beartype._check.convert._convcoerce._hint_repr_to_hint`
      dictionary).
    * The **type hint wrapper cache** (i.e., private
      :data:`beartype._door._cls.doormeta._hint_to_wrapper` dictionary).
    * The **object blacklist cache** (i.e., private
      :data:`_object_to_is_blacklisted` dictionary).
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
