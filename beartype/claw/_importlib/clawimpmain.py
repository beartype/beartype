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

# ....................{ TODO                               }....................
#FIXME: Beartype now needs to explicitly guard against the increasingly common
#edge case in which one or more third-party packages have already injected one
#or more competing import hooks into "sys.path_hooks". There are a variety of
#ways beartype can do this. First, though, let's examine what exactly these
#packages are to. To the best of our knowledge, these packages cleave into two
#distinct categories of badness:
#* *CATEGORY 1*: PyInstaller. It's incredibly important that "beartype.claw"
#  import hooks *NOT* be ignored when registered inside a PyInstaller-frozen
#  app. Currently, they are. Not good. Sadly, this is probably also non-trivial.
#  PyInstaller is... unique. To prevent PyInstaller-frozen apps from ignoring
#  "beartype.claw" import hooks, we'll need to dissect the PyInstaller codebase,
#  discover what exactly the PyInstaller path hook is doing, determine whether
#  beartype can (or should) monkey-patch that approach, and then do that. Since
#  this is almost certainly non-trivial, it's best to leave this for later.
#* *CATEGORY 2*: AST transforms. It's incredibly important that "beartype.claw"
#  import hooks also *NOT* be ignored when registered inside an app whose app
#  stack is so large that it transitively imports one or more of those of
#  packages during its app lifetime. Currently, they are. Also not good.
#  Thankfully, this should be *MUCH* easier than the PyInstaller case. Why?
#  Because we (in theory, anyway) more or less already know what to do to
#  resolve this AST case.
#
#So, AST transforms it is! Now here's where things get *REAL* interesting:
#* Define a new "beartype.claw._importlib.loader" subpackage. In this
#  subpackage:
#  * Move "_clawimpfileloader" to
#    "beartype.claw._importlib.loader.clawimploadpassive".
#  * Rename "BeartypeSourceFileLoader" to "BeartypeSourceFileLoaderPassive".
#  * Define a new sibling "clawimploadaggressive" submodule, copy-pasted from
#    "clawimploadpassive".
#* In this new "clawimploadaggressive" submodule:
#  * Rename "BeartypeSourceFileLoader" to "BeartypeSourceFileLoaderAggressive".
#* In this new "BeartypeSourceFileLoaderAggressive" subclass:
#  * First, the whole idea here is that, unlike
#    "BeartypeSourceFileLoaderPassive", "BeartypeSourceFileLoaderAggressive"
#    explicitly performs path hook *COMPOSITION* (i.e., chaining, cascading).
#    Inside our BeartypeSourceFileLoaderAggressive.get_code() override, we'll
#    (probably) want to implement a similar scheme as currently employed by the
#    default MetaPathFinder._path_hooks() static method. Note that PEP 302
#    mandates a *TOTALLY* cray-cray search algorithm as officially documented:
#        "If the path entry is not present in the cache, the path based finder
#         iterates over every callable in sys.path_hooks. Each of the path entry
#         hooks in this list is called with a single argument, the path entry to
#         be searched. This callable may either return a path entry finder that
#         can handle the path entry, or it may raise ImportError. An ImportError
#         is used by the path based finder to signal that the hook cannot find a
#         path entry finder for that path entry. The exception is ignored and
#         import path iteration continues."
#
#    Just accept that madness for now. Eventually, that should also be cached by
#    us in a similar manner as the "MetaFileFinder" caches the results of
#    calling the _path_hooks() static method. The point is,
#    BeartypeSourceFileLoaderAggressive.get_code() searches over
#    "sys.path_hooks" until either... Wait. Actually:
#    * If "len(sys.path_hooks) == DEFAULT_PATH_HOOKS_LEN", don't even bother
#      searching. Fallback to our existing efficient
#      BeartypeSourceFileLoaderPassive.get_code() approach.
#    * Else, we need to search over the slice "sys.path_hooks[1:-1]" (assuming
#      that the first entry is the beartype-specific file finder path hook and
#      the last entry is the beartype-agnostic file finder path hook) for the
#      first path hook that, when passed the passed path, does *NOT* raise an
#      "ImportError". Madness. *WHATEVAH*. Then:
#      * If we do *NOT* find a match, then (yet again) we fallback to our
#        existing efficient BeartypeSourceFileLoaderPassive.get_code() approach.
#        There's *NO* point in calling the default beartype-agnostic file finder
#        path hook, honestly. That just needlessly complicates everything.
#      * If we *DO* find a match, then stuff gets *REAL* interesting. We need to
#        ensure that any AST transform instantiated by that matching hook gets
#        monkey-patched by us first to ensure that our AST transform is also
#        applied. Note that path hooks return a fully instantiated *FINDER*
#        rather than either a finder class *OR* an actual loader. The finder is
#        literally a "FileFinder" defining the pivotal find_spec() method. When
#        called, that find_spec() method instantiates our beartype-specific
#        loader to do its internal work. Super non-trivial stuff. Okay. Anyways!
#        For our purposes, it looks like we'll need to:
#        * Call that "path_hook.find_spec()" method, which returns a module
#          spec. Note that this does *NOT* actually call the loader (and thus
#          does *NOT* actually import the module, thankfully): e.g.,
#              module_spec = path_hook.find_spec()
#        * Access the "module_spec.loader" instance variable. Note that the
#          previously called "path_hook.find_spec()" has instantiated this
#          variable to be a new third-party "SourceFileLoader" subclass
#          instance: e.g.,
#              loader_external = module_spec.loader
#        * If "loader_external" actually is a "SourceFileLoader" subclass... or,
#          maybe don't even bother checking? Probably doesn't matter, honestly.
#          Skip this check. *lolsighbro*
#        * If the passed module is one a user has *NOT* requested to be
#          beartyped, just call loader_external() directly and defer to whatever
#          it returns.
#        * Else, the passed module is one a user has requested to be beartyped.
#          Life intensifies even further:
#          * *TEMPORARILY MONKEY-PATCH* the core "ast.NodeTransformer"
#            superclass. Look. Just do it. Since the import lock exists, this is
#            about as safe as it possibly can be. I mean, we've already been
#            friggin' monkey-patching low-level "_bootstrap_externals"
#            functionality for a decade and... that's been totally fine. One
#            more monkey-patch hurts nothing, we insist!
#
#            Okay. So, the core idea here is that we monkey-patch a new
#            __getattribute__() dunder method into "ast.NodeTransformer". Note
#            that __getattribute__() commonly causes infinite recursion. Yeah.
#            Thankfully, it's trivial to circumvent by falling back to the root
#            object.__getattribute__() dunder method. Anways. This
#            __getattribute__() monkey-patch exists *ONLY* to intercept attempts
#            by third-party AST transforms to call the NodeTransformer.visit()
#            method. Ergo, that monkey-patch should:
#            * Detect if the passed name is "visit". If it is, return a new
#              *BEARTYPE-SPECIFIC* visit() method rather than either the default
#              NodeTransformer.visit() method *OR* the third-party
#              SomeCustomNodeTransformer.visit() method. Then our
#              _beartype_visit() monkey-patch should:
#              * *HMM*. Maybe _beartype_visit() should be a closure? If it is,
#                we can then safely define a new local local variable:
#                    # Define in the outer get_code() scope:
#                    is_beartype_ast_visited = False
#
#                    def _node_transformer_visit_beartype(module_ast: Node) -> Node:
#                        nonlocal is_beartype_ast_visited
#
#                        # This is needed to prevent @beartype from
#                        # inappropriately re-applying its AST transformer
#                        # multiple times for a single module. This edge case
#                        # arises if two or more third-party packages register
#                        # competing import hooks that also transform this AST
#                        # and thus call the NodeTransformer.visit() method two
#                        # or more times, once per such import hook.
#                        if not is_beartype_ast_visited:
#                            #FIXME: [SPEED] Attempt to cache this rather than
#                            #reinstantiating this object on each module import.
#                            # AST transformer decorating typed callables and classes by @beartype.
#                            ast_beartyper = BeartypeNodeTransformer(
#                                module_name=self._module_name, conf=self._module_conf)
#
#                            # Abstract syntax tree (AST) modified by this transformer.
#                            module_ast_beartyped = ast_beartyper.visit(module_ast)
#
#                            is_beartype_ast_visited = True
#
#                            return module_ast_beartyped
#
#                    node_transformer_visit_old = NodeTransformer.visit
#                    NodeTransformer.visit = _node_transformer_visit_beartype
#
#                    try:
#                        if not is_beartype_ast_visited:
#                            issue_warning('Ugh! Ugh, we say!')
#                    finally:
#                        NodeTransformer.visit = node_transformer_visit_old
#
#                We need this to decide whether this third-party path hook
#                actually did perform an AST transformation or not. If:
#                * It did, then our monkey-patch of that also performed an AST
#                  transformation and then compiled that transformation into the
#                  imported module's "__code__" object. Great.
#                * It didn't, then we're in trouble. No idea what to do in this
#                  case, honestly. The imported module's "__code__" object was
#                  already produced, but we never got a chance to transform it!
#                  Bad juju is afoot. At the least, we should:
#                  * Issue a *NEW* non-fatal warning advising the end user to
#                    submit a new issue to *OUR* tracker. We'll then need to add
#                    additionally blacklist whatever third-party package or
#                    module is responsible in the same way that we're
#                    blacklisting PyInstaller.
#                  * Actually, there's something *MUCH* better we can do here: a
#                    valid alternative that should work in the general case.
#                    This alternative has several disadvantages, however, and is
#                    thus (probably) only a last-ditch desperate fallback:
#                    * It requires an optional runtime dependency: "astor",
#                      whose popular astor.code_to_ast(codeobj) function does
#                      just this.
#                    * *WAIT*. "astor" is officially unmaintained, actually.
#                      What a shame. Thankfully, modern actively maintained
#                      alternatives exist... Oh, wait. They're all dead, too!
#                      Their names are "meta" (yeah, trash name obviously),
#                      "uncompyle6" (dead for lack of funding), and
#                      "decompile3" (dead for lack of funding). The likeliest
#                      to be resurrected is "decompile3", but see this madness:
#                          https://github.com/rocky/python-decompile3/issues/45
#                      Dude is kinda toxic, honestly. You don't do open source
#                      for the money. You do open source for the love. Oh, well!
#                    * Anyway. The idea here is obvious, right? Even though no
#                      actively maintained Python decompilers exist, if one
#                      *DID*, then we could just decompile the module "__code__"
#                      object returned by any arbitrary downstream path hook
#                      into its corresponding AST and then trivially transform
#                      that AST in the usual way. But... we can't do that,
#                      because no actively maintained Python decompilers exist.
#                  * That said, there is yet another possible alternative. By
#                    inspecting our own loader, we see that we call the public
#                    importlib.util.decode_source() function, which internally
#                    calls the private C-based
#                    io.IncrementalNewlineDecoder.decode() method. Tragically,
#                    that method is indeed C-based and thus *NOT* amenable to
#                    monkey-patching: e.g.,
#                        >>> from io import IncrementalNewlineDecoder as yum
#                        >>> yum.decode = lambda self, *args, **kwargs: print('lol')
#                        Traceback (most recent call last):
#                          File "<python-input-1>", line 1, in <module>
#                            yum.decode = lambda self, *args, **kwargs: print('lol')
#                            ^^^^^^^^^^
#                        TypeError: cannot set 'decode' attribute of immutable type '_io.IncrementalNewlineDecoder'.
#                    Too bad you can't monkey-patch that, huh? Would've been a
#                    great viable alternative.
#                  * *WAIT*. Now, this is getting intense. But... it might
#                    ultimately be the best option on the table. We can't
#                    directly monkey-patch decode_source(), because third-party
#                    packages have already imported that at global scope. But
#                    what we *CAN* do is monkey-patch the
#                    "decode_source.__code__" object. Yup. Apparently, that
#                    works just fine:
#                        https://stackoverflow.com/a/54650413/2809027
#                    That said, it's unclear whether this is worthwhile. Do any
#                    competing import hooks call decode_source() but *NOT*
#                    NodeTransformer.visit()? No idea. For now, let's just run
#                    with our NodeTransformer.visit() monkey-patch. *shrug*
#            * Else, fallback to calling object.__getattribute__() for safety.
#
#The rest of the gameplan is boring, but also the most important public-facing
#part of all this shadow madness:
#* First, define a new "BeartypeClawPathHookPlace" enumeration inside the
#  existing "beartype._conf.confenum" submodule. The definition should resemble:
#      @die_unless_enum_member_values_unique
#      class BeartypeClawPathHookPlace(Enum):
#          FIRST = next_enum_member_value()
#          LAST_BEFORE_STANDARD_PATH_HOOK = next_enum_member_value()
#
#  This enumeration should initially define these two members:
#  * "LAST_BEFORE_STANDARD_PATH_HOOK", the current conservation approach in
#    which we cautiously inject the beartype-specific file finder path hook
#    immediately before the beartype-agnostic file finder path hook.
#    Technically, this works. Pragmatically, the existence of typeguard and
#    jaxtyping means this no longer works. Ergo, *THIS SHOULD NO LONGER BE THE
#    DEFAULT*. Nonetheless, something *COULD* (but hopefully won't) go wrong
#    with our new aggressive strategies. Ergo, we should still preserve this as
#    an option for users who find our new aggressive defaults to be problematic.
#  * "FIRST", our new approach. When this member is enabled, beartype will:
#    * Unsurprisingly, forcefully inject itself as the first item of the
#      "sys.path_hooks" list. Don't worry. We'll see shortly that this is safe.
#      Actually:
#      * PyInstaller's path hook is obviously unsafe. Others probably are, too.
#        We want to inject our path hook *AFTER* PyInstaller's to avoid breaking
#        this common use case that we already know to be broken. Maybe we want
#        to rename "FIRST" to "FIRST_AFTER_CLAW_HOSTILE" in keeping with our
#        existing "LAST_BEFORE_DECOR_HOSTILE" enum member defined elsewhere.
#        Yeah. Makes sense, really.
#    * Surprisingly, forcefully replace the entire "sys.path_hooks" instance of
#      the "list" builtin with a new instance of a new beartype-specific
#      "BeartypePathHooks" list subclass. This subclass prevents third-party
#      packages or modules that attempt to insert competing import hooks to the
#      front of "sys.path_hooks" *AFTER* "beartype.claw" import hooks have
#      already inserted the beartype-specific path hook to the front of that
#      list from doing so:
#          class BeartypePathHooks(list):
#              def insert(self, index: int, item: object) -> None:
#
#                  #FIXME: Obviously not *QUITE* right, because of PyInstaller
#                  #and possibly other "beartype.claw"-hostile import hooks at
#                  #the front of "sys.path_hooks". This is *ALMOST* right,
#                  #though. Isn't that good enough!?
#
#                  # Prevent third-party packages or modules from forcefully
#                  # deprioritizing the beartype-specific path hook. Instead,
#                  # deprioritize the passed third-party path hook in favour of
#                  # the existing beartype-specific path hook already occupying
#                  # the front of this list.
#                  if index == 0:
#                      index = 1
#
#                  super().insert(index, item)
#* Next, add a new "claw_path_hook_place: BeartypeClawPathHookPlace =
#  BeartypeClawPathHookPlace.FIRST" configuration option to "BeartypeConf". Note
#  in the docstring that, unlike most options, this option is purely
#  first-come-first-served. That is, the first registration of a "beartype.claw"
#  import hook by a package dictates the policy for the remainder of the active
#  Python interpreter (basically).
#* Improve the add_beartype_path_hook() adder as follows:
#  * Add a new mandatory "conf: BeartypeConf" parameter, please. *sigh*
#  * *INSIDE* the entire if checking whether "if claw_state.beartype_path_hook is
#    None:", add a new if checking whether "conf.claw_path_hook_place is
#    BeartypeClawPathHookPlace.FIRST". Since that's the new default, it pretty
#    much *ALWAYS* will be. When that's the case:
#    * Instantiate a "BeartypeSourceFileLoaderAggressive"-oriented rather than
#      "BeartypeSourceFileLoaderPassive"-oriented path hook factory. Yet another
#      thing to spec out, obviously. Trivial. Just annoying. Urgh!
#  * *AFTER* the entire if checking whether "if claw_state.beartype_path_hook is
#    None:", add a new if checking whether "conf.claw_path_hook_place is
#    BeartypeClawPathHookPlace.FIRST". Since that's the new default, it pretty
#    much *ALWAYS* will be. When that's the case:
#    * Guard against future misbehaviour by forcefully replacing the entire
#      "sys.path_hooks" instance of the "list" builtin with a new instance of a
#      new beartype-specific "BeartypePathHooks" list subclass, as above. Note
#      here that "_bootstrap_external" claims that "sys.path_hooks" can be weird
#      (e.g., "None"), and that that's totally okay:
#          if sys.path_hooks is not None and not sys.path_hooks:
#              _warnings.warn('sys.path_hooks is empty', ImportWarning)
#
#      In other words, we'll need to explicitly check whether "sys.path_hooks is
#      None" and, if so, simply instantiate a 1-"BeartypePathHooks" containing
#      only our path hook. *WHATEVAHS*. /shrug/
#* Unit test up "LAST_BEFORE_STANDARD_PATH_HOOK", now that that's no longer the
#  default.
#FIXME: [PYINSTALLER] Let's issue a *MUCH* more succinct warning if we detect
#PyInstaller. There's no confusion here. PyInstaller is ignoring third-party
#path hooks and thus PEP 302-noncompliant. Suggest users shout about this on the
#PyInstaller issue tracker. Should be trivial to detect. Just look for
#"PyiFrozenFinder" (or whatevahs) on the current "sys.path_hooks" list.
#
#When we do, resurrect our existing unit test that we've currently disabled.

#FIXME: [JAXTYPING] Is jaxtyping configurable? Probably. If not, though,
#beartype should probably begin automatically:
#* Detect whether the currently decorated callable is annotated by one or more
#  "jaxtyping"-specific type hints. They're probably not too hard to detect.
#  Searching for substrings in the usual "repr(hint)" output might get us there.
#* If so, automatically decorate this callable with "jaxtyping".
#
#On the other hand, if jaxtyping *IS* configurable, the above is insufficient.
#Our current approach is then obviously preferable.
#
#Either way, the core issue remains: jaxtyping's import hooks automatically
#apply the @beartype decorator! That's... not great. Why? Because beartype is
#*DEFINITELY* configurable. The @beartype decorator automatically applied by
#jaxtyping's import hooks assumes the default configuration (rather than the
#"conf" the current user passed to beartype_this_package()), which is simply
#wrong in many cases. Ergo, either:
#* Beartype should *DEFINITELY* try to:
#  * Detect when the caller has registered a jaxtyping import hook with
#    @beartype as jaxtyping's default type-checker.
#  * Issue a non-fatal warning suggesting that that is a bad idea and that
#    jaxtyping's import hooks should instead be explicitly configured with
#    "checker=None" (or whatevahs).
#* Jaxtyping itself should just stop doing that. Pretty sure if we beg hard
#  enough on their issue tracker that they might even deprecate that beartype
#  integration. Might. Maybe. We are tired, fam. *sigh*
#
#*WAIT*. Maybe that's not an issue after all... So long as beartype applies its
#AST transform *BEFORE* jaxtyping, the @beartype decorator subsequently applied
#by jaxtyping will just be redundant and thus silently noop in beartype itself.
#Makes sense. Probably not an issue then. \o/

#FIXME: [PYINSTALLER] Internal commentary in the PyInstaller codebase suggest
#that PyInstaller's PyiFrozenFinder.fallback_finder() property is what's
#conflicting with our beartype-specific file finder path hook. Ideally, that
#property should be returning our beartype-specific file finder path hook. It
#isn't -- presumably because "self.path_hook" is literally just the
#PyiFrozenFinder.path_hook() class method. None of that code makes sense,
#honestly. Why is PyiFrozenFinder.fallback_finder() searching through
#"sys.path_hooks" just to return its own PyiFrozenFinder.path_hook() class
#method? No idea. *WHATEVAHS*. It's clear that PyInstaller is PEP
#302-noncompliant in the sense that PyInstaller basically just ignores
#everything on "sys.path_hooks" in favour of itself. We should probably open up
#a discussion on the PyInstaller issue tracker about this, because it implies
#that PyInstaller is also incompatible with jaxtyping and typeguard import
#hooks, which... means literally all runtime type-checking. Jeeeeez.

# ....................{ IMPORTS                            }....................
# Intentionally import the root "sys" module rather than attributes of that
# module (e.g., "meta_path", "path_hooks") to account for malicious third-party
# packages that reassign those attributes rather than modifying their contents.
import sys

from beartype.roar import BeartypeClawImportlibFileFinderPathHookInactiveWarning
from beartype.roar._roarexc import (
    _BeartypeClawImportlibIsPathHookActiveException)
from beartype.claw._importlib._clawimpfilefinder import (
    is_beartype_file_finder_path_hook,
    make_beartype_file_finder_path_hook_index,
)
from beartype._data.claw.dataclawmagic import (
    STANDARD_META_PATH_ITEM_NAMES,
    STANDARD_PATH_HOOKS_ITEM_NAMES,
)
from beartype._metaverse import URL_ISSUES
from beartype._util.error.utilerrwarn import issue_warning
from beartype._util.kind.maplike.utilmaptest import is_mapping_keys_any
from beartype._util.text.utiltextjoin import join_strings_bulleted_unnumbered
from beartype._util.utilobjget import get_object_name
from importlib import invalidate_caches

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
        sys.path_hooks.insert(path_hook_index, path_hook)

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
    sys.path_hooks.remove(claw_state.beartype_path_hook)

    # Allow subsequent calls of the add_beartype_path_hook() function to re-add
    # a new instance of this path hook immediately *AFTER* successfully removing
    # the first such path hook.
    claw_state.beartype_path_hook = None

    # Allow subsequent calls of the _warn_if_beartype_pathhook_inactive()
    # function to re-issue the non-fatal warning previously issued by that
    # function (if any).
    claw_state.is_warned_if_beartype_path_hook_inactive = False

    # Lastly, clear *ALL* import path hook caches for safety.
    _clear_importlib_caches()

# ....................{ PRIVATE ~ globals                  }....................
_WARN_BLACKLIST_PACKAGE_NAMES = frozenset(('jaxtyping', 'typeguard',))
'''
Frozen set of the fully-qualified names of all **warning-blacklisted third-party
packages** (i.e., packages well-known to aggressively add competing import hooks
to the front of the global :obj:`sys.path_hooks` list, resulting in
:mod:`beartype.claw` import hooks being silently ignored).

The :func:`._warn_if_beartype_pathhook_inactive` function silently reduces to a
noop if *any* of these packages have already been imported under the active
Python interpreter. Since their import hooks are already well-known to disable
ours, issuing warnings to users only uselessly annoys users without contributing
any useful solutions in recompense.
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

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype.claw._clawstate import claw_state

    # ....................{ NOOP                           }....................
    # If this function has already issued this warning...
    if claw_state.is_warned_if_beartype_path_hook_inactive:
        # Then avoid doing so again. This warning is verbose and thus likely to
        # incite anger in users. We know. Instead, silently reduce to a noop.
        return
    # Else, this function has *NOT* already issued this warning.
    #
    # If the global "sys.modules" dictionary contains the fully-qualified names
    # of one or more warning-blacklisted third-party package as keys, one or
    # more such packages have been imported. In this case, silently reduce to a
    # noop. Why? Because the competing import hooks published by these packages
    # are already well-known to "accidentally" disable "beartype.claw" import
    # hooks. Issuing warnings to users would only uselessly annoy users without
    # contributing any useful solutions in recompense.
    elif is_mapping_keys_any(
        mapping=sys.modules, keys=_WARN_BLACKLIST_PACKAGE_NAMES):
        return
    # Else, the global "sys.modules" dictionary contains the fully-qualified
    # names of *NO* warning-blacklisted third-party package as keys.

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

    # ....................{ GLOBALs                        }....................
    # Record that this function has now issued this warning, preventing
    # subsequent calls from uselessly doing so again.
    #
    # Note that we intentionally assign this global early rather than late
    # (i.e., after calling the issue_warning() function below). Why? To reduce
    # the likelihood of issuing this warning multiple times in the event that
    # the caller fails to call this function from a thread-safe context. That
    # should never happen. Since assigning this global early is trivial,
    # however, we do so to avoid suffering in both users and in us. No pain!
    claw_state.is_warned_if_beartype_path_hook_inactive = True

    # ....................{ LOCALS                         }....................
    # List of the fully-qualified names of all competing meta path hooks on the
    # global "sys.meta_path" list defined by third-party packages or modules,
    # iteratively appended to by the iteration performed below.
    hook_custom_names_list = []

    # ....................{ META PATH                      }....................
    # For each meta path hook registered in the global "sys.meta_path" list...
    for meta_path_hook in sys.meta_path:
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
            hook_custom_names_list.append(
                f'"{meta_path_hook_name}" on "sys.meta_path"')
        # Else, fully-qualified name of this meta path hook is that of a
        # standard meta path hook. In this case, silently ignore this meta path
        # hook and continue to the next.

    # ....................{ PATH HOOKS                     }....................
    # For each path hook registered in the global "sys.path_hooks" list...
    for path_hook in sys.path_hooks:
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
            if is_beartype_file_finder_path_hook(path_hook):
                break
            # Else, this path hook is *NOT* the beartype-specific file finder
            # path hook. This hook precedes that hook and *COULD* thus be the
            # culprit responsible for inactivating that hook.

            # Append this name to this list.
            hook_custom_names_list.append(
                f'"{path_hook_name}" on "sys.path_hooks"')
        # Else, fully-qualified name of this path hook is that of a standard
        # path hook. In this case, silently ignore this path hook and continue
        # to the next.

    # Bullet point-delimited string listing the fully-qualified names of all
    # competing import hooks on either the global "sys.meta_path" *OR*
    # "sys.path_hooks" lists defined by third-party packages or modules.
    hook_custom_names = join_strings_bulleted_unnumbered(hook_custom_names_list)

    # ....................{ MESSAGE                        }....................
    # Warning message to be issued below.
    warning_message = (
        f'"beartype.claw" import hooks erroneously disabled by '
        f'competing third-party import hooks, '
        f'preventing beartype from automatically type-checking '
        f'packages and modules in this app stack. '
        f"This is mostly Python's fault. "
        f'Python lacks standards governing import hook interoperability. '
        f"The import hook ecosystem is "
        f'an unscoped feeding frenzy of '
        f'lawless piranhas digesting '
        f"Python's last shred of dignity. "
        f'Competing third-party import hooks include:'
        f'{hook_custom_names if hook_custom_names else "* No idea, yo. Something went horribly wrong. Ugh!"}\n'
        f'You now have three unpleasant options. Either:\n'
        f'* [DESPERATION MOVE] Globally silence this warning by adding to '
        f'your top-level "{{your_package}}.__init__" submodule:\n'
        f'\tfrom beartype.roar import BeartypeClawImportlibFileFinderPathHookInactiveWarning\n'
        f'\tfrom warnings import filterwarnings\n'
        f'\tfilterwarnings(action="ignore", category=BeartypeClawImportlibFileFinderPathHookInactiveWarning)\n'
        f'* [RECOMMENDED] Submit an issue to the issue tracker of '
        f'the competing third-party import hook listed above responsible for '
        f'ignoring "beartype.claw" import hooks. '
        f'Good luck identifying the culprit. '
        f'Request they improve the compatibility of '
        f'their import hook with '
        f'other PEP 302-compliant import hooks registered by '
        f'other frameworks -- especially those registered by "beartype.claw". '
        f'Ping @leycec (i.e., @beartype maintainer bald guy) on '
        f'all relevant issues so he can '
        f'nod respectfully and pretend to render assistance.\n'
        f'* [NOT RECOMMENDED] Complain about other people on '
        f"@beartype's issue tracker. "
        f'Like in real life, this is usually useless. '
        f'There is probably nothing @beartype can do. '
        f'We cannot force others to improve the interoperability '
        f'of their incompatible import hooks. '
        f'We can only heckle them with animated GIFs. '
        f'Do this only if you want us to heckle somebody '
        f'with animated GIFs:\n'
        f'\t{URL_ISSUES}'
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
    sys.path_importer_cache.clear()

    # Clear *ALL* "importlib" caches as well for safety.
    invalidate_caches()
