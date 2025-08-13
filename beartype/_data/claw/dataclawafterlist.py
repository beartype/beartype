#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype import hook afterlist globals** (i.e., global constants defining the
initial contents of the afterlist automating decorator positioning for
:mod:`beartype.claw` import hooks).

:mod:`beartype.claw` import hooks initialize user-configurable afterlists via
these globals of third-party decorators well-known to be **decorator-hostile**
(i.e., decorators hostile to other decorators by prematurely terminating
decorator chaining, such that *no* decorators may appear above these decorators
in any chain of one or more decorators).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.typing.datatyping import (
    DictStrToStr,
    DictStrToStrToStr,
)
from beartype._util.kind.map.utilmapfrozen import FrozenDict

# ....................{ TODO                               }....................
#FIXME: Actually use these data structures somewhere, please! *sigh*

# ....................{ DICTS                              }....................
# The @beartype decorator *MUST* appear below these decorator functions:
CLAW_AFTERLIST_MODULE_TO_FUNC_DECORATOR_NAME: DictStrToStr = (
    FrozenDict({
        # The third-party @mcp.tool decorator method of the FastMCP package.
        # See also: https://github.com/beartype/beartype/issues/540
        'mcp': 'tool',

        # The third-party @chain decorator method of the
        # "langchain_core.runnables" package.
        # See also: https://github.com/beartype/beartype/issues/541
        'langchain_core.runnables': 'chain',
    }))
'''
**Afterlist decorator function schema** (i.e., frozen dictionary mapping from
the fully-qualified name of each third-party module to the unqualified basename
of each decorator function of that module which the :func:`beartype.beartype`
decorator *must* appear after within the chain of decorators for objects
decorated by that decorator).
'''


# The @beartype decorator *MUST* appear below these decorator methods:
CLAW_AFTERLIST_MODULE_TO_TYPE_TO_METHOD_DECORATOR_NAME: DictStrToStrToStr = (
    FrozenDict({
        # The third-party @task decorator method of the "celery.Celery" type.
        # See also: https://github.com/beartype/beartype/issues/500
        'celery': {'Celery': 'task'},

        # The third-party @command decorator method of the "typer.Typer" type.
        # See also: https://github.com/beartype/beartype/issues/436
        'typer': {'Typer': 'command'},
    }))
'''
**Afterlist decorator method schema** (i.e., frozen dictionary mapping from the
fully-qualified name of each third-party module to the unqualified basename of
each type in that module to the unqualified basename of each decorator method of
that type which the :func:`beartype.beartype` decorator *must* appear after
within the chain of decorators for objects decorated by that decorator).
'''
