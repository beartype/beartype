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

#FIXME: Improve module docstring, please.

# ....................{ IMPORTS                            }....................
from beartype.typing import Iterable
from importlib.abc import (
    Loader,
    MetaPathFinder,
)
from importlib.machinery import PathFinder
from sys import meta_path

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ FUNCTIONS                          }....................
#FIXME: Docstring us up, please.
#FIXME: Unit test us up, please.
def beartype_package(package_names: Iterable[str]) -> None:
    '''
    Recursively apply the :func:`beartype.beartype` decorator to all well-typed
    callables and classes defined by all submodules of all packages with the
    passed names.

    Parameters
    ----------
    package_names : Iterable[str]
        Iterable of the fully-qualified names of one or more packages to be
        type-checked by :func:`beartype.beartype`.
    '''

    #FIXME: Validate "package_names", please.

    #FIXME: This almost certainly conflicts with "pytest", which also attempts
    #to inject its assertion-rewriting import hook to the same index. In
    #reflection, it might be feasible for us to:
    #* Detect whether "meta_path[0] is
    #  _pytest.assertion.rewrite.AssertionRewritingHook".
    #* If so, monkey-patching "AssertionRewritingHook._find_spec" as follows:
    #      AssertionRewritingHook._find_spec = _BeartypeMetaPathFinder.find_spec
    #* Else, installing our import hook as below.
    #
    #The disadvantage, of course, is that *THAT WOULD BE EXTREMELY FRAGILE.*
    #Assuming that even works -- which it probably wouldn't. In any case,
    #consider submitting an upstream "pytest" issue on behalf of @beartype,
    #`ideas`, and `typeguard`.

    #FIXME: Pass "package_names" to _BeartypeMetaPathFinder(), please.
    # Prepend our import hook *BEFORE* all other import hooks.
    meta_path.insert(0, _BeartypeMetaPathFinder())

# ....................{ PRIVATE ~ classes                  }....................
#FIXME: Docstring us up, please.
#FIXME: Unit test us up, please.
class _BeartypeMetaPathFinder(MetaPathFinder, Loader):
    '''

    Attributes
    ----------
    '''

    pass
