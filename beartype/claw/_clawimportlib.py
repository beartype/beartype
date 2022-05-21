#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype all-at-once high-level** :mod:`importlib` **machinery.**

This private submodule is the main entry point for this subpackage, defining the
public-facing :func:`beartype_submodules_on_import` function registering new
beartype import path hooks. Notably, this submodule integrates high-level
:mod:`importlib` machinery required to implement :pep:`302`- and
:pep:`451`-compliant import hooks with the low-level abstract syntax tree (AST)
transformation defined by the low-level :mod:`beartype.claw._clawast` submodule.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: The New Five-Year Plan 2.0 is to avoid all interaction with the
#higher-level "sys.meta_path" mechanism entirely. Why? Because pytest leverages
#that some mechanism for its assertion rewriting. Do we care? *WE CARE,*
#especially because there appears to be no sensible means of portably stacking
#our own "MetaPathFinder" (...or whatever) on top of pytest's. Instead, we note
#the existence of the much less commonly used (but ultimately significantly
#safer) lower-level "sys.path_hooks" mechanism. Fascinatingly, AST transforms
#can be implemented by leveraging either. For some reason, everyone *ONLY*
#leverages the former to transform ASTs. Let's break that trend by instead
#leveraging the latter to transform ASTs. Specifically:
#* First, define a new private "_BeartypeSourceLoader(SourceFileLoader)" class
#  strongly inspired by the *SECOND* example of this exemplary StackOverflow
#  answer, which is probably the definitive statement on the subject:
#  https://stackoverflow.com/a/43573798/2809027
#  Note the use of the concrete "SourceFileLoader" superclass rather than the
#  less concrete "FileLoader" superclass. Since both typeguard and ideas
#  explicitly test for "SourceFileLoader" instances, it's almost certain that
#  that's what we require as well.
#  The disadvantage of this approach is that it fails to generalize to embedded
#  Python modules (e.g., in frozen archives or zip files). Of course, *SO DOES*
#  what "typeguard" and "ideas" are both doing and no one particularly seems to
#  care there, right? This approach is thus still generally robust enough to
#  suffice for a first pass.
#  After getting this simplistic approach working, let's then fully invest in
#  exhaustively testing that this approach successfully:
#  * Directly decorates callables declared at:
#    * Global scope in an on-disk top-level non-package module embedded in our
#      test suite.
#    * Class scope in the same module.
#    * Closure scope in the same module.
#  * Recursively decorates all callables declared by submodules of an on-disk
#    top-level package.
#  * Does *NOT* conflict with pytest's assertion rewriting mechanism. This will
#    be non-trivial. Can we isolate another pytest process within the main
#    currently running pytest process? O_o
#* Next, generalize that class to support stacking. What? Okay, so the core
#  issue with the prior approach is that it only works with standard Python
#  modules defined as standard files in standard directories. This assumption
#  breaks down for Python modules embedded within other files (e.g., as frozen
#  archives or zip files). The key insight here is given by Iguananaut in this
#  StackOverflow answer:
#    https://stackoverflow.com/a/48671982/2809027
#  This approach "...installs a special hook in sys.path_hooks that acts almost
#  as a sort of middle-ware between the PathFinder in sys.meta_path, and the
#  hooks in sys.path_hooks where, rather than just using the first hook that
#  says 'I can handle this path!' it tries all matching hooks in order, until it
#  finds one that actually returns a useful ModuleSpec from its find_spec
#  method."
#  Note that "hooks" in "sys.path_hooks" are actually *FACTORY FUNCTIONS*,
#  typically defined by calling the FileFinder.path_hook() class method.
#  We're unclear whether we want a full "ModuleSpec," however. It seems
#  preferable to merely search for a working hook in "sys.path_hooks" that
#  applies to the path. Additionally, if that hook defines a get_source() method
#  *AND* that method returns a non-empty string (i.e., that is neither "None"
#  *NOR* the empty string), then we want to munge that string with our AST
#  transformation. The advantages of this approach are multitude:
#  * This approach supports pytest, unlike standard "meta_path" approaches.
#  * This approach supports embedded files, unlike the first approach above. In
#    particular, note that the standard
#    "zipimporter.zipimporter(_bootstrap_external._LoaderBasics)" class for
#    loading Python modules from arbitrary zip files does *NOT* subclass any of
#    the standard superclasses you might expect it to (e.g.,
#    "importlib.machinery.SourceFileLoader"). Ergo, a simple inheritance check
#    fails to suffice. Thankfully, that class *DOES* define a get_source()
#    method resembling that of SourceFileLoader.get_source().
#FIXME: I've confirmed by deep inspection of both the standard "importlib"
#package and the third-party "_pytest.assertion.rewrite" subpackage that the
#above should (but possible does *NOT*) suffice to properly integrate with
#pytest. Notably, the
#_pytest.assertion.rewrite.AssertionRewritingHook.find_spec() class method
#improperly overwrites the "importlib._bootstrap.ModuleSpec.loader" instance
#variable with *ITSELF* here:
#
#    class AssertionRewritingHook(importlib.abc.MetaPathFinder, importlib.abc.Loader):
#        ...
#
#        _find_spec = importlib.machinery.PathFinder.find_spec
#
#        def find_spec(
#            self,
#            name: str,
#            path: Optional[Sequence[Union[str, bytes]]] = None,
#            target: Optional[types.ModuleType] = None,
#        ) -> Optional[importlib.machinery.ModuleSpec]:
#            ...
#
#            # *SO FAR, SO GOOD.* The "spec.loader" instance variable now refers
#            # to an instance of our custom "SourceFileLoader" subclass.
#            spec = self._find_spec(name, path)  # type: ignore
#            ...
#
#            # *EVEN BETTER.* This might save us. See below.
#            if not self._should_rewrite(name, fn, state):
#                return None
#
#            # And... everything goes to Heck right here. Passing "loader=self"
#            # completely replaces the loader that Python just helpfully
#            # provided with this "AssertionRewritingHook" instance, which is
#            # all manner of wrong.
#            return importlib.util.spec_from_file_location(
#                name,
#                fn,
#                loader=self,  # <-- *THIS IS THE PROBLEM, BRO.*
#                submodule_search_locations=spec.submodule_search_locations,
#            )
#
#Ultimately, it's no surprise whatsoever that this brute-force behaviour from
#pytest conflicts with everyone else in the Python ecosystem. That said, this
#might still not be an issue. Why? Because the call to self._should_rewrite()
#*SHOULD* cause "AssertionRewritingHook" to silently reduce to a noop for
#anything that beartype would care about.
#
#If true (which it should be), the above approach *SHOULD* still actually work.
#So why does pytest conflict with other AST transformation approaches? Because
#those other approaches also leverage "sys.meta_path" machinery, typically by
#forcefully prepending their own "MetaPathFinder" instance onto "sys.meta_path",
#which silently overwrites pytest's "MetaPathFinder" instance. Since we're *NOT*
#doing that, we should be fine with our approach. *sweat beads brow*

#FIXME: Improve module docstring, please.

# ....................{ IMPORTS                            }....................
from ast import (
    PyCF_ONLY_AST,
    fix_missing_locations,
)
from beartype.claw._clawast import _BeartypeNodeTransformer
from beartype.claw._clawpackagenames import (
    is_packages_registered,
    register_packages,
)
from beartype.roar import BeartypeClawRegistrationException
from beartype.typing import (
    Iterable,
    Optional,
)
from beartype._conf import BeartypeConf
from beartype._util.func.utilfunccodeobj import (
    FUNC_CODEOBJ_NAME_MODULE,
    get_func_codeobj,
)
from beartype._util.func.utilfuncframe import get_frame
from importlib import (  # type: ignore[attr-defined]
    _bootstrap_external,
    invalidate_caches,
)
from importlib.machinery import (
    SOURCE_SUFFIXES,
    FileFinder,
    SourceFileLoader,
)
from importlib.util import (
    decode_source,
)
from sys import (
    path_hooks,
    path_importer_cache,
)
from threading import RLock
from types import (
    CodeType,
    FrameType,
)

# Original cache_from_source() function defined by the private (*gulp*)
# "importlib._bootstrap_external" submodule, preserved *BEFORE* temporarily
# replacing that function with our beartype-specific variant below.
from importlib.util import cache_from_source as cache_from_source_original

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ HOOKS                              }....................
#FIXME: Unit test us up, please.
def beartype_submodules_on_import(
    # Optional parameters.
    package_names: Optional[Iterable[str]] = None,

    # Optional keyword-only parameters.
    *,
    conf: BeartypeConf = BeartypeConf(),
) -> None:
    '''
    Register a new **beartype import path hook** (i.e., callable inserted to the
    front of the standard :mod:`sys.path_hooks` list recursively applying the
    :func:`beartype.beartype` decorator to all well-typed callables and classes
    defined by all submodules of all packages with the passed names on the first
    importation of those submodules).

    Parameters
    ----------
    package_names : Optional[Iterable[str]]
        Iterable of the fully-qualified names of one or more packages to be
        type-checked by :func:`beartype.beartype`. Defaults to ``None``, in
        which case this parameter defaults to a 1-tuple containing only the
        fully-qualified name of the **calling package** (i.e., external parent
        package of the submodule directly calling this function).
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object). Defaults
        to ``BeartypeConf()``, the default ``O(1)`` constant-time configuration.

    Raises
    ----------
    BeartypeClawRegistrationException
        If either:

        * The passed ``package_names`` parameter is either:

          * *Not* iterable (i.e., fails to satisfy the
            :class:`collections.abc.Iterable` protocol).
          * An empty iterable.
          * A non-empty iterable containing at least one item that is either:

            * *Not* a string.
            * The empty string.
            * A non-empty string that is *not* a valid **package name** (i.e.,
              ``"."``-delimited concatenation of valid Python identifiers).

        * The passed ``conf`` parameter is *not* a beartype configuration (i.e.,
          :class:`BeartypeConf` instance).

    See Also
    ----------
    https://stackoverflow.com/a/43573798/2809027
        StackOverflow answer strongly inspiring the low-level implementation of
        this function with respect to inscrutable :mod:`importlib` machinery.
    '''

    # ..................{ PACKAGE NAMES                      }..................
    # Note the following logic *CANNOT* reasonably be isolated to a new
    # private helper function. Why? Because this logic itself calls existing
    # private helper functions assuming the caller to be at the expected
    # position on the current call stack.
    if package_names is None:
        #FIXME: *UNSAFE.* get_frame() raises a "ValueError" exception if
        #passed a non-existent frame, which is non-ideal: e.g.,
        #    >>> sys._getframe(20)
        #    ValueError: call stack is not deep enough
        #Since beartype_on_import() is public, that function can
        #technically be called directly from a REPL. When it is, a
        #human-readable exception should be raised instead. Notably, we
        #instead want to:
        #* Define new utilfuncframe getters resembling:
        #      def get_frame_or_none(ignore_frames: int) -> Optional[FrameType]:
        #          try:
        #              return get_frame(ignore_frames + 1)
        #          except ValueError:
        #              return None
        #      def get_frame_caller_or_none() -> Optional[FrameType]:
        #          return get_frame_or_none(2)
        #* Import "get_frame_caller_or_none" above.
        #* Refactor this logic here to resemble:
        #      frame_caller = get_frame_caller_or_none()
        #      if frame_caller is None:
        #          raise BeartypeClawRegistrationException(
        #              'beartype_submodules_on_import() '
        #              'not callable directly from REPL scope.'
        #          )
        frame_caller: FrameType = get_frame(1)  # type: ignore[assignment,misc]

        # Code object underlying the caller if that caller is pure-Python *OR*
        # raise an exception otherwise (i.e., if that caller is C-based).
        frame_caller_codeobj = get_func_codeobj(frame_caller)

        # Unqualified basename of that caller.
        frame_caller_basename = frame_caller_codeobj.co_name

        # Fully-qualified name of the module defining that caller.
        frame_caller_module_name = frame_caller.f_globals['__name__']

        #FIXME: Relax this constraint, please. Just iteratively search up the
        #call stack with iter_frames() until stumbling into a frame satisfying
        #this condition.
        # If that name is *NOT* the placeholder string assigned by the active
        # Python interpreter to all scopes encapsulating the top-most lexical
        # scope of a module in the current call stack, the caller is a class or
        # callable rather than a module. In this case, raise an exception.
        if frame_caller_basename != FUNC_CODEOBJ_NAME_MODULE:
            raise BeartypeClawRegistrationException(
                f'beartype_submodules_on_import() '
                f'neither passed "package_names" nor called from module scope '
                f'(i.e., caller scope '
                f'"{frame_caller_module_name}.{frame_caller_basename}" '
                f'either class or callable). '
                f'Please either pass "package_names" or '
                f'call this function from module scope.'
            )

        # If the fully-qualified name of the module defining that caller
        # contains *NO* delimiters, that module is a top-level module defined by
        # *NO* parent package. In this case, raise an exception. Why? Because
        # this function uselessly and silently reduces to a noop when called by
        # a top-level module. Why? Because this function registers an import
        # hook applicable only to subsequently imported submodules of the passed
        # packages. By definition, a top-level module is *NOT* a package and
        # thus has *NO* submodules. To prevent confusion, notify the user here.
        #
        # Note this is constraint is also implicitly imposed by the subsequent
        # call to the frame_caller_module_name.rpartition() method: e.g.,
        #     >>> frame_caller_module_name = 'muh_module'
        #     >>> frame_caller_module_name.rpartition()
        #     ('', '', 'muh_module')  # <-- we're now in trouble, folks
        if '.' not in frame_caller_module_name:
            raise BeartypeClawRegistrationException(
                f'beartype_submodules_on_import() '
                f'neither passed "package_names" nor called by a submodule '
                f'(i.e., caller module "{frame_caller_module_name}" '
                f'defined by no parent package).'
            )
        # Else, that module is a submodule of some parent package.

        # Fully-qualified name of the parent package defining that submodule,
        # parsed from the name of that submodule via this standard idiom:
        #     >>> frame_caller_module_name = 'muh_package.muh_module'
        #     >>> frame_caller_module_name.rpartition()
        #     ('muh_package', '.', 'muh_module')
        frame_caller_package_name = frame_caller_module_name.rpartition()[0]

        # Default this iterable to the 1-tuple referencing only this package.
        package_names = (frame_caller_package_name,)

    # ..................{ PATH HOOK                          }..................
    # With a submodule-specific thread-safe reentrant lock...
    with _claw_lock:
        # True only if the beartype import path hook subsequently added below
        # has already been added by a prior call to this function under the
        # active Python interpreter.
        #
        # Technically, this condition is also decidable by an iterative search
        # over the "sys.path_hooks" list for an item that is an instance of our
        # private "_BeartypeSourceFileLoader" subclass. However, doing so would
        # impose O(n) time complexity for "n" the size of that list,
        #
        # Pragmatically, this condition is trivially decidable by noting that:
        # * This public function performs the *ONLY* call to the private
        #   register_packages() function in this codebase.
        # * The first call of this function under the active Python interpreter:
        #   * Also performs the first call of the register_packages() function.
        #   * Also adds our beartype import path hook.
        #
        # Ergo, deciding this state in O(1) time complexity reduces to deciding
        # whether the register_packages() function has been called already.
        is_path_hook_added = is_packages_registered()

        # Register these packages for subsequent lookup during submodule
        # importation by the beartype import path hook registered below *AFTER*
        # deciding whether this function has been called already.
        #
        # Note this helper function fully validates these parameters. Ergo, we
        # intentionally avoid doing so here in this higher-level function.
        register_packages(package_names=package_names, conf=conf)

        # True only if the beartype import path hook subsequently added below
        # has already been added by a prior call to this function under the
        # active Python interpreter.
        if not is_path_hook_added:
            _add_path_hook()


def _add_path_hook() -> None:
    '''
    Add a new **beartype import path hook** (i.e., callable inserted to the
    front of the standard :mod:`sys.path_hooks` list recursively applying the
    :func:`beartype.beartype` decorator to all well-typed callables and classes
    defined by all submodules of all packages with the passed names on the first
    importation of those submodules).
    '''

    # 2-tuple of the undocumented format expected by the FileFinder.path_hook()
    # class method called below, associating our beartype-specific source file
    # loader with the platform-specific filetypes of all sourceful Python
    # packages and modules. We didn't do it. Don't blame the bear.
    LOADER_DETAILS = (_BeartypeSourceFileLoader, SOURCE_SUFFIXES)

    # Closure instantiating a new "FileFinder" instance invoking this loader.
    #
    # Note that we intentionally ignore mypy complaints here. Why? Because mypy
    # erroneously believes this method accepts 2-tuples whose first items are
    # loader *INSTANCES* (e.g., "Tuple[Loader, List[str]]"). In fact, this
    # method accepts 2-tuples whose first items are loader *TYPES* (e.g.,
    # "Tuple[Type[Loader], List[str]]"). This is why we can't have nice.
    loader_factory = FileFinder.path_hook(LOADER_DETAILS)  # type: ignore[arg-type]

    # Prepend a new import hook (i.e., factory closure encapsulating this
    # loader) *BEFORE* all other import hooks.
    path_hooks.insert(0, loader_factory)

    # Uncache *ALL* competing loaders cached by prior importations. Just do it!
    path_importer_cache.clear()
    invalidate_caches()

# ....................{ PRIVATE ~ classes                  }....................
#FIXME: *PROBABLY INSUFFICIENT.* For safety, we really only want to apply this
#loader to packages in the passed "package_names" list. For all other packages,
#the relevant method of this loader (which is probably find_spec(), but let's
#research that further) should return "None". Doing so defers loading to the
#next loader in "sys.path_hooks".
#FIXME: Unit test us up, please.
class _BeartypeSourceFileLoader(SourceFileLoader):
    '''
    **Beartype source file loader** implementing :mod:`importlib` machinery
    loading a **sourceful Python package or module** (i.e., package or module
    backed by a ``.py``-suffixed source file) into a **module spec** (i.e.,
    in-memory :class:`importlib._bootstrap.ModuleSpec` instance describing the
    importation of that package or module, complete with a reference back to
    this originating loader).

    The :func:`beartype_package` function injects a low-level **import path
    hook** (i.e., factory closure instantiating this class as an item of the
    standard :mod:`sys.path_hooks` list) to the front of that list. When called
    by a higher-level parent **import metapath hook** (i.e., object suitable for
    use as an item of the standard :mod:`sys.meta_path` list), that closure:

    #. Instantiates one instance of this class for each **imported Python
       package or module** (i.e., package or module on the standard
       :mod:`sys.path` list).
    #. Adds a new key-value pair to the standard :mod:`sys.path_importer_cache`
       dictionary, whose:

       * Key is the package of that module.
       * Value is that instance of this class.

    See Also
    ----------
    * The `comparable "typeguard.importhook" submodule <typeguard import
      hook_>`__ implemented by the incomparable `@agronholm (Alex Grönholm)
      <agronholm_>`__, whose intrepid solutions strongly inspired this
      subpackage. `Typeguard's import hook infrastructure <typeguard import
      hook_>`__ is a significant improvement over the prior state of the art in
      Python and a genuine marvel of concise, elegant, and portable abstract
      syntax tree (AST) transformation.

    .. _agronholm:
       https://github.com/agronholm
    .. _typeguard import hook:
       https://github.com/agronholm/typeguard/blob/master/src/typeguard/importhook.py
    '''

    # ..................{ API                                }..................
    #FIXME: We also need to also:
    #* Define the find_spec() method, which should:
    #  * Efficiently test whether the passed "path" is in "_package_names" in a
    #    *THREAD-SAFE MANNER.*
    #  * If not, this method should reduce to a noop by returning "None".
    #  * Else, this method should return the value of calling the superclass
    #    find_spec() implementation.
    #  We're fairly certain that suffices. Nonetheless, verify this by
    #  inspecting the comparable find_spec() implementation at:
    #      https://stackoverflow.com/a/48671982/2809027

    # Note that we explicitly ignore mypy override complaints here. For unknown
    # reasons, mypy believes that "importlib.machinery.SourceFileLoader"
    # subclasses comply with the "importlib.abc.InspectLoader" abstract base
    # class (ABC). Naturally, that is *NOT* the case. Ergo, we entirely ignore
    # mypy complaints here with respect to signature matching.
    def source_to_code(  # type: ignore[override]
        self,

        # Mandatory parameters.
        data: bytes,
        path: str,

        # Optional keyword-only parameters.
        *,
        _optimize: int =-1,
    ) -> CodeType:
        '''
        Code object dynamically compiled from the **sourceful Python package or
        module** (i.e., package or module backed by a ``.py``-suffixed source
        file) with the passed undecoded contents and filename, efficiently
        transformed in-place by our abstract syntax tree (AST) transformation
        automatically applying the :func:`beartype.beartype` decorator to all
        applicable objects of that package or module.

        Parameters
        ----------
        data : bytes
            **Byte array** (i.e., undecoded list of bytes) of the Python package
            or module to be decoded and dynamically compiled into a code object.
        path : str
            Absolute or relative filename of that Python package or module.
        _optimize : int, optional
            **Optimization level** (i.e., numeric integer signifying increasing
            levels of optimization under which to compile that Python package or
            module). Defaults to -1, implying the current interpreter-wide
            optimization level with which the active Python process was
            initially invoked (e.g., via the ``-o`` command-line option).

        Returns
        ----------
        CodeType
            Code object dynamically compiled from that Python package or module.
        '''

        # Plaintext decoded contents of that package or module.
        module_source = decode_source(data)

        # Abstract syntax tree (AST) dynamically parsed from these contents.
        module_ast = compile(
            module_source,
            path,
            'exec',
            PyCF_ONLY_AST,
            dont_inherit=True,
            optimize=_optimize,
        )

        # Abstract syntax tree (AST) modified by our AST transformation dynamically parsed from these contents.
        module_ast_beartyped = _BeartypeNodeTransformer().visit(module_ast)

        #FIXME: Document why exactly this call is needed -- if indeed this call
        #is needed. Is it? Research us up, please.
        fix_missing_locations(module_ast_beartyped)

        # Code object dynamically compiled from that transformed AST.
        module_codeobj = compile(
            module_ast_beartyped,
            path,
            'exec',
            dont_inherit=True,
            optimize=_optimize,
        )

        # Return this code object.
        return module_codeobj


    #FIXME: Is this monkey-patch strictly necessary? What exactly are the
    #real-world consequences of *NOT* doing so? Docstring us up, please.
    def get_code(self, *args, **kwargs) -> Optional[CodeType]:
        '''
        Create and return the code object underlying the passed module.

        All passed parameters are passed as is to the superclass method.
        '''

        # Temporarily replace that function with a beartype-specific variant.
        # Doing so is strongly inspired by a similar monkey-patch applied by the
        # external typeguard.importhook.TypeguardLoader.exec_module() method
        # authored by the incomparable @agronholm (Alex Grönholm), who writes:
        #     Use a custom optimization marker – the import lock should make
        #     this monkey patch safe
        #
        # We implicitly trust @agronholm to get that right in a popular project
        # stress-tested across hundreds of open-source projects over the past
        # several decades. So, we avoid explicit thread-safe locking here.
        #
        # Lastly, note there appears to be *NO* other means of safely
        # implementing this behaviour *WITHOUT* violating Don't Repeat Yourself
        # (DRY). Specifically, doing so would require duplicating most of the
        # entirety of the *EXTREMELY* non-trivial nearly 100 line-long
        # importlib._bootstrap_external.SourceLoader.get_code() method. Since
        # duplicating non-trivial and fragile code inherently tied to a specific
        # CPython version is considerably worse than applying a trivial one-line
        # monkey-patch, first typeguard and now @beartype strongly prefer this
        # monkey-patch. Did we mention that @agronholm is amazing? Because that
        # really bears repeating. May the name of Alex Grönholm live eternal!
        _bootstrap_external.cache_from_source = _cache_from_source_beartype

        # Attempt to defer to the superclass method with all passed parameters.
        try:
            return super().get_code(*args, **kwargs)
        # After doing so (and regardless of whether doing so raises an
        # exception), restore the original cache_from_source() function.
        finally:
            _bootstrap_external.cache_from_source = cache_from_source_original

# ....................{ PRIVATE ~ globals : threading      }....................
_claw_lock = RLock()
'''
Reentrant reusable thread-safe context manager gating access to otherwise
non-thread-safe private globals defined by both this high-level submodule and
subsidiary lower-level submodules (particularly, the
:attr:`beartype.claw._clawpackagenames._package_basename_to_subpackages` cache).
'''

# ....................{ PRIVATE ~ cachers                  }....................
#FIXME: Unit test us up, please.
def _cache_from_source_beartype(*args, **kwargs) -> str:
    '''
    Beartype-specific variant of the
    :func:`importlib._bootstrap_external.cache_from_source` function applying a
    beartype-specific optimization marker to that function.

    This, in turn, ensures that submodules residing in packages registered by a
    prior call to the :func:`beartype_submodules_on_import` function are
    compiled to files with the filetype ``".pyc{optimization}-beartype"``,
    where ``{optimization}`` is the original ``optimization`` parameter passed
    to this function call.
    '''

    # Original optimization parameter passed to this function call if any *OR*
    # the empty string otherwise.
    optimization_marker_old = kwargs.get('optimization', '')

    # New optimization parameter applied by this monkey-patch of that function,
    # uniquifying that parameter with a beartype-specific suffix.
    kwargs['optimization'] = f'{optimization_marker_old}-beartype'

    # Defer to the implementation of the original cache_from_source() function.
    return cache_from_source_original(*args, **kwargs)
