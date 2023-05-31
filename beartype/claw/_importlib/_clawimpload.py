#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype module loaders** (i.e., :mod:`importlib`-compliant classes
dynamically decorating all typed callables and classes of all submodules of all
packages previously registered in our global package trie by the
:func:`beartype.beartype` decorator via abstract syntax tree (AST) transformers
defined by the :mod:`beartype.claw._ast.clawastmain` submodule).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from ast import PyCF_ONLY_AST
from beartype.claw._ast.clawastmain import BeartypeNodeTransformer
from beartype.claw._pkg.clawpkgtrie import get_package_conf_or_none
from beartype.meta import VERSION
from beartype.typing import Optional
from beartype._conf.confcls import BeartypeConf
from importlib import (  # type: ignore[attr-defined]
    _bootstrap_external,  # pyright: ignore[reportGeneralTypeIssues]
)
from importlib.machinery import SourceFileLoader
from importlib.util import decode_source
from types import CodeType

# Original cache_from_source() function defined by the private (*gulp*)
# "importlib._bootstrap_external" submodule, preserved *BEFORE* temporarily
# replacing that function with our beartype-specific variant below.
from importlib.util import cache_from_source as cache_from_source_original

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

    The :func:`beartype_package` function injects a low-level **import path
    hook** (i.e., factory closure instantiating this class as an item of the
    standard :mod:`sys.path_hooks` list) to the front of that list. When called
    by a higher-level parent **import metapath hook** (i.e., object suitable for
    use as an item of the standard :mod:`sys.meta_path` list), that closure:

    #. Instantiates one instance of the standard
       :class:`importlib._bootstrap_external.FileFinder` class for each
       **imported Python package** (i.e., package on the :mod:`sys.path` list).
       The :meth:``importlib._bootstrap_external.FileFinder.find_spec` method of
       that instance then returns this :class:`BeartypeSourceFileLoader` class
       uninstantiated for each **imported Python package submodule** (i.e.,
       submodule directly contained in that package).
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
    _conf_beartype_if_module_hooked : Optional[BeartypeConf]
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
        :meth:`get_code` method to communicate this configuration to the child
        :meth:`source_to_code` method, which fails to accept and thus has *no*
        access to this module name. The superclass implementation of the
        :meth:`get_code` method then internally calls our override of the
        :meth:`source_to_code` method, which accesses this instance variable to
        decide whether and how to type-check that module.

        Ordinarily, this approach would be fraught with fragility. For example,
        what if something *other* than the :meth:`get_code` method called the
        :meth:`source_to_code` method? Thankfully, that is *not* a concern here.
        :meth:`source_to_code` is only called by :meth:`get_code` in the
        :mod:`importlib` codebase. Ergo, :meth:`source_to_code` should ideally
        have been privatized (e.g., as ``_source_to_code()``).

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

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, *args, **kwargs) -> None:
        '''
        Initialize this beartype source file loader.

        All passed parameters are passed as is to the superclass method, which
        then calls our lower-level :meth:`source_to_code` subclass method
        overridden below.
        '''

        # Initialize our superclass with all passed parameters.
        super().__init__(*args, **kwargs)

        # Nullify all subclass-specific instance variables for safety.
        self._conf_beartype_if_module_hooked: Optional[BeartypeConf] = None

    # ..................{ LOADER API                         }..................
    # The importlib._bootstrap_external.*Loader API declares the low-level
    # exec_module() method, which accepts an "importlib._bootstrap.ModuleSpec"
    # instance created and returned by a prior call to the higher-level
    # find_spec() method documented above; the exec_module() method then uses
    # that module spec to create and return a fully imported module object
    # (i.e., "types.ModuleType" instance). To do so:
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
        :mod:`beartype.claw._pkg.clawpkghook` submodule (e.g., by a call to the
        :func:`beartype.claw.beartype_package` function). Specifically:

        * If *no* parent package transitively containing that module has been
          registered, this method fully defers to the superclass
          :meth:`SourceLoader.get_code` method.
        * Else, one or more parent packages transitively containing that module
          have been registered. In this case, this method (in order):

          #. Temporarily monkey-patches (i.e., replaces) the
             private :func:`importlib._bootstrap_external.cache_from_source`
             function with our beartype-specific
             :func:`_cache_from_source_beartype` variant.
          #. Calls the superclass :meth:`SourceLoader.get_code` method, which:

             #. Calls our override of the lower-level superclass
                :meth:`SourceLoader.source_to_code` method.

          #. Restores the
             :func:`importlib._bootstrap_external.cache_from_source` function to
             its original implementation.

        Motivation
        ----------
        The temporary monkey-patch applied by this method is strongly inspired
        by a suspiciously similar temporary monkey-patch applied by the external
        :meth:`typeguard.importhook.TypeguardLoader.exec_module` method authored
        by the incomparable @agronholm (Alex Grönholm), who writes:

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

        This monkey-patch suffixing ``{optimization_markers}`` with the
        substring ``"-beartype-{BEARTYPE_VERSION}"``, which additionally
        uniquifies the filename of this bytecode file to the abstract syntax
        tree (AST) transformation applied by this version of :mod:`beartype`.
        Why? Because external callers can trivially enable and disable that
        transformation for any module by either calling or not calling the
        :func:`beartype.claw.beartype_package` function with the name of a
        package transitively containing that module. Compiling a @beartyped
        module to the same bytecode file as the non-@beartyped variant of that
        module would erroneously persist @beartyping to that module -- even
        *after* removing the relevant call to the
        :func:`beartype.claw.beartype_package` function! Clearly, that's awful.
        Enter @agronholm's phenomenal patch, stage left.

        We implicitly trust @agronholm to get that right in a popular project
        stress-tested across hundreds of open-source projects over the past
        several decades. So, we avoid explicit thread-safe locking here.

        Lastly, note there appears to be *no* other means of safely
        implementing this behaviour *without* violating Don't Repeat Yourself
        (DRY). Specifically, doing so would require duplicating most of the
        entirety of the *extremely* non-trivial nearly 100 line-long
        :meth:`importlib._bootstrap_external.SourceLoader.get_code` method.
        Since duplicating non-trivial and fragile code inherently tied to a
        specific CPython version is considerably worse than applying a trivial
        one-line monkey-patch, first typeguard and now @beartype strongly prefer
        this monkey-patch. Did we mention that @agronholm is amazing? Because
        that really bears repeating. May the name of Alex Grönholm live eternal!
        '''

        # Fully-qualified name of the parent package of the module with the
        # passed fully-qualified name, defined as either...
        package_name = (
            # If that module is a submodule of a package, then the expression
            # "fullname.rpartition('.')[0]" necessarily yields the
            # fully-qualified name of that package;
            fullname.rpartition('.')[0] or

            #FIXME: Actually, *IS* it feasible for a top-level module to be
            #registered as a package? Certainly, our API permits that -- but how
            #does "importlib" machinery actually import top-level modules? They
            #don't have packages, but *ALL* "importlib" machinery is based on
            #containing packages. This is a fascinating edge case, so let's
            #investigate further if we ever grep up the time.

            # Else, that module is a top-level module with *NO* parent package.
            # In this case, since the above expression
            # "fullname.rpartition('.')[0]" erroneously yields the empty string,
            # fallback to the fully-qualified name of that module as is.
            # Although unlikely, it is feasible for a top-level module to be
            # registered as a package by a prior call resembling:
            #     beartype.claw.beartype_package(fullname)
            fullname
        )

        # Beartype configuration with which to type-check that module if the
        # parent package of that module was previously registered *OR* "None"
        # otherwise (i.e., if this function preserves that module unmodified).
        self._conf_beartype_if_module_hooked = get_package_conf_or_none(
            package_name)

        # If that module has *NOT* been registered for type-checking, preserve
        # that module as is by simply deferring to the superclass method
        # *WITHOUT* monkey-patching cache_from_source(). This isn't only an
        # optimization, although it certainly is that as well. This is critical.
        # Why? Because modules *NOT* being @beartyped should remain compiled
        # under their standard non-@beartyped bytecode filenames.
        if self._conf_beartype_if_module_hooked is None:
            return super().get_code(fullname)
        # Else, that module has been registered for type-checking. In this
        # case...
        #
        # Note that the logic below requires inefficient exception handling (as
        # well as a potentially risky monkey-patch) and is thus performed *ONLY*
        # when absolutely necessary.
        else:
            # Temporarily monkey-patch away the cache_from_source() function.
            #
            # Note that @agronholm (Alex Grönholm) claims that "the import lock
            # should make this monkey patch safe." We're trusting you here, man!
            _bootstrap_external.cache_from_source = _cache_from_source_beartype

            # Attempt to defer to the superclass method.
            try:
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

        The higher-level :meth:`get_code` superclass method internally calls
        this lower-level subclass method.

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

        # If that module has *NOT* been registered for type-checking, preserve
        # that module as is by simply deferring to the superclass method.
        if self._conf_beartype_if_module_hooked is None:
            return super().source_to_code(  # type: ignore[call-arg]
                data=data, path=path, _optimize=_optimize)  # pyright: ignore[reportGeneralTypeIssues]
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
            conf_beartype=self._conf_beartype_if_module_hooked)

        # Abstract syntax tree (AST) modified by this transformer.
        module_ast_beartyped = ast_beartyper.visit(module_ast)

        #FIXME: *THIS IS BAD, BRO.* For one thing, this is slow. Recursion is
        #slow. It's also dangerous. We shouldn't do it more than we have to. Now
        #we're recursing over the entire AST tree twice: once in our AST
        #transformation above (which is unavoidable) and again in the call to
        #fix_missing_locations() here (which probably is avoidable). Instead, we
        #should fold the logic of fix_missing_locations() directly into our AST
        #transformation. Specifically, our AST transformation should:
        #* For each newly generated AST node, non-recursively propagate the line
        #  and column numbers of that node's parent node onto that node.
        #FIXME: Fascinating. It would seem that we need to propagate these
        #*FOUR* attributes: "lineno", "end_lineno", "col_offset", and
        #"end_col_offset". Note that the "end_"-prefixed attributes may only be
        #available under newer Python versions. Say, Python ≥ 3.9 or 3.10?
        #Further research is required, clearly. Fortunately, the implementation
        #of the ast.fix_missing_locations() function is trivial. It shouldn't be
        #terribly arduous to embed equivalent functionality in our AST
        #transformation, assuming we think we know what we're doing. (We don't.)

        # Recursively propagate the line and column numbers of all parent nodes
        # in this tree to their children that failed to define these numbers
        # *BEFORE* calling the compile() builtin, which requires these numbers
        # to be defined on all AST nodes supporting these numbers. All AST nodes
        # supporting these numbers define these numbers *EXCEPT* those AST nodes
        # programmatically generated by our AST transformation, which currently
        # leaves these numbers undefined due to programmer laziness.
        #fix_missing_locations(module_ast_beartyped)

        # Code object compiled from this transformed AST.
        module_codeobj = compile(
            module_ast_beartyped,
            path,
            'exec',
            # Prevent these contents from inheriting the effects of any
            # "from __future__ import" statements in effect in beartype itself.
            dont_inherit=True,
            optimize=_optimize,
        )

        # Return this code object.
        return module_codeobj

# ....................{ PRIVATE ~ cachers                  }....................
#FIXME: Unit test us up, please.
def _cache_from_source_beartype(*args, **kwargs) -> str:
    '''
    Beartype-specific variant of the
    :func:`importlib._bootstrap_external.cache_from_source` function applying a
    beartype-specific optimization marker to that function.

    This, in turn, ensures that submodules residing in packages registered by a
    prior call to the :func:`beartype_package` function are
    compiled to files with the filetype ``".pyc{optimization}-beartype"``,
    where ``{optimization}`` is the original ``optimization`` parameter passed
    to this function call.
    '''

    # Original optimization parameter passed to this function call if any *OR*
    # the empty string otherwise.
    optimization_marker_old = kwargs.get('optimization', '')

    # New optimization parameter applied by this monkey-patch of that function,
    # uniquifying that parameter with a beartype-specific suffix.
    kwargs['optimization'] = f'{optimization_marker_old}-beartype-{VERSION}'

    # Defer to the implementation of the original cache_from_source() function.
    return cache_from_source_original(*args, **kwargs)
