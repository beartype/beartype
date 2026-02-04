#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator call metadata dataclass** (i.e., class aggregating *all*
metadata for the callable currently being decorated by the
:func:`beartype.beartype` decorator).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype._check.metadata.call.callmetaabc import BeartypeCallMetaABC
from beartype._conf.confmain import BeartypeConf
from beartype._data.typing.datatyping import TypeException
from beartype._data.typing.datatypingport import Hint

# ....................{ SUBCLASSES                         }....................
class BeartypeCallExternalMeta(BeartypeCallMetaABC):
    '''
    **Beartype external call metadata** (i.e., dataclass encapsulating *all*
    metadata for the first external lexical scope on the call stack originating
    from any third-party module or package *except* those residing in the
    :mod:`beartype` package).

    This dataclass aggregates specific metadata unique to the high-level public
    :mod:`beartype.door` API, including:

    * The :func:`beartype.door.die_if_unbearable` statement-level type-checker.
    * The :func:`beartype.door.is_bearable` statement-level type-checker.

    Design
    ------
    **This dataclass is a thread-safe singleton.** Third-party packages,
    modules, apps, APIs, endpoints, pipelines, and workflows commonly call the
    :func:`beartype.door.die_if_unbearable` and
    :func:`beartype.door.is_bearable` type-checkers inside performance-critical
    code paths. These type-checkers thus conform to fairly tight performance
    constraints. They must not idly squander either space or time complexity.
    Indeed, because the heaviness of object-oriented design is indeed heavy,
    they avoid instantiating unnecessary objects unnecessarily. To that end,
    this dataclass is only a singleton shared across all possible threads.

    This dataclass could instead be instantiated once for each unique call to
    these type-checkers. Doing so would enable this dataclass to internally
    cache the call-specific forward scope internally synthesized by the first
    call to the :meth:`resolve_hint_pep484_ref_str` method for efficient reuse
    across all subsequent calls to that method. However, doing so neglects the
    forest for the trees. Real-world forward references (and thus calls to the
    :meth:`resolve_hint_pep484_ref_str` method) are rare. Most real-world type
    hints are neither forward references *nor* transitively subscripted by
    forward references. Micro-optimizing for this edge case by memoizing forward
    scopes would anti-optimize the common case by requiring this dataclass be
    repeatedly re-instantiated rather than shared. We prefer the common case.

    This dataclass maintains *no* internal state to ensure its safe usability
    across threads.
    '''

    # ..................{ RESOLVERS                          }..................
    def resolve_hint_pep484_ref_str(
        self,

        # Mandatory parameters.
        hint: str,
        conf: BeartypeConf,

        # Optional parameters.
        exception_cls: TypeException = BeartypeDecorHintForwardRefException,
        exception_prefix: str = '',
    ) -> Hint:

        # Avoid circular import dependencies.
        from beartype._check.forward.fwdresolve import (
            resolve_hint_pep484_ref_str_caller_external)

        # Defer to this low-level resolver.
        return resolve_hint_pep484_ref_str_caller_external(
            hint=hint,
            conf=conf,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )

# ....................{ GLOBALS                            }....................
BEARTYPE_CALL_EXTERNAL_META = BeartypeCallExternalMeta()
'''
**Beartype external call metadata singleton** (i.e., public global constant
:class:`.BeartypeCallExternalMeta` instance intended to be the *only*
:class:`.BeartypeCallExternalMeta` instance instantiated for the life of the
active Python interpreter).

See Also
--------
:class:`.BeartypeCallExternalMeta`
    Further details.
'''
