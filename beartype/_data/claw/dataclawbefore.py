#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype import hook beforelist globals** (i.e., global constants defining the
initial contents of the beforelist automating decorator positioning for
:mod:`beartype.claw` import hooks).

:mod:`beartype.claw` import hooks initialize user-configurable beforelists via
these globals of third-party decorators well-known to be **decorator-hostile**
(i.e., decorators hostile to other decorators by prematurely terminating
decorator chaining, such that *no* decorators may appear above these decorators
in any chain of one or more decorators).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    ChainMap,
    Dict,
    FrozenSet,
    Optional,
    Union,
)
from beartype._util.kind.maplike.utilmapfrozen import FrozenDict

# ....................{ HINTS                              }....................
#FIXME: Actually define these hints as proper type aliases *AFTER* we drop
#support for Python 3.11, please: e.g.,
#   type _ClawBeforelist = Dict[str, Union[FrozenSet[str], _ClawBeforelist]]

ClawBeforelistTrie = Dict[str, Dict[str, 'ClawBeforelistSubtrie']]
'''
PEP-compliant recursive alias matching a **beforelist trie** (i.e., recursive
tree structure whose nodes are the unqualified basenames of problematic
third-party attributes imported into a scope of the currently visited module,
defined as a frozen dictionary mapping from strings to either the :data:`None`
singleton placeholder signifying a terminal leaf node *or* yet another such
recursively nested frozen dictionary).

Note that the root trie is guaranteed to map from strings to *only* nested
frozen dictionaries (rather than to both nested frozen dictionaries and
:data:`None`). Consequently, this hint intentionally differentiates between
matching the root and non-root nesting levels of this trie.
'''


ClawBeforelistSubtrie = Optional[Dict[str, 'ClawBeforelistSubtrie']]
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


ClawBeforelistImportedAttrNameTrie = ChainMap[str, 'ClawBeforelistSubtrie']
'''
PEP-compliant recursive alias matching a **beforelist imported attribute name
trie** (i.e., recursive tree structure whose nodes are the unqualified basenames
of problematic third-party attributes imported into a scope of the currently
visited module, defined as a chain map mapping from strings to either the
:data:`None` singleton placeholder signifying a terminal leaf node *or* yet
another such recursively nested dictionary).
'''

# ....................{ DICTS                              }....................
#FIXME: *INSUFFICIENT.* Close, but no cigar. Non-trivial end user logic could
#perform imports resembling:
#    import langchain
#
#    @langchain.runnables.chain
#    def problem_func(...): ...
#
#This currently simplistic data structure fails to account for edge cases like
#that. Accounting for that would probably require generalizing this to resemble:
CLAW_BEFORELIST_MODULE_TO_FUNC_DECOR_NAMES: (
    ClawBeforelistTrie) = FrozenDict({
        # The third-party @mcp.tool decorator method of the FastMCP package.
        # See also: https://github.com/beartype/beartype/issues/540
        'mcp': FrozenDict({'tool': None}),

        # The third-party @chain decorator method of the
        # "langchain_core.runnables" package.
        # See also: https://github.com/beartype/beartype/issues/541
        'langchain_core': FrozenDict(
            {'runnables': FrozenDict({'chain': None})}),
    })
'''
**Decorator function beforelist** (i.e., frozen dictionary mapping from the
unqualified basename of each third-party (sub)package and (sub)module
transitively defining one or more decorator-hostile decorator functions to
either a frozen set of the unqualified basenames of those functions *or* yet
another such recursively nested frozen dictionary).
'''


#FIXME: Revise docstring, please. *shrug*
# The @beartype decorator *MUST* appear below these decorator methods:
CLAW_BEFORELIST_MODULE_TO_TYPE_TO_METHOD_DECOR_NAMES: (
    ClawBeforelistTrie) = FrozenDict({
        # The third-party @task decorator method of the "celery.Celery" type.
        # See also: https://github.com/beartype/beartype/issues/500
        'celery': FrozenDict({'Celery': FrozenDict({'task': None})}),

        # The third-party @command decorator method of the "typer.Typer" type.
        # See also: https://github.com/beartype/beartype/issues/436
        'typer': FrozenDict({'Typer': FrozenDict({'command': None})}),
    })
'''
**Decorator method beforelist** (i.e., frozen dictionary mapping from the
fully-qualified name of each third-party module to the unqualified basename of
each type in that module to a tuple of the unqualified basenames of each
decorator method of that type which the :func:`beartype.beartype` decorator
*must* appear before within the chain of decorators for objects decorated by
that decorator).
'''
