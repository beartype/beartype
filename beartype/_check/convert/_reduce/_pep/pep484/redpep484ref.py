#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **forward reference reducers** (i.e.,
low-level callables converting :pep:`484`-compliant forward references to
lower-level type hints more readily consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.metadata.call.bearcallabc import BeartypeCallMetaABC
from beartype._check.metadata.hint.hintsane import (
    HintSane,
)
from beartype._conf.confmain import BeartypeConf
from beartype._data.typing.datatyping import HintPep484Ref

# ....................{ REDUCERS ~ forwardref              }....................
#FIXME: Unit test us up, please.
def reduce_hint_pep484_ref(
    hint: HintPep484Ref,
    call_meta: BeartypeCallMetaABC,
    conf: BeartypeConf,
    exception_prefix: str,
    **kwargs
) -> HintSane:
    '''
    Reduce the passed :pep:`484`-compliant **forward reference hint** (i.e.,
    object indirectly referring to a user-defined type that typically has yet to
    be defined) to the object this reference refers to if that object is
    efficiently accessible at this early decoration time without unsafe dynamic
    importation of third-party packages or modules *or* preserve this reference
    as is otherwise.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), due to requiring contextual parameters and
    thus being fundamentally unmemoizable.

    Parameters
    ----------
    hint : Hint
        Forward reference type hint to be reduced.
    call_meta : BeartypeCallMetaABC
        **Beartype call metadata** (i.e., dataclass aggregating *all* common
        metadata encapsulating the user-defined callable, type, or statement
        currently being type-checked by the end user).
    conf : BeartypeConf, default: BEARTYPE_CONF_DEFAULT
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object).
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    All remaining passed arguments are silently ignored.

    Returns
    -------
    HintSane
        Sanified hint metadata encapsulating the non-string type hint to which
        this forward reference dynamically resolves, relative to the local and
        global scope of the currently type-checked callable, type, or statement.
    '''

    #FIXME: As the method name implies, this almost certainly *ONLY* handles
    #stringified forward references. "typing.ForwardRef" instances thus require
    #additional handling. We'll probably need to:
    #* Under Python >= 3.14, instead call a completely different
    #  make_forwardref_annotationlib_subtype() factory function. *sigh*
    #* Under Python <= 3.13, instead call a completely different
    #  make_forwardref_subbable_subtype() factory function. *sigh*:
    #
    #*SEE THE EXISTING "pep484refcanonic" SUBMODULE FOR FIXME INSTRUCTIONS.* \o/
    hint_resolved = call_meta.resolve_hint_pep484_ref_str(
        hint=hint,
        conf=conf,
        exception_prefix=exception_prefix,
    )

    # Sanified hint metadata encapsulating the non-string type hint to which
    # this forward reference dynamically resolves.
    hint_sane = HintSane(  # type: ignore[assignment]
        hint=hint_resolved,
        # Type-checking code dynamically generated for a forward reference is
        # contextually relative to the local and global scope of the currently
        # type-checked callable, type, or statement and thus *CANNOT* be cached
        # across all forward references.
        is_cacheable_check_expr=False,
    )

    # Return this metadata.
    return hint_sane
