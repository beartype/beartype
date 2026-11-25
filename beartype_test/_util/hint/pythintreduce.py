#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
:mod:`pytest` **continuous integration (CI) utilities.**
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype._check.cls.call.calldataabc import BeartypeCallDataABC
from beartype._check.cls.call.calldataexternal import (
    BEARTYPE_CALL_EXTERNAL_META)
from beartype._check.cls.hint.hintsane import HintSane
from beartype._check.convert._reduce.redmain import reduce_hint
from beartype._data.typing.datatypingport import Hint

# ....................{ REDUCERS                           }....................
def reduce_hint_call_external(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    call_curr: BeartypeCallDataABC = BEARTYPE_CALL_EXTERNAL_META,
    **kwargs
) -> HintSane:
    '''
    Lower-level type hint reduced (i.e., converted) relative to the external
    caller from the passed higher-level type hint if this hint is reducible *or*
    this hint as is otherwise (i.e., if this hint is irreducible).

    This reducer is a convenience wrapper for the more general-purpose
    :func:`.reduce_hint` reducer, principally intended to be called from unit
    tests. Specifically, this reducer defaults the ``call_curr`` parameter
    accepted by the :func:`.reduce_hint` reduce to the **beartype external call
    metadata singleton** (i.e., :data:`.BEARTYPE_CALL_EXTERNAL_META`). Doing so
    reduces :pep:`484-compliant forward reference type hints visitable from the
    passed type hint against the first external lexical scope on the call stack
    originating from a third-party package or module. This default is
    appropriate only for unit tests rather than real-world use cases.

    Caveats
    -------
    **The more fine-grained** :func:`.reduce_hint` **reducer should typically be
    called instead.** This more coarse-grained reducer drops the mandatory
    ``call_curr`` parameter required by the former, which is *not* necessarily a
    good thing. That parameter should typically be passed. Failing to pass that
    parameter drops essential metadata required to properly sanitize many kinds
    of insane type hints.

    Parameters
    ----------
    hint : Hint
        Type hint to be reduced.
    call_curr : BeartypeCallDataABC, default: BEARTYPE_CALL_EXTERNAL_META
        **Beartype call metadata** (i.e., dataclass aggregating *all* common
        metadata encapsulating the user-defined callable, type, or statement
        currently being type-checked by the end user). Defaults to the beartype
        external call metadata singleton, thus sanifying :pep:`484`-compliant
        stringified forward reference type hints against the local and global
        scope of the first third-party caller on the current call stack.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`.reduce_hint` reducer.

    Returns
    -------
    HintSane
        Either:

        * If this hint is ignorable, :data:`.HINT_SANE_IGNORABLE`.
        * Else if this unignorable hint is reducible to another hint, metadata
          encapsulating this reduction.
        * Else, this unignorable hint is irreducible. In this case, metadata
          encapsulating this hint unmodified.
    '''

    #FIXME: *WEIRD*. This is already the default. Why force this? No idea, yo.
    # Default to the beartype external call metadata singleton.
    kwargs['call_curr'] = BEARTYPE_CALL_EXTERNAL_META

    # Return this hint possibly reduced to a lower-level hint.
    return reduce_hint(hint=hint, **kwargs)
