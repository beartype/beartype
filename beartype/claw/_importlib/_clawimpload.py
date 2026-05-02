#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **import hook module loaders** (i.e., :mod:`importlib`-compliant
classes dynamically decorating all typed callables and classes of all submodules
of all packages previously registered in our global package trie by the
:func:`beartype.beartype` decorator via abstract syntax tree (AST) transformers
defined by the :mod:`beartype.claw._ast.clawastmain` submodule).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from ast import PyCF_ONLY_AST
from beartype.claw._ast.clawastmain import BeartypeNodeTransformer
from beartype.claw._importlib.clawimpcache import (  # type: ignore[attr-defined]
    cache_from_source_beartype,
    cache_from_source_original,
)
from beartype.roar import BeartypeClawImportAstException
from beartype._cave._cavefast import RegexCompiledType
from beartype._conf.confmain import BeartypeConf
from beartype._util.ast.utilastget import get_node_repr_indented
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_15
from beartype._util.text.utiltextlabel import label_exception_message
from importlib import (  # type: ignore[attr-defined]
    _bootstrap_external,  # pyright: ignore
)
from importlib.machinery import SourceFileLoader
from importlib.util import decode_source
from re import compile as re_compile
from types import CodeType
from typing import Optional

# ....................{ CLASSES                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: To improve forward compatibility with the superclass API over which
# we have *NO* control, avoid accidental conflicts by suffixing *ALL* private
# and public attributes of this subclass by "_beartype".
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#FIXME: Unit test us up, please.
class BeartypeSourceFileLoader(SourceFileLoader):
    '''
    **Beartype source file loader** implementing :mod:`importlib` machinery
    loading a **sourceful Python package or module** (i.e., package or module
    backed by a ``.py``-suffixed source file) into a **module spec** (i.e.,
    in-memory :class:`importlib._bootstrap.ModuleSpec` instance describing the
    importation of that package or module, complete with a reference back to
    this originating loader).

    The low-level :func:`beartype.claw._package.clawpkgmain.hook_packages`
    import hook underlying *all* high-level :mod:`beartype.claw` import hooks
    injects a lower-level **import path hook** (i.e., factory closure
    instantiating this class as an item of the standard :mod:`sys.path_hooks`
    list) to the front of that list. When called by a higher-level parent
    **import metapath hook** (i.e., object suitable for use as an item of the
    standard :mod:`sys.meta_path` list), that import path hook closure:

    #. Instantiates one instance of the standard
       :class:`importlib._bootstrap_external.FileFinder` class for each
       **imported Python package** (i.e., package on the :mod:`sys.path` list).
       The :meth:``importlib._bootstrap_external.FileFinder.find_spec` method of
       that instance then returns this uninstantiated
       :class:`.BeartypeSourceFileLoader` class for each **imported Python
       package submodule** (i.e., submodule directly contained in that package).
    #. Adds a new key-value pair to the standard :mod:`sys.path_importer_cache`
       dictionary, whose:

       * Key is the package of that module.
       * Value is that instance of this class.

    Motivation
    ----------
    This loader was intentionally implemented so as to exclusively leverage the
    lower-level :attr:`sys.path_hooks` mechanism for declaring import hooks
    rather than both that *and* the higher-level :attr:`sys.meta_path`
    mechanism. All prior efforts in the Python ecosystem to transform the
    abstract syntax trees (ASTs) of modules at importation time via import hooks
    leverage both mechanisms. This includes:

    * :mod:`pytest`, which rewrites test assertion statements via import hooks
      leveraging both mechanisms.
    * :mod:`typeguard`, which implicitly applies the runtime type-checking
      :func:`typguard.typechecked` decorator via import hooks leveraging both
      mechanisms.
    * :mod:`ideas`, which applies arbitrary caller-defined AST transformations
      via (...wait for it) import hooks leveraging both mechanisms.

    Beartype subverts this long-storied tradition by *only* leveraging the
    lower-level :attr:`sys.path_hooks` mechanism. Doing so reduces maintenance
    burden, code complexity, and inter-package conflicts. The latter is
    particularly salient. AST transformations applied by both :mod:`typeguard`
    and :mod:`ideas` accidentally conflict with those applied by :mod:`pytest`.
    Why? Because (in order):

    #. When run as a test suite runner, :mod:`pytest` necessarily runs first and
       thus prepends its import hook as the new first item of the
       :attr:`sys.meta_path` list.
    #. When imported during subsequent unit and/or integration testing under
       that test suite runner, :mod:`typeguard` and :mod:`ideas` then install
       their own import hooks as the new first item of the :attr:`sys.meta_path`
       list. The import hook previously prepended by :mod:`pytest` then becomes
       the second item  of the :attr:`sys.meta_path` list. Python consults both
       the :attr:`sys.meta_path` and :attr:`sys.path_hooks` lists in a
       first-come-first-served manner. The first hook on each list satisfying a
       request to find and import a module being imported terminates that
       request; no subsequent hooks are consulted. Both :mod:`typeguard` and
       :mod:`ideas` fail to iteratively consult subsequent hooks (e.g., with a
       piggybacking scheme of some sort). Both squelch the hook previously
       installed by :mod:`pytest` that rewrote assertions. That is bad.

    Attributes
    ----------
    _module_conf : Optional[BeartypeConf]
        Either:

        * If the most recent call to the :meth:`get_code` method (which loads a
          module by creating and return the code object underlying that module)
          was passed the fully-qualified name of a module with a transitive
          parent package previously registered by a call to a public
          :mod:`beartype.claw` import hook factory (e.g.,
          :func:`beartype.claw.beartype_package`), the beartype configuration
          with which to type-check that module.
        * Else, :data:`None`.

        This instance variable enables our override of the parent
        :meth:`.get_code` method to communicate this configuration to the child
        :meth:`.source_to_code` method, which fails to accept and thus has *no*
        access to this module name. The superclass implementation of the
        :meth:`.get_code` method then internally calls our override of the
        :meth:`.source_to_code` method, which accesses this instance variable to
        decide whether and how to type-check that module.

        Ordinarily, this approach would be fraught with fragility. For example,
        what if something *other* than the :meth:`get_code` method called the
        :meth:`.source_to_code` method? Thankfully, that is *not* a concern here.
        :meth:`.source_to_code` is only called by :meth:`get_code` in the
        :mod:`importlib` codebase. Ergo, :meth:`source_to_code` should ideally
        have been privatized (e.g., as ``_source_to_code()``).
    _module_name : str
        Fully-qualified name of the module currently being imported by the
        :meth:`.get_code` method for subsequent reference in the lower-level
        :meth:`.source_to_code` method transitively called by the former.

    See Also
    --------
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

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, *args, **kwargs) -> None:
        '''
        Initialize this beartype source file loader.

        All passed parameters are passed as is to the superclass method, which
        then calls our lower-level :meth:`.source_to_code` subclass method
        overridden below.
        '''

        # Initialize our superclass with all passed parameters.
        super().__init__(*args, **kwargs)

        # Nullify all subclass-specific instance variables for safety.
        self._module_conf: Optional[BeartypeConf] = None
        self._module_name: str = None  # type: ignore[assignment]

    # ..................{ LOADER API                         }..................
    # The importlib._bootstrap_external.*Loader API declares the low-level
    # exec_module() method, which accepts a module spec (i.e.,
    # "importlib._bootstrap.ModuleSpec" object created and returned by a prior
    # call to the higher-level find_spec() method documented above) to create
    # and return a fully imported module object (i.e., "types.ModuleType"
    # object). To do so:
    # * The default exec_module() implementation internally calls the
    #   lower-level get_code() method returning an in-memory Python code object
    #   deserialized from the on-disk or in-memory bytes underlying that module.
    # * The default get_code() implementation internally calls the
    #   lower-level source_to_code() method returning an in-memory Python code
    #   object dynamically compiled from the passed in-memory bytes.

    def get_code(self, fullname: str) -> Optional[CodeType]:
        '''
        Create and return the code object underlying the module with the passed
        name.

        This override of the superclass :meth:`SourceLoader.get_code` method
        internally follows one of two distinct code paths, conditionally
        depending on whether a parent package transitively containing that
        module has been previously registered with the
        :mod:`beartype.claw._package.clawpkgmain` submodule (e.g., by a call to
        the :func:`beartype.claw.beartype_package` function). Specifically:

        * If *no* parent package transitively containing that module has been
          registered, this method fully defers to the superclass
          :meth:`.SourceLoader.get_code` method.
        * Else, one or more parent packages transitively containing that module
          have been registered. In this case, this method (in order):

          #. Temporarily monkey-patches (i.e., replaces) the
             private :func:`importlib._bootstrap_external.cache_from_source`
             function with our beartype-specific
             :func:`.cache_from_source_beartype` variant.
          #. Calls the superclass :meth:`.SourceLoader.get_code` method, which:

             #. Calls our override of the lower-level superclass
                :meth:`.SourceLoader.source_to_code` method.

          #. Restores the
             :func:`importlib._bootstrap_external.cache_from_source` function to
             its original implementation.

        Motivation
        ----------
        The temporary monkey-patch applied by this method is strongly inspired
        by a suspiciously similar temporary monkey-patch applied by the external
        :meth:`typeguard._importhook.TypeguardLoader.exec_module` method
        authored by the incomparable @agronholm (Alex Grönholm), who writes:

            Use a custom optimization marker – the import lock should make
            this monkey patch safe

        The aforementioned "custom optimization marker" is, in fact, a
        beartype-specific constant embedded in the filename of the cached Python
        bytecode file to which that module is byte-compiled. This filename
        typically resembles
        ``__pycache__/{module_basename}.{optimization_markers}.pyc``, where:

        * ``{module_basename}`` is the unqualified basename of that module.
        * ``{optimization_markers}`` is a ``"-"``-delimited string of
          **optimization markers** (i.e., arbitrary alphanumeric labels
          uniquifying this bytecode file to various bytecode-specific metadata,
          including the name and version of the active Python interpreter).

        This monkey-patch suffixes ``{optimization_markers}`` by
        :data:`.OPTIMIZATION_MARKER_BEARTYPE`, which additionally uniquifies the
        filename of this bytecode file to the abstract syntax tree (AST)
        transformation applied by this version of :mod:`beartype`. Why? Because
        external callers can trivially enable and disable that transformation
        for any module by either calling or not calling the
        :func:`beartype.claw.beartype_package` function with the name of a
        package transitively containing that module. Compiling a beartyped
        variant of that module to the same bytecode file as the non-beartyped
        variant of that module would erroneously persist beartyping to that
        module -- even *after* removing the relevant call to the
        :func:`beartype.claw.beartype_package` function! Clearly, that's awful.
        Enter @agronholm's phenomenal patch, stage left.

        We implicitly trust @agronholm to get that right in a popular project
        stress-tested across hundreds of open-source projects over the past
        several decades. So, we avoid explicit thread-safe locking here.

        Lastly, note there appears to be *no* other means of safely implementing
        this behaviour *without* violating Don't Repeat Yourself (DRY).
        Specifically, doing so would require duplicating most of the entirety of
        the *extremely* non-trivial nearly 100 line-long
        :meth:`importlib._bootstrap_external.SourceLoader.get_code` method.
        Since duplicating non-trivial and fragile code inherently tied to a
        specific CPython version is considerably worse than applying a trivial
        one-line monkey-patch, first typeguard and now @beartype strongly prefer
        this monkey-patch. Did we mention that @agronholm is amazing? Because
        that really bears repeating. May the name of Alex Grönholm live eternal!

        Caveats
        -------
        This getter intentionally avoids all dangerous attempts to recursively
        type-check the :mod:`beartype` package by the :func:`beartype.beartype`
        decorator. Doing so would be:

        * **Fundamentally unnecessary.** The entirety of the :mod:`beartype`
          package already religiously guards against type violations with a
          laborious slew of type checks littered throughout the codebase --
          including assertions of the form ``"assert isinstance({arg}, {type}),
          ..."``. Further decorating *all* :mod:`beartype` callables with
          automated type-checking only needlessly reduces the runtime efficiency
          of the :mod:`beartype` package.
        * **Fundamentally dangerous**, which is the greater concern. For
          example, the
          :meth:`beartype.claw._ast.clawastmain.BeartypeNodeTransformer.visit_Module`
          method dynamically inserts a module-scoped import of the
          :func:`beartype._decor.decorcore.beartype_object_nonfatal` decorator
          at the head of the module currently being imported. But if the
          :mod:`beartype._decor.decorcore` submodule itself is being imported,
          then that importation would destructively induce an infinite circular
          import! Could that ever happen? **YES.** Conceivably, an external
          caller could force reimportation of all modules by emptying the
          :mod:`sys.modules` cache.

        Note this edge case is surprisingly common. The public
        :func:`beartype.claw.beartype_all` function implicitly registers *all*
        packages (including :mod:`beartype` itself by default) for decoration by
        the :func:`beartype.beartype` decorator.

        Parameters
        ----------
        fullname : str
            Fully-qualified name of the module currently being imported.

        Returns
        -------
        Optional[CodeType]
            Code object underlying that module.
        '''

        # ..................{ NOOP ~ core                    }..................
        # If that module resides in a fundamentally problematic package (e.g.,
        # the beartype codebase itself), preserve that module as is by simply
        # deferring to the superclass method *WITHOUT* monkey-patching
        # cache_from_source().
        #
        # Ideally, this should *NOT* be required. Why? Because the
        # get_package_conf_or_none() getter called below is already hard-wired
        # to return "None" and thus preserve that module as is when the passed
        # module resides in the beartype codebase.
        #
        # Pragmatically, this is *ABSOLUTELY* required. Why? The quasi-standard
        # "coverage" package and all downstream packages layered on top of that
        # package (e.g., "pytest-cov"). For unknown reasons that neither I nor
        # "coverage" maintainers will ever be able to clearly articulate,
        # "coverage" fails with unreadable exceptions when beartype fails to
        # perform this "if" conditional -- which beartype once did, which is why
        # beartype no longer does. Oddly, these failures occur *ONLY* when
        # instructing "coverage" to measure coverage for a specific submodule of
        # a third-party package whose top-level "{package}.__init__" submodule
        # registers a "beartype.claw" import hook. These failures resemble:
        #     $ coverage run --source "{package}.{submodule}" -m pytest tests
        #     Traceback (most recent call last):
        #       File "/home/leycec/py/pyenv/versions/3.15.0a5/bin/coverage", line 7, in <module>
        #         sys.exit(main())
        #                  ~~~~^^
        #       File "/home/leycec/py/pyenv/versions/3.15.0a5/lib/python3.15/site-packages/coverage/cmdline.py", line 1163, in main
        #         status = CoverageScript().command_line(argv)
        #       File "/home/leycec/py/pyenv/versions/3.15.0a5/lib/python3.15/site-packages/coverage/cmdline.py", line 853, in command_line
        #         return self.do_run(options, args)
        #                ~~~~~~~~~~~^^^^^^^^^^^^^^^
        #       File "/home/leycec/py/pyenv/versions/3.15.0a5/lib/python3.15/site-packages/coverage/cmdline.py", line 1042, in do_run
        #         runner.run()
        #         ~~~~~~~~~~^^
        #       File "/home/leycec/py/pyenv/versions/3.15.0a5/lib/python3.15/site-packages/coverage/execfile.py", line 174, in run
        #         self._prepare2()
        #         ~~~~~~~~~~~~~~^^
        #       File "/home/leycec/py/pyenv/versions/3.15.0a5/lib/python3.15/site-packages/coverage/execfile.py", line 139, in _prepare2
        #         pathname, self.package, self.spec = find_module(self.modulename)
        #                                             ~~~~~~~~~~~^^^^^^^^^^^^^^^^^
        #       File "/home/leycec/py/pyenv/versions/3.15.0a5/lib/python3.15/site-packages/coverage/execfile.py", line 58, in find_module
        #         spec = importlib.util.find_spec(mod_main)
        #       File "<frozen importlib.util>", line 90, in find_spec
        #       File "/home/leycec/py/beartype/beartype/claw/_importlib/_clawimpload.py", line 322, in get_code
        #         from beartype.claw._clawstate import claw_state
        #       File "/home/leycec/py/beartype/beartype/claw/_importlib/_clawimpload.py", line 322, in get_code
        #         from beartype.claw._clawstate import claw_state
        #       File "/home/leycec/py/beartype/beartype/claw/_importlib/_clawimpload.py", line 322, in get_code
        #         from beartype.claw._clawstate import claw_state
        #       [Previous line repeated 1 more time]
        #     ImportError: cannot import name 'claw_state' from partially
        #     initialized module 'beartype.claw._clawstate' (most likely due to
        #     a circular import)
        #     (/home/leycec/py/beartype/beartype/claw/_clawstate.py)
        #
        # What is clear is that this "if" conditional resolves that issue.
        # Therefore, understanding is irrelevant. All that matters is resolving
        # inscrutable issues, even in the absence of understanding. I sigh.
        #
        # Note that this "if" conditional *MUST* be performed prior to importing
        # *ANYTHING* below. Importing *ANYTHING* before this "if" conditional
        # triggers the above "coverage" failure, which rather defeats the point.
        if _BLACKLIST_PACKAGE_NAMES_REGEX.match(fullname) is not None:
            return super().get_code(fullname)
        # Else, that module does *NOT* reside in a problematic package.

        # ..................{ IMPORTS                        }..................
        # Avoid circular import dependencies.
        from beartype.claw._clawstate import claw_state
        from beartype.claw._package.clawpkgtrie import get_package_conf_or_none

        # ..................{ NOOP ~ more                    }..................
        # Beartype configuration with which to type-check that module if that
        # module is hooked under its fully-qualified name *OR* "None" otherwise
        # (i.e., if that module is unhooked).
        conf = get_package_conf_or_none(fullname)
        # print(f'Imported module "{fullname}" package "{package_name}" conf: {repr(self._module_conf)}')

        # If that module is unhooked, preserve that module as is by simply
        # deferring to the superclass method *WITHOUT* monkey-patching
        # cache_from_source(). This isn't only an optimization, though it is
        # that as well. This is critical. Why? Because modules *NOT* being
        # beartyped should remain compiled under their standard non-beartyped
        # bytecode filenames.
        if conf is None:
            # print(f'Importing module "{fullname}" without beartyping...')
            return super().get_code(fullname)
        # Else, that module has been hooked. In this case...
        #
        # Note that the logic below requires inefficient exception handling (as
        # well as a potentially risky monkey-patch) and is thus performed *ONLY*
        # when absolutely necessary.

        # ..................{ TYPE-CHECK                     }..................
        # Classify local attributes as instance variables for subsequent
        # reference in the lower-level source_to_code() method transitively
        # called by this higher-level method.
        self._module_conf = conf
        self._module_name = fullname

        # Expose this configuration to the "beartype.claw._ast" subpackage.
        claw_state.module_name_to_beartype_conf[fullname] = conf

        # Temporarily monkey-patch away the cache_from_source() function with a
        # beartype-specific replacement transforming that module with
        # beartype-specific type-checking.
        #
        # Note that @agronholm (Alex Grönholm) claims that "the import lock
        # should make this monkey patch safe." We're trusting you here, man!
        _bootstrap_external.cache_from_source = cache_from_source_beartype

        # Attempt to defer to the superclass method.
        try:
            # print(f'Importing module "{fullname}" with beartyping...')
            return super().get_code(fullname)
        # After doing so (and regardless of whether doing so raises an
        # exception), restore the original cache_from_source() function.
        finally:
            _bootstrap_external.cache_from_source = (
                cache_from_source_original)


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

        # Optional parameters.
        #
        # Note that the optional "fullname" parameter is accepted by the
        # superclass method *ONLY* under Python >= 3.15.
        fullname: Optional[str] = None,

        # Optional keyword-only parameters.
        *,
        _optimize: int = -1,
    ) -> CodeType:
        '''
        Code object dynamically compiled from the **sourceful Python package or
        module** (i.e., package or module backed by a ``.py``-suffixed source
        file) with the passed undecoded contents and filename, efficiently
        transformed in-place by our abstract syntax tree (AST) transformation
        automatically applying the :func:`beartype.beartype` decorator to all
        applicable objects of that package or module.

        The higher-level :meth:`get_code` superclass method internally calls
        this lower-level subclass method.

        Parameters
        ----------
        data : bytes
            **Byte array** (i.e., undecoded list of bytes) of the Python package
            or module to be decoded and dynamically compiled into a code object.
        path : str
            Absolute or relative filename of that Python package or module.
        fullname : Optional[str], default: None,
            Fully-qualified name of that Python package or module. In theory,
            this name *should* be equal to the :mod:`beartype`-specific
            :attr:`._module_name` instance variable and thus ignorable for
            :mod:`beartype` purposes. In practice, it's best to assume nothing.
            Defaults to :data:`None`, presumably for compatibility with
            third-party packages targeting older Python versions that failed to
            define this parameter.
        _optimize : int, default: -1
            **Optimization level** (i.e., numeric integer signifying increasing
            levels of optimization under which to compile that Python package or
            module). Defaults to -1, implying the current interpreter-wide
            optimization level with which the active Python process was
            initially invoked (e.g., via the ``-o`` command-line option).

        Returns
        -------
        CodeType
            Code object dynamically compiled from that Python package or module.

        Raises
        ------
        BeartypeClawImportAstException
            If our **beartype node transformer** (i.e.,
            :class:`.BeartypeNodeTransformer` instance) dynamically transforms
            the original valid abstract syntax tree (AST) governing that Python
            package or module into a new invalid AST.
        '''
        #NOTETOSELF: If you uncomment this and don't see any output, then
        #bytecode caching is the culprit. Unit or integration tests are probably
        #failing to properly clear the appropriate bytecode cache. *sigh*
        # from sys import stderr
        # print('!!!TRANSFORMING!!!', file=stderr)
        # print('!!!TRANSFORMING!!!')

        # If that module has *NOT* been registered for type-checking, preserve
        # that module as is by simply deferring to the superclass method.
        if self._module_conf is None:
            # If the active Python interpreter targets Python >= 3.15, the
            # superclass method accepts the additional optional "fullname"
            # parameter. In this case, pass this parameter.
            if IS_PYTHON_AT_LEAST_3_15:
                return super().source_to_code(  # type: ignore[call-arg]
                    data=data,
                    path=path,
                    fullname=fullname,  # pyright: ignore
                    _optimize=_optimize,
                )
            # Else, the active Python interpreter targets Python <= 3.14. In
            # this case, the superclass method accepts *NO* additional optional
            # "fullname" parameter. Avoid passing this parameter.
            else:
                return super().source_to_code(  # type: ignore[call-arg]
                    data=data, path=path, _optimize=_optimize)  # pyright: ignore
        # Else, that module has been registered for type-checking.

        # Plaintext decoded contents of that module.
        module_source = decode_source(data)

        # Abstract syntax tree (AST) parsed from these contents.
        module_ast = compile(
            module_source,
            path,
            'exec',
            PyCF_ONLY_AST,
            # Prevent these contents from inheriting the effects of any
            # "from __future__ import" statements in effect in beartype itself.
            dont_inherit=True,
            optimize=_optimize,
        )

        # AST transformer decorating typed callables and classes by @beartype.
        ast_beartyper = BeartypeNodeTransformer(
            module_name=self._module_name, conf=self._module_conf)

        # Abstract syntax tree (AST) modified by this transformer.
        module_ast_beartyped = ast_beartyper.visit(module_ast)

        #FIXME: Conditionally perform this logic if "conf.is_debug", please.
        #Note that printing to "stderr" is pivotal. For some reason, Python
        #fails to forward printing to "stdout" across subprocesses even when we
        #explicitly tell it to. Look. I don't even know. Just roll with it!
        # from sys import stderr
        # print(
        #     (
        #         f'Module "{self._module_name}" abstract syntax tree (AST) '
        #         f'transformed by @beartype to:\n\n'
        #         f'{get_node_repr_indented(module_ast_beartyped)}'
        #     ),
        #     file=stderr,
        # )

        # Attempt to...
        try:
            # Code object compiled from this transformed AST.
            module_codeobj = compile(
                module_ast_beartyped,
                path,
                'exec',
                # Prevent these contents from inheriting the effects of any
                # "from __future__ import" statements in effect in the beartype
                # codebase itself.
                dont_inherit=True,
                optimize=_optimize,
            )
        # If doing so raises *ANY* exception whatsoever, wrap that low-level
        # exception with a higher-level exception exhibiting the exact issue.
        # Doing so enables users to submit meaningful issues to our tracker.
        except Exception as exception:
            raise BeartypeClawImportAstException(
                f'Module "{self._module_name}" unimportable, as '
                f'@beartype generated invalid '
                f'abstract syntax tree (AST):\n\n'
                f'{get_node_repr_indented(module_ast_beartyped)}\n\n'
                f'ast.compile() exception (when passed the above AST):\n\t'
                f'{label_exception_message(exception)}'
            ) from exception

        # Return this code object.
        return module_codeobj

# ....................{ PRIVATE ~ globals                  }....................
#FIXME: Preserved in the likelihood we'll need to resurrect this. *sigh*
_BLACKLIST_PACKAGE_NAMES_REGEX: RegexCompiledType = None  # type: ignore[assignment]
'''
Compiled regular expression matching the the fully-qualified names of all
top-level packages to be blacklisted by the
:func:`.BeartypeSourceFileLoader.get_code` method.

See commentary inside that method for exhaustive (and exhausting) details.
'''

# ....................{ PRIVATE ~ initializers             }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Enable this global to be locally initialized below.
    global _BLACKLIST_PACKAGE_NAMES_REGEX

    # Frozen set of the fully-qualified names of all top-level packages to be
    # blacklisted by the BeartypeSourceFileLoader.get_code() method.
    #
    # Note that:
    # * This set is defined in an ad-hoc brute-force manner by simply
    #   iteratively adding package names to this set until all tests pass. Yes,
    #   this is absurd. Yes, this is "importlib" Hell. Welcome to Python, son.
    # * If you are reading this, you are wondering exactly how we decided what
    #   package names to even add to this set. The answer is that we manually
    #   inspected circular "ImportError" exceptions raised by the
    #   Coverage.py-specific integration test for suspicious imports of *ANY*
    #   packages residing outside the beartype codebase. For example, a cautious
    #   inspection of the following traceback would note the ultra-suspicious
    #   "import email" import statement, suggesting that the standard "email"
    #   package also needs to be added to this set: e.g.,
    #       Traceback (most recent call last):
    #         File "<frozen runpy>", line 196, in _run_module_as_main
    #         File "<frozen runpy>", line 87, in _run_code
    #         File "/home/leycec/py/pyenv/versions/3.15.0a8/lib/python3.15/site-packages/coverage/__main__.py", line 12, in <module>
    #           sys.exit(main())
    #                    ~~~~^^
    #         File "/home/leycec/py/pyenv/versions/3.15.0a8/lib/python3.15/site-packages/coverage/cmdline.py", line 1163, in main
    #           status = CoverageScript().command_line(argv)
    #         File "/home/leycec/py/pyenv/versions/3.15.0a8/lib/python3.15/site-packages/coverage/cmdline.py", line 853, in command_line
    #           return self.do_run(options, args)
    #                  ~~~~~~~~~~~^^^^^^^^^^^^^^^
    #         File "/home/leycec/py/pyenv/versions/3.15.0a8/lib/python3.15/site-packages/coverage/cmdline.py", line 1042, in do_run
    #           runner.run()
    #           ~~~~~~~~~~^^
    #         File "/home/leycec/py/pyenv/versions/3.15.0a8/lib/python3.15/site-packages/coverage/execfile.py", line 174, in run
    #           self._prepare2()
    #           ~~~~~~~~~~~~~~^^
    #         File "/home/leycec/py/pyenv/versions/3.15.0a8/lib/python3.15/site-packages/coverage/execfile.py", line 139, in _prepare2
    #           pathname, self.package, self.spec = find_module(self.modulename)
    #                                               ~~~~~~~~~~~^^^^^^^^^^^^^^^^^
    #         File "/home/leycec/py/pyenv/versions/3.15.0a8/lib/python3.15/site-packages/coverage/execfile.py", line 58, in find_module
    #           spec = importlib.util.find_spec(mod_main)
    #         File "<frozen importlib.util>", line 90, in find_spec
    #         File "/home/leycec/py/beartype/beartype/claw/_importlib/_clawimpload.py", line 394, in get_code
    #           from beartype.claw._clawstate import claw_state
    #         File "/home/leycec/py/beartype/beartype/__init__.py", line 150, in <module>
    #           _init()
    #           ~~~~~^^
    #         File "/home/leycec/py/beartype/beartype/__init__.py", line 71, in _init
    #           from beartype.meta import (
    #           ...<4 lines>...
    #           )
    #         File "/home/leycec/py/beartype/beartype/meta.py", line 35, in <module>
    #           from importlib.metadata import metadata as _get_package_metadata
    #         File "/home/leycec/py/pyenv/versions/3.15.0a8/lib/python3.15/importlib/metadata/__init__.py", line 14, in <module>
    #           import email  # <-- *THIS IS ULTRA-SUSPICIOUS IMPORT OF DOOMGUY*
    #         File "/home/leycec/py/beartype/beartype/claw/_importlib/_clawimpload.py", line 394, in get_code
    #           from beartype.claw._clawstate import claw_state
    #         File "/home/leycec/py/beartype/beartype/claw/__init__.py", line 210, in <module>
    #           from beartype.claw._clawmain import (
    #           ...<4 lines>...
    #           )
    #         File "/home/leycec/py/beartype/beartype/claw/_clawmain.py", line 24, in <module>
    #           from beartype.claw._package.clawpkgmain import hook_packages
    #         File "/home/leycec/py/beartype/beartype/claw/_package/clawpkgmain.py", line 16, in <module>
    #           from beartype.claw._package.clawpkgtrie import (
    #           ...<5 lines>...
    #           )
    #         File "/home/leycec/py/beartype/beartype/claw/_package/clawpkgtrie.py", line 17, in <module>
    #           from beartype.claw._importlib.clawimpmain import remove_beartype_pathhook
    #         File "/home/leycec/py/beartype/beartype/claw/_importlib/clawimpmain.py", line 18, in <module>
    #           from beartype.claw._importlib._clawimpload import BeartypeSourceFileLoader
    #         File "/home/leycec/py/beartype/beartype/claw/_importlib/_clawimpload.py", line 18, in <module>
    #           from beartype.claw._ast.clawastmain import BeartypeNodeTransformer
    #         File "/home/leycec/py/beartype/beartype/claw/_ast/clawastmain.py", line 21, in <module>
    #           from beartype.claw._ast._kind.clawastassign import (
    #               BeartypeNodeTransformerAssignMixin)
    #         File "/home/leycec/py/beartype/beartype/claw/_ast/_kind/clawastassign.py", line 24, in <module>
    #           from beartype._data.claw.dataclawmagic import BEARTYPE_RAISER_FUNC_NAME
    #         File "/home/leycec/py/beartype/beartype/_data/claw/dataclawmagic.py", line 14, in <module>
    #           from beartype.meta import (
    #           ...<2 lines>...
    #           )
    #       ImportError: cannot import name 'NAME' from partially initialized module 'beartype.meta' (most likely due to a circular import) (/home/leycec/py/beartype/beartype/meta.py)
    _BLACKLIST_PACKAGE_NAMES = frozenset((
        'beartype',
        'email',
        'importlib',
        'numbers',
    ))

    # "|"-delimited string of these names.
    _BLACKLIST_PACKAGE_NAMES_ORED = r'|'.join(_BLACKLIST_PACKAGE_NAMES)

    # Compiled regular expression matching any string starting with these names
    # and either:
    # * Immediately terminating *OR*...
    # * Followed by a "." delimiter (effectively also terminating that name)
    #   followed by one or more arbitrary characters.
    _BLACKLIST_PACKAGE_NAMES_REGEX = re_compile(
        rf'^({_BLACKLIST_PACKAGE_NAMES_ORED})(?:\..+)?$')


# Initialize this submodule.
_init()
