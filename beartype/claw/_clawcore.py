#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Core beartype all-at-once API.**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
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
