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
    Union,
)
from beartype._util.kind.maplike.utilmapfrozen import FrozenDict

# ....................{ HINTS                              }....................
#FIXME: Actually define these hints as proper type aliases *AFTER* we drop
#support for Python 3.11, please: e.g.,
#   type _ClawBeforelist = Dict[str, Union[FrozenSet[str], _ClawBeforelist]]

ClawBeforelistChainMap = ChainMap[
    str, Union[ChainMap[str, None], 'ClawBeforelistChainMap']]
'''
PEP-compliant recursive alias matching a **beforelist chain map** (i.e.,
mutable chain map mapping from strings to either set-like chain maps of strings
mapping to the :data:`None` singleton placeholder *or* yet another such
recursively nested chain map).
'''


ClawBeforelistFrozenDict = Dict[
    str, Union[FrozenSet[str], 'ClawBeforelistFrozenDict']]
'''
PEP-compliant recursive alias matching a **beforelist frozen dictionary** (i.e.,
immutable frozen dictionary mapping from strings to either frozen sets of
strings *or* yet another such recursively nested frozen dictionary).
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
CLAW_BEFORELIST_MODULE_TO_FUNC_DECORATOR_NAMES: (
    ClawBeforelistFrozenDict) = FrozenDict({
        # The third-party @mcp.tool decorator method of the FastMCP package.
        # See also: https://github.com/beartype/beartype/issues/540
        'mcp': frozenset(('tool',)),

        # The third-party @chain decorator method of the
        # "langchain_core.runnables" package.
        # See also: https://github.com/beartype/beartype/issues/541
        'langchain_core': FrozenDict({'runnables': frozenset(('chain',))}),
    })
'''
**Beforelist decorator function schema** (i.e., frozen dictionary mapping from
the fully-qualified name of each third-party package to either a frozen set of
the unqualified basename of each decorator-hostile function directly defined by
that package *or* yet another such recursively nested frozen dictionary).
'''


# The @beartype decorator *MUST* appear below these decorator methods:
CLAW_BEFORELIST_MODULE_TO_TYPE_TO_METHOD_DECORATOR_NAMES: (
    ClawBeforelistFrozenDict) = FrozenDict({
        # The third-party @task decorator method of the "celery.Celery" type.
        # See also: https://github.com/beartype/beartype/issues/500
        'celery': FrozenDict({'Celery': frozenset(('task',))}),

        # The third-party @command decorator method of the "typer.Typer" type.
        # See also: https://github.com/beartype/beartype/issues/436
        'typer': FrozenDict({'Typer': frozenset(('command',))}),
    })
'''
**Beforelist decorator method schema** (i.e., frozen dictionary mapping from the
fully-qualified name of each third-party module to the unqualified basename of
each type in that module to a tuple of the unqualified basenames of each
decorator method of that type which the :func:`beartype.beartype` decorator
*must* appear before within the chain of decorators for objects decorated by
that decorator).
'''
