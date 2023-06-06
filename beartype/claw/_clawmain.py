#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype import hooks** (i.e., public-facing functions integrating high-level
:mod:`importlib` machinery required to implement :pep:`302`- and
:pep:`451`-compliant import hooks with the abstract syntax tree (AST)
transformations defined by the low-level :mod:`beartype.claw._ast.clawastmain`
submodule).

This private submodule is the main entry point for this subpackage. Nonetheless,
this private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Define a new "with all_beartyped():" context manager with signature:
#    @contextmanager
#    def all_beartyped(conf: BeartypeConf = BeartypeConf()): ...

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
from beartype.claw._pkg.clawpkgenum import BeartypeClawCoverage
from beartype.claw._pkg.clawpkghook import hook_packages
from beartype.roar import BeartypeClawRegistrationException
from beartype.typing import (
    Iterable,
)
from beartype._cave._cavefast import CallableFrameType
from beartype._conf.confcls import (
    BEARTYPE_CONF_DEFAULT,
    BeartypeConf,
)
from beartype._util.func.utilfunccodeobj import FUNC_CODEOBJ_NAME_MODULE
from beartype._util.func.utilfuncframe import (
    get_frame,
    get_frame_basename,
    get_frame_module_name,
)

# ....................{ HOOKERS                            }....................
#FIXME: Unit test us up, please.
def beartype_all(
    # Optional keyword-only parameters.
    *,
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
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

    This function is thread-safe.

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

    **tl;dr:** *Only call this function in non-reusable end user apps.*

    Parameters
    ----------
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., dataclass configuring the
        :mod:`beartype.beartype` decorator for *all* decoratable objects
        recursively decorated by the path hook added by this function).
        Defaults to ``BeartypeConf()``, the default ``O(1)`` configuration.

    Raises
    ----------
    BeartypeClawRegistrationException
        If the passed ``conf`` parameter is *not* a beartype configuration
        (i.e., :class:`BeartypeConf` instance).

    See Also
    ----------
    :func:`beartype.claw.beartyped`
        Arguably safer alternative to this function isolating the effect of this
        function to only imports performed inside a context manager.
    '''

    # The advantage of one-liners is the vantage of vanity.
    hook_packages(claw_coverage=BeartypeClawCoverage.PACKAGES_ALL, conf=conf)


#FIXME: Unit test us up, please.
def beartype_package_current(
    # Optional keyword-only parameters.
    *,
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
) -> None:
    '''
    Register a new **current package-specific beartype import path hook** (i.e.,
    callable inserted to the front of the standard :mod:`sys.path_hooks` list
    recursively applying the :func:`beartype.beartype` decorator to all typed
    callables and classes of all submodules of the current user-defined package
    calling this function on the first importation of those submodules).

    This function is thread-safe.

    Parameters
    ----------
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., dataclass configuring the
        :mod:`beartype.beartype` decorator for *all* decoratable objects
        recursively decorated by the path hook added by this function).
        Defaults to ``BeartypeConf()``, the default ``O(1)`` configuration.

    Raises
    ----------
    BeartypeClawRegistrationException
        If either:

        * This function is *not* called from a module (i.e., this function is
          called directly from within a read–eval–print loop (REPL)).
        * The passed ``conf`` parameter is *not* a beartype configuration
          (i.e., :class:`.BeartypeConf` instance).

    See Also
    ----------
    :func:`.beartype_packages`
        Further details.
    '''

    # Note the following logic *CANNOT* reasonably be isolated to a new private
    # helper function. Why? Because this logic itself calls existing private
    # helper functions assuming the caller to be at the expected position on the
    # current call stack.

    #FIXME: *UNSAFE.* get_frame() raises a "ValueError" exception if
    #passed a non-existent frame, which is non-ideal: e.g.,
    #    >>> sys._getframe(20)
    #    ValueError: call stack is not deep enough
    #
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
    #          return get_frame_or_none(ignore_frames=2)
    #* Import "get_frame_caller_or_none" above.
    #* Refactor this logic here to resemble:
    #      frame_caller = get_frame_caller_or_none()
    #      if frame_caller is None:
    #          raise BeartypeClawRegistrationException(
    #              'beartype_package_current() '
    #              'not callable directly from REPL scope.'
    #          )
    frame_caller: CallableFrameType = get_frame(1)  # type: ignore[assignment,misc]

    # Unqualified basename of that caller.
    frame_caller_basename = get_frame_basename(frame_caller)

    # Fully-qualified name of the module defining that caller.
    frame_caller_module_name = get_frame_module_name(frame_caller)

    #FIXME: Relax this constraint, please. Just iteratively search up the
    #call stack with iter_frames() until stumbling into a frame satisfying
    #this condition.
    # If that name is *NOT* the placeholder string assigned by the active
    # Python interpreter to all scopes encapsulating the top-most lexical
    # scope of a module in the current call stack, the caller is a class or
    # callable rather than a module. In this case, raise an exception.
    if frame_caller_basename != FUNC_CODEOBJ_NAME_MODULE:
        raise BeartypeClawRegistrationException(
            f'beartype_package_current() not called from module scope '
            f'(i.e., caller '
            f'"{frame_caller_module_name}.{frame_caller_basename}" '
            f'either class or callable rather than module).'
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
            f'beartype_package_current() not called by submodule '
            f'(i.e., caller module "{frame_caller_module_name}" is a '
            f'top-level module rather than submodule of some parent package).'
        )
    # Else, that module is a submodule of some parent package.

    # Fully-qualified name of the parent package defining that submodule,
    # parsed from the name of that submodule via this standard idiom:
    #     >>> frame_caller_module_name = 'muh_package.muh_module'
    #     >>> frame_caller_module_name.rpartition('.')
    #     ('muh_package', '.', 'muh_module')
    frame_caller_package_name = frame_caller_module_name.rpartition('.')[0]

    # Add a new import path hook beartyping this package.
    hook_packages(
        claw_coverage=BeartypeClawCoverage.PACKAGES_ONE,
        package_name=frame_caller_package_name,
        conf=conf,
    )


#FIXME: Unit test us up, please.
def beartype_package(
    # Mandatory parameters.
    package_name: str,

    # Optional keyword-only parameters.
    *,
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
) -> None:
    '''
    Register a new **package-specific beartype import path hook** (i.e.,
    callable inserted to the front of the standard :mod:`sys.path_hooks` list
    recursively applying the :func:`beartype.beartype` decorator to all typed
    callables and classes of all submodules of the package with the passed
    names on the first importation of those submodules).

    This function is thread-safe.

    Parameters
    ----------
    package_name : str
        Fully-qualified name of the package to be type-checked.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., dataclass configuring the
        :mod:`beartype.beartype` decorator for *all* decoratable objects
        recursively decorated by the path hook added by this function).
        Defaults to ``BeartypeConf()``, the default ``O(1)`` configuration.

    Raises
    ----------
    BeartypeClawRegistrationException
        If either:

        * The passed ``conf`` parameter is *not* a beartype configuration (i.e.,
          :class:`BeartypeConf` instance).
        * The passed ``package_name`` parameter is either:

          * *Not* a string.
          * The empty string.
          * A non-empty string that is *not* a valid **package name** (i.e.,
            ``"."``-delimited concatenation of valid Python identifiers).

    See Also
    ----------
    https://stackoverflow.com/a/43573798/2809027
        StackOverflow answer strongly inspiring the low-level implementation of
        this function with respect to inscrutable :mod:`importlib` machinery.
    '''

    # Add a new import path hook beartyping this package.
    hook_packages(
        claw_coverage=BeartypeClawCoverage.PACKAGES_ONE,
        package_name=package_name,
        conf=conf,
    )


#FIXME: Unit test us up, please.
def beartype_packages(
    # Mandatory parameters.
    package_names: Iterable[str],

    # Optional keyword-only parameters.
    *,
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
) -> None:
    '''
    Register a new **package-specific beartype import path hook** (i.e.,
    callable inserted to the front of the standard :mod:`sys.path_hooks` list
    recursively applying the :func:`beartype.beartype` decorator to all typed
    callables and classes of all submodules of all packages with the passed
    names on the first importation of those submodules).

    This function is thread-safe.

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
    package_names : Iterable[str]
        Iterable of the fully-qualified names of one or more packages to be
        type-checked.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., dataclass configuring the
        :mod:`beartype.beartype` decorator for *all* decoratable objects
        recursively decorated by the path hook added by this function).
        Defaults to ``BeartypeConf()``, the default ``O(1)`` configuration.

    Raises
    ----------
    BeartypeClawRegistrationException
        If either:

        * The passed ``conf`` parameter is *not* a beartype configuration (i.e.,
          :class:`BeartypeConf` instance).
        * The passed ``package_names`` parameter is either:

          * Non-iterable (i.e., fails to satisfy the
            :class:`collections.abc.Iterable` protocol).
          * An empty iterable.
          * A non-empty iterable containing at least one item that is either:

            * *Not* a string.
            * The empty string.
            * A non-empty string that is *not* a valid **package name** (i.e.,
              ``"."``-delimited concatenation of valid Python identifiers).

    See Also
    ----------
    https://stackoverflow.com/a/43573798/2809027
        StackOverflow answer strongly inspiring the low-level implementation of
        this function with respect to inscrutable :mod:`importlib` machinery.
    '''

    # Add a new import path hook beartyping these packages.
    hook_packages(
        claw_coverage=BeartypeClawCoverage.PACKAGES_MANY,
        package_names=package_names,
        conf=conf,
    )
