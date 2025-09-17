#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **decorator position globals** (i.e., global constants defining the
initial user-configurable contents of the beforelist automating decorator
positioning for :mod:`beartype.claw` import hooks).

:mod:`beartype.claw` import hooks initialize user-configurable beforelists via
these globals of third-party decorators well-known to be **decorator-hostile**
(i.e., decorators hostile to other decorators by prematurely terminating
decorator chaining, such that *no* decorators may appear above these decorators
in any chain of one or more decorators).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Dict,
    Optional,
)
from beartype._util.kind.maplike.utilmapfrozen import FrozenDict
from beartype._conf.decorplace.confplacetrie import (
    BeartypeDecorPlacePackageTrie,
    BeartypeDecorPlaceTypeTrie,
)

# ....................{ HINTS                              }....................
#FIXME: Actually define these hints as proper type aliases *AFTER* we drop
#support for Python 3.11, please: e.g.,
#   type _ClawBeforelist = Dict[str, Union[FrozenSet[str], _ClawBeforelist]]

BeartypeDecorPlaceSubtrie = Optional[Dict[str, 'BeartypeDecorPlaceSubtrie']]
'''
PEP-compliant recursive alias matching a **beforelist subtrie** (i.e.,
corresponding value of some key-value pair signifying a child node of a parent
beforelist (sub)trie), constrained to be either:

* If this is a leaf child node terminating a branch of that (sub)trie,
  :data:`None`.
* If this is a stem child node perpetuating a branch of that (sub)trie, yet
  another such recursively nested dictionary mapping from the unqualified
  basenames of problematic third-party attributes imported into a scope of the
  currently visited module to yet another (sub)trie child node.
'''


BeartypeDecorPlaceTrie = Dict[str, Dict[str, BeartypeDecorPlaceSubtrie]]
'''
PEP-compliant recursive alias matching a **beforelist trie** (i.e., recursive
tree structure whose nodes are the unqualified basenames of problematic
third-party attributes imported into a scope of the currently visited module,
defined as a frozen dictionary mapping from strings to either yet another such
recursively nested frozen dictionary *or* :data:`None` signifying a terminal
leaf node).

Note that the root trie is guaranteed to map from strings to *only* nested
frozen dictionaries (rather than to both nested frozen dictionaries and
:data:`None`). Consequently, this hint intentionally differentiates between
matching the root and non-root nesting levels of this trie.
'''

# ....................{ TRIES                              }....................
#FIXME: The root frozen dictionary should probably be a new unique
#"class BeartypeDecorPlacePackagesTrie(FrozenDict):" subclass. We don't require
#that at the moment and thus can't be bothered. That said, going public with
#this will necessitate doing this for future extensibility.
DECOR_HOSTILE_ATTR_NAME_TRIE: BeartypeDecorPlaceTrie = FrozenDict({
    # ....................{ FUNCTIONS                      }....................
    # Third-party decorator-hostile decorator *FUNCTIONS* directly defined by
    # functional (i.e., *NOT* object-oriented) APIs.

    # The third-party @chain decorator function of the
    # "langchain_core.runnables" package of the LangChain API. See also:
    #     https://github.com/beartype/beartype/issues/541
    'langchain_core': BeartypeDecorPlacePackageTrie(
        {'runnables': BeartypeDecorPlacePackageTrie({'chain': None})}),

    # ....................{ METHODS                        }....................
    # Third-party decorator-hostile decorator *METHODS* directly defined by
    # types directly defined by object-oriented (OO) APIs.

    # The third-party @task decorator method of the "celery.Celery" type of the
    # Celery API. See also:
    #     https://github.com/beartype/beartype/issues/500
    'celery': BeartypeDecorPlacePackageTrie({
        'Celery': BeartypeDecorPlaceTypeTrie({'task': None})}),

    # The third-party @.tool decorator function of the "fastmcp.FastMCP" type of
    # the FastMCP API. See also:
    #     https://github.com/beartype/beartype/issues/540
    'fastmcp': BeartypeDecorPlacePackageTrie({
        'FastMCP': BeartypeDecorPlaceTypeTrie({'tool': None})}),
})
'''
**Decorator beforelist** (i.e., frozen dictionary mapping from the unqualified
basename of each third-party (sub)package and (sub)module transitively defining
one or more decorator-hostile decorators to either yet another such recursively
nested frozen dictionary *or* :data`None`, in which case the corresponding key
is the unqualified basename of a decorator-hostile decorator directly defined by
that (sub)package, (sub)module, type, or instance).
'''
