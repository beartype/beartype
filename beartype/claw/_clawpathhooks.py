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
:pep:`451`-compliant import hooks with the abstract syntax tree (AST)
transformation defined by the low-level :mod:`beartype.claw._clawast` submodule.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Unit test us up. Specifically, test that this approach successfully:
#* Directly decorates callables declared at:
#  * Global scope in an on-disk top-level non-package module embedded in our
#    test suite.
#  * Class scope in the same module.
#  * Closure scope in the same module.
#* Recursively decorates all callables declared by submodules of an on-disk
#  top-level package.
#* Does *NOT* conflict with pytest's assertion rewriting mechanism. This will
#  be non-trivial. Can we isolate another pytest process within the main
#  currently running pytest process? O_o

# ....................{ IMPORTS                            }....................
from beartype.claw._clawloader import BeartypeSourceFileLoader
from beartype.claw._clawregistrar import (
    is_packages_registered_any,
    register_packages,
    register_packages_all,
)
from beartype.roar import BeartypeClawRegistrationException
from beartype.typing import (
    Iterable,
    Optional,
    Union,
)
from beartype._conf import BeartypeConf
from beartype._util.func.utilfunccodeobj import (
    FUNC_CODEOBJ_NAME_MODULE,
    get_func_codeobj,
)
from beartype._util.func.utilfuncframe import get_frame
from importlib import invalidate_caches
from importlib.machinery import (
    SOURCE_SUFFIXES,
    FileFinder,
)
from sys import (
    path_hooks,
    path_importer_cache,
)
from threading import RLock
from types import (
    FrameType,
)

# ....................{ HOOKS                              }....................
#FIXME: Unit test us up, please.
def beartype_all(
    # Optional keyword-only parameters.
    *,
    conf: BeartypeConf = BeartypeConf(),
) -> None:
    '''
    Register a new **universal beartype import path hook** (i.e., callable
    inserted to the front of the standard :mod:`sys.path_hooks` list recursively
    decorating *all* typed callables and classes of *all* submodules of *all*
    packages on the first importation of those submodules with the
    :func:`beartype.beartype` decorator, wrapping those callables and classes
    with performant runtime type-checking).

    This function is the runtime equivalent of a full-blown static type checker
    like ``mypy`` or ``pyright``, enabling full-stack runtime type-checking of
    *all* typed callables and classes across *all* submodules imported from this
    end-user application -- including those defined by both:

    * First-party proprietary packages directly authored for this application.
    * Third-party open-source packages authored and maintained elsewhere.

    Usage
    ----------
    This function is intended to be called (usually without passed parameters)
    from module scope as the first statement of the top-level ``__init__``
    submodule of the top-level package of an end-user application to be fully
    type-checked by :func:`beartype.beartype`. This function then registers an
    import path hook type-checking all typed callables and classes of all
    submodules of all packages on the first importation of those submodules:
    e.g.,

    .. code-block:: python

       # In "muh_package.__init__":
       from beartype.claw import beartype_package
       beartype_package()  # <-- beartype all subsequent imports, yo

       # Import submodules *AFTER* calling beartype_package().
       from muh_package._some_module import muh_function  # <-- @beartyped!
       from yer_package.other_module import muh_class     # <-- @beartyped!

    Caveats
    ----------
    **This function is not intended to be called from intermediary APIs,
    libraries, frameworks, or other middleware.** This function is *only*
    intended to be called from full stack end-user applications as a convenient
    alternative to manually passing the names of all packages to be type-checked
    to the more granular :func:`beartype_package` function. This function
    imposes runtime type-checking on downstream reverse dependencies that may
    not necessarily want, expect, or tolerate runtime type-checking. This
    function should typically *only* be called by proprietary packages not
    expected to be reused by others. Open-source packages are advised to call
    the more granular :func:`beartype_package` function instead.

    **tl;dr:** *Only call this function in proprietary non-reusable packages.*

    Parameters
    ----------
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object). Defaults
        to ``BeartypeConf()``, the default ``O(1)`` constant-time configuration.

    Raises
    ----------
    BeartypeClawRegistrationException
        If either:

        * The passed ``conf`` parameter is *not* a beartype configuration (i.e.,
          :class:`BeartypeConf` instance).
    '''

    # ..................{ PATH HOOK                          }..................
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize with the beartype_all() function.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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
        is_path_hook_added = is_packages_registered_any()

        # Register *ALL* packages for subsequent lookup during submodule
        # importation by the beartype import path hook registered below *AFTER*
        # deciding whether this function has been called already.
        #
        # Note this helper function fully validates these parameters. Ergo, we
        # intentionally avoid doing so here in this higher-level function.
        register_packages_all(conf=conf)

        # True only if the beartype import path hook subsequently added below
        # has already been added by a prior call to this function under the
        # active Python interpreter.
        if not is_path_hook_added:
            _add_path_hook()


#FIXME: Unit test us up, please.
def beartype_package(
    # Optional parameters.
    package_names: Optional[Union[str, Iterable[str]]] = None,

    # Optional keyword-only parameters.
    *,
    conf: BeartypeConf = BeartypeConf(),
) -> None:
    '''
    Register a new **package-specific beartype import path hook** (i.e.,
    callable inserted to the front of the standard :mod:`sys.path_hooks` list
    recursively applying the :func:`beartype.beartype` decorator to all typed
    callables and classes of all submodules of all packages with the passed
    names on the first importation of those submodules).

    Usage
    ----------
    This function is intended to be called (usually without passed parameters)
    from module scope as the first statement of the top-level ``__init__``
    submodule of any package to be type-checked by :func:`beartype.beartype`.
    This function then registers an import path hook type-checking all
    typed callables and classes of all submodules of that package on the first
    importation of those submodules: e.g.,

    .. code-block:: python

       # In "muh_package.__init__":
       from beartype.claw import beartype_package
       beartype_package()  # <-- beartype all subsequent package imports, yo

       # Import package submodules *AFTER* calling beartype_package().
       from muh_package._some_module import muh_function  # <-- @beartyped!
       from muh_package.other_module import muh_class     # <-- @beartyped!

    Parameters
    ----------
    package_names : Optional[Union[str, Iterable[str]]]
        Either:

        * Fully-qualified name of the package to be type-checked.
        * Iterable of the fully-qualified names of one or more packages to be
          type-checked.

        Defaults to ``None``, in which case this parameter defaults to the
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

          * Neither a string nor an iterable (i.e., fails to satisfy the
            :class:`collections.abc.Iterable` protocol).
          * An empty string or iterable.
          * A non-empty string that is *not* a valid **package name** (i.e.,
            ``"."``-delimited concatenation of valid Python identifiers).
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
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize with the beartype_all() function.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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
        is_path_hook_added = is_packages_registered_any()

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

    See Also
    ----------
    https://stackoverflow.com/a/43573798/2809027
        StackOverflow answer strongly inspiring the low-level implementation of
        this function with respect to inscrutable :mod:`importlib` machinery.
    '''

    # 2-tuple of the undocumented format expected by the FileFinder.path_hook()
    # class method called below, associating our beartype-specific source file
    # loader with the platform-specific filetypes of all sourceful Python
    # packages and modules. We didn't do it. Don't blame the bear.
    LOADER_DETAILS = (BeartypeSourceFileLoader, SOURCE_SUFFIXES)

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

# ....................{ PRIVATE ~ globals : threading      }....................
_claw_lock = RLock()
'''
Reentrant reusable thread-safe context manager gating access to otherwise
non-thread-safe private globals defined by both this high-level submodule and
subsidiary lower-level submodules (particularly, the
:attr:`beartype.claw._clawregistrar._package_basename_to_subpackages` cache).
'''
