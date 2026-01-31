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
from beartype._check.forward.reference.fwdrefmake import (
    make_forwardref_subbable_subtype)
from beartype._check.metadata.call.callmetaabc import BeartypeCallMetaABC
from beartype._check.metadata.hint.hintsane import (
    HintSane,
)
from beartype._conf.confmain import BeartypeConf
from beartype._data.typing.datatyping import HintPep484Ref
from beartype._util.hint.pep.proposal.pep484.forward.pep484refgeneral import (
    get_hint_pep484_ref_names_relative)
from typing import ForwardRef

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

    #FIXME: Under Python >= 3.14, instead call a completely different
    #make_forwardref_annotationlib_subtype() factory function. See also the
    #existing "pep484refcanonic" submodule for further details. *sigh*

    # If this hint is a PEP 484-compliant object-oriented forward reference
    # (rather than a stringified forward reference)...
    if isinstance(hint, ForwardRef):
        # Possibly undefined fully-qualified module name and possibly unqualified
        # classname referred to by this forward reference.
        ref_module_name, ref_type_name = get_hint_pep484_ref_names_relative(
            hint=hint, exception_prefix=exception_prefix)

        # If this reference was instantiated with a module name, this classname
        # is relative to that module. The type referred to by this reference can
        # be dynamically imported without disambiguity at some later time (e.g.,
        # when the currently decorated callable is called) by a forward
        # reference proxy directly instantiated now. In this case...
        if ref_module_name:
            # Reduce this runtime-unusable PEP 484-compliant object-oriented
            # forward reference to a runtime-usable forward reference proxy.
            hint = make_forwardref_subbable_subtype(
                scope_name=ref_module_name, hint_name=ref_type_name)

            # Return this proxy directly. All logic below assumes that "hint"
            # is now a stringified forward reference.
            return hint
        # Else, this reference was instantiated with *NO* module name. This
        # classname is relative to an unknown module and thus currently
        # ambiguous. This ambiguity can *ONLY* be resolved by dynamically
        # evaluating this classname in the local and global scope of the
        # callable, type, or statement currently being type-checked by the end
        # user. To that end, we:
        # 1. Reduce this runtime-unusable PEP 484-compliant object-oriented
        #    forward reference to its equally runtime-unusable (yet mildly more
        #    useful) ambiguous classname here.
        # 2. Reduce this ambiguous classname to a forward reference proxy below.
        else:
            hint = ref_type_name
    # Else, this hint is a stringified forward reference.
    #
    # In any case, this hint should now be a stringified forward reference.

    # Guarantee this to be the case. We've had enough surprises for one decade.
    assert isinstance(hint, str), (
        f'{exception_prefix}PEP 484 forward reference type hint {repr(hint)} '
        f'not stringified.'
    )

    # Either:
    # * If this stringified forward reference refers to an attribute that has
    #   already been defined in the local and global scope of the callable,
    #   type, or statement currently being type-checked by the end user, that
    #   attribute directly (e.g., the "list" builtin type for the stringified
    #   forward reference "list[set[str]]").
    # * Else, this stringified forward reference refers to an attribute that has
    #   yet to be defined in that local and global scope. In this case, a
    #   runtime-usable forward reference proxy encapsulating this
    #   runtime-unusable stringified forward reference.
    hint_resolved = call_meta.resolve_hint_pep484_ref_str(
        hint=hint, conf=conf, exception_prefix=exception_prefix)

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
