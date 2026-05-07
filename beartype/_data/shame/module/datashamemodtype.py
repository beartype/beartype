#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Shameful module type blacklist globals** (i.e., immutable data structures defining
the initial user-configurable contents of blacklists preventing problematic
third-party classes defined by problematic third-party modules and packages
known to be hostile to runtime type-checking in general and :mod:`beartype`
specifically from being inappropriately type-checked by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: [CONF] Actually do allow users to configure *ALL* of the blacklists
#defined below by defining one new "BeartypeConf" option for each whose default
#values are those data structures defined below. Currently, the codebase just
#uses those data structures directly. *shrug*

# ....................{ IMPORTS                            }....................
from beartype._data.typing.datatyping import DictStrToFrozenSetStrs
from beartype._util.kind.maplike.utilmapfrozen import FrozenDict

# ....................{ DICTS                              }....................
BLACKLIST_MODULE_NAME_TO_TYPE_NAMES: DictStrToFrozenSetStrs = FrozenDict({
    # ....................{ ANTIPATTERN ~ decor-hostile    }....................
    # These third-party packages and modules widely employ the decorator-hostile
    # decorator antipattern throughout their codebases and are thus
    # runtime-hostile.

    # Older implementations of the object-oriented @fastmcp.FastMCP.tool
    # decorator method destructively transforms callable user-defined functions
    # and methods into *UNCALLABLE* FastMCP-specific instances of this type.
    # Why, FastMCP!? WHY!?!!?? *sigh*
    #
    # Note that this only applies to FastMCP <= 2.14.3. Newer FastMCP versions
    # guarantee decorator compatibility by preserving the type and thus
    # callability of decorated callables. Nonetheless, we *MUST* preserve this
    # kludge in perpetuity to preserve backward compatibility with older FastMCP
    # versions. Thankfully, doing so incurs no tangible harms elsewhere.
    #
    # See also:
    #     https://github.com/beartype/beartype/issues/540
    'fastmcp.tools.tool': frozenset(('FunctionTool',)),

    # The object-oriented @langchain_core.runnables.chain decorator method
    # destructively transforms callable user-defined functions and methods into
    # *UNCALLABLE* LangChain-specific instances of this type. Why, LangChain!?!
    'langchain_core.runnables.base': frozenset(('RunnableLambda',)),
})
'''
Frozen dictionary mapping from the fully-qualified name of each problematic
third-party package and module to a frozen set of the unqualified basenames of
all **beartype-blacklisted types** defined by that package or module. These
types are well-known to be hostile to runtime type-checking in general and
:mod:`beartype` specifically, usually due to employing one or more of the
following antipatterns:

* The **decorator-hostile decorator antipattern,** a harmful design pattern
  unofficially promoted throughout the large language model (LLM) community.
  This antipattern abuses the standard PEP-compliant decorator paradigm (which
  supports decorator chaining by permitting arbitrary decorators to be applied
  to other decorators) by prohibiting decorator chaining. Many open-source LLM
  APIs, for example, define decorator-hostile decorators destructively transform
  callable user-defined functions and methods into uncallable instances of
  non-standard types usable *only* by those APIs. Due to being uncallable *and*
  non-standard, those instances then obstruct trivial wrapping by the
  :func:`beartype.beartype` decorator.
'''


BLACKLIST_TYPE_MRO_ROOT_MODULE_NAME_TO_TYPE_NAMES: (
    DictStrToFrozenSetStrs) = FrozenDict({
    # ....................{ ANTIPATTERN ~ decor-hostile    }....................
    # These third-party packages and modules widely employ the decorator-hostile
    # decorator antipattern throughout their codebases and are thus
    # runtime-hostile.

    # The object-oriented @celery.Celery.task decorator method transforms
    # callable user-defined functions and methods into callable Celery-specific
    # instances of this type, known as Celery tasks. For better or worse, Celery
    # tasks masquerade as the user-defined callables they wrap and thus are
    # *ONLY* accessible as the root MRO item:
    #     # Define a trivial Celery task.
    #     >>> from celery import Celery
    #     >>> celery_server = Celery(broker='memory://')
    #     >>> @celery_server.task()
    #     >>> def muh_celery_task() -> None: pass
    #
    #     # Prove that Celery tasks lie about everything.
    #     >>> muh_celery_task.__module__
    #     celery.local  # <-- weird, but okay
    #     >>> muh_celery_task.__name__
    #     muh_celery_task  # <-- *LIAR*! you're actually a "Task" instance!!
    #     >>> muh_celery_task.__class__.__module__
    #     __main__  # <-- *LIAR*! you're actually a "Task" instance!!
    #     >>> muh_celery_task.__class__.__name__
    #     muh_celery_task  # <-- *LIAR*! you're actually a "Task" instance!!
    #     >>> muh_celery_task.__class__.__mro__
    #     (<class '__main__.muh_celery_task'>, <class
    #     'celery.app.task.Task'>, <class 'celery.app.task.Task'>, <class
    #     'object'>)  # <-- *FINALLY*. at last. the truth is revealed.
    'celery.app.task': frozenset(('Task',)),
})
'''
Frozen dictionary mapping from the fully-qualified name of each problematic
third-party package and module to a frozen set of the unqualified basenames of
all **beartype-blacklisted types** defined by that package or module such that
these high-level types masquerade as the low-level user-defined callables that
they wrap, typically by an even higher-level decorator wrapping callables with
those types.

These types hide themselves from public view and thus are *only* accessible as
the **root method-resolution order (MRO) item** (i.e., second-to-last item of
the ``__mro__`` dunder dictionary of these types, thus ignoring the ignorable
:class:`object` guaranteed to be the last item of all such dictionaries).

See Also
--------
:data:`.BLACKLIST_MODULE_NAME_TO_TYPE_NAMES`
    Further details.
'''
