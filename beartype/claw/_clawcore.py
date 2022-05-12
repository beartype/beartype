#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Core beartype all-at-once API.**

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
from beartype.typing import (
    Iterable,
    Union,
)
from importlib import invalidate_caches
from importlib.machinery import (
    SOURCE_SUFFIXES,
    FileFinder,
    SourceFileLoader,
)
from sys import (
    path_hooks,
    path_importer_cache,
)

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ FUNCTIONS                          }....................
#FIXME: Unit test us up, please.
def beartype_package(package_names: Iterable[str]) -> None:
    '''
    Register a new **beartype import path hook** (i.e., callable inserted to the
    front of the standard :mod:`sys.path_hooks` list recursively applying the
    :func:`beartype.beartype` decorator to all well-typed callables and classes
    defined by all submodules of all packages with the passed names on the first
    importation of those submodules).

    Parameters
    ----------
    package_names : Iterable[str]
        Iterable of the fully-qualified names of one or more packages to be
        type-checked by :func:`beartype.beartype`.

    See Also
    ----------
    https://stackoverflow.com/a/43573798/2809027
        StackOverflow answer strongly inspiring the low-level implementation of
        this function with respect to inscrutable :mod:`importlib` machinery.
    '''

    #FIXME: Validate "package_names", please.

    #FIXME: Pass "package_names" to _BeartypeMetaPathFinder(), please. Uhm...
    #how exactly do we do that, though? *OH. OH, BOY.* The
    #FileFinder.path_hook() creates a closure that, when invoked, ultimately
    #calls the FileFinder._get_spec() method that instantiates our loader in the
    #bog-standard way ala:
    #    loader = loader_class(fullname, path)
    #So, that doesn't leave us with any means of intervening in the process.
    #We have two options here:
    #* [CRUDE OPTION] The crude option is to cache all passed package names into
    #  a new private global thread-safe "_package_names" list, which can only be
    #  safely accessed by a "threading.{R,}Lock" context manager. Each
    #  "_BeartypeSourceFileLoader" instance then accesses that global list. This
    #  isn't necessarily awful. That said...
    #* [FINE OPTION] The fine option is to do what we probably already want to
    #  do and adopt the stacking solution described both above and at:
    #      https://stackoverflow.com/a/48671982/2809027
    #  This approach requires considerably more work, because we then need to
    #  completely avoid all existing "importlib" machinery and write our own.
    #  That's not necessarily a bad thing, though -- because all that machinery
    #  is insufficient for our needs, anyway! So, we should probably "just do
    #  the right thing" and adopt the fine solution. It's fine, yo.

    # 2-tuple of the undocumented format expected by the FileFinder.path_hook()
    # class method called below, associating our beartype-specific source file
    # loader with the platform-specific filetypes of all sourceful Python
    # packages and modules. We didn't do it. Don't blame the bear.
    LOADER_DETAILS = (_BeartypeSourceFileLoader, SOURCE_SUFFIXES)

    # Prepend a new import hook (i.e., factory closure encapsulating this
    # loader) *BEFORE* all other import hooks.
    path_hooks.insert(0, FileFinder.path_hook(LOADER_DETAILS))

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

    Attributes
    ----------
    package_names : Iterable[str]
        Iterable of the fully-qualified names of one or more packages to be
        type-checked by :func:`beartype.beartype`.
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,

        # Mandatory keyword-only parameters.
        *,
        package_names: Iterable[str],
        **kwargs
    ) -> None:
        '''
        Initialize this loader against the passed package list.

        Parameters
        ----------
        package_names : Iterable[str]
            Iterable of the fully-qualified names of one or more packages to be
            type-checked by :func:`beartype.beartype`.

        All remaining keyword parameters are passed as is to the
        :func:`importlib.machinery.FileLoader.__init__` method.
        '''

        # Initialize the transitive "FileLoader" superclass of our direct
        # "SourceFileLoader" superclass with all remaining keyword parameters.
        super().__init__(**kwargs)

        # Classify all subclass-specific parameters.
        self.package_names = package_names


    def get_data(self, path: Union[bytes, str]) -> bytes:
        '''
        Plaintext decoded contents of the Python **sourceful Python package or
        module** (i.e., package or module backed by a ``.py``-suffixed source
        file) with the passed name, transformed in-place by our abstract syntax
        tree (AST) transformation automatically applying the
        :func:`beartype.beartype` decorator to all applicable objects of that
        package or module.

        Parameters
        ----------
        path : Union[bytes, str]
            Absolute or relative filename of the sourceful Python package or
            module to be decoded.

        Returns
        ----------
        bytes
            Plaintext decoded contents of this package or module.
        '''

        # Plaintext decoded contents of this package or module.
        module_source = super().get_data(path)

        #FIXME: Apply our abstract syntax tree (AST) transformation here! \o/

        # Return these contents.
        return module_source
