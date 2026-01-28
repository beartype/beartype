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
from beartype._check.metadata.call.bearcallabc import BeartypeCallMetaABC
from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
from beartype._conf.confmain import BeartypeConf
from beartype._data.typing.datatyping import TypeException
from beartype._data.typing.datatypingport import Hint

# ....................{ SUBCLASSES                         }....................
#FIXME: Docstring us up, please. *sigh*
#FIXME: Implement us up, please. *sigh*
class BeartypeCallExternalMeta(BeartypeCallMetaABC):
    '''
    **Beartype external call metadata** (i.e., dataclass encapsulating *all*
    metadata for the first external callable on the call stack originating from
    any module or package *except* those residing in the :mod:`beartype`
    package).

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

        # Optional parameters.
        conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
        exception_cls: TypeException = BeartypeDecorHintForwardRefException,
        exception_prefix: str = '',
    ) -> Hint:

        # Avoid circular import dependencies.
        from beartype._check.forward.fwdresolve import (
            resolve_hint_pep484_ref_str)
        from beartype._check.forward.scope.fwdscopemake import (
            make_caller_external_scope_forward)

        # Forward scope relative to the first external scope on the call stack,
        # encapsulating a call to a public beartype callable by an external
        # callable originating from a third-party package or module.
        scope_forward = make_caller_external_scope_forward(
            hint=hint,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )

        # Defer to this low-level resolver.
        return resolve_hint_pep484_ref_str(
            hint=hint,
            conf=conf,
            scope_forward=scope_forward,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )
