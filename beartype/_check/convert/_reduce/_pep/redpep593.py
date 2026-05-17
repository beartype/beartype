#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`593`-compliant **type metahint reducers** (i.e., low-level
low-level callables converting higher-level type hints created by subscripting
the :obj:`typing.Annotated` type hint factory to lower-level type hints more
readily consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Iteratively flatten *ALL* nested "Annotated[...]" child hints until no
#such hints remain to be flattened: e.g.,
#    # Flatten this non-flat structure...
#    Annotated[Annotated[Annotated[int, float], str], bool]
#
#    # ...into this flat structure.
#    Annotated[int, float, str, bool]
#
#Don't bother until someone loudly complains, of course. We do nothing loudly!

# ....................{ IMPORTS                            }....................
from beartype._check.cls.hint.hintsane import HintSane
from beartype._data.check.error.dataerrmagic import EXCEPTION_PLACEHOLDER
from beartype._data.typing.datatypingport import Hint
from beartype._util.hint.pep.proposal.pep593 import (
    get_hint_pep593_metahint,
    is_hint_pep593_beartype,
)
from typing import Optional

# ....................{ REDUCERS                           }....................
def reduce_hint_pep593_annotated(
    hint: Hint, hint_parent_sane: Optional[HintSane], **kwargs) -> Hint:
    '''
    Reduce the passed :pep:`593`-compliant **type metahint** (i.e., subscription
    of the :obj:`typing.Annotated` hint factory) to a lower-level type hint more
    readily digestible by :mod:`beartype`.

    This reducer reduces this metahint to the first child type hint subscripting
    this metahint if this metahint is subscripted by *no* **beartype
    validators** (i.e., :mod:`beartype.vale` objects), in which case *all* child
    type hints following the first are safely ignorable by :mod:`beartype`.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as the implementation trivially reduces to a
    one-liner.

    Parameters
    ----------
    hint : Hint
        Type hint to be reduced.
    hint_parent_sane : Optional[HintSane]
        Either:

        * If the passed hint is a **root** (i.e., top-most parent hint of a tree
          of child hints), :data:`None`.
        * Else, the passed hint is a **child** of some parent hint. In this
          case, the **sanified parent type hint metadata** (i.e., immutable and
          thus hashable object encapsulating *all* metadata previously returned
          by :mod:`beartype._check.convert.convmain` sanifiers after sanitizing
          the possibly PEP-noncompliant parent hint of this child hint into a
          fully PEP-compliant parent hint).

    All remaining passed keyword-only parameters are silently ignored.

    Returns
    -------
    Hint
        Lower-level type hint currently supported by :mod:`beartype`.
    '''
    # print(f'Reducing non-beartype PEP 593 type hint {repr(hint)}...')

    # Return either...
    return (
        # If any of the following conditions apply, then preserve this metahint
        # as is for subsequent handling elsewhere;
        hint
        if (
            # This metahint is beartype-specific *AND*...
            is_hint_pep593_beartype(hint) and
            # Either...
            (
                # This hint has no parent and is thus a root hint *OR*...
                hint_parent_sane is None or
                # This hint has a parent and is thus a child hint *AND* this
                # child hint does *NOT* transitively subscript a PEP 484- or
                # 585-compliant parent subclass hint...
                not hint_parent_sane.is_hint_parent_pep484585_subclass
            )
        ) else
        # Else, either:
        # * This metahint is beartype-agnostic and thus irrelevant to us *OR*...
        # * This metahint is a child hint transitively subscripting a PEP 484-
        #   or 585-compliant parent subclass hint (e.g., hint subtree resembling
        #   "type[Annotated[cls, ...]]"). A PEP 593-compliant metahint is *NOT*
        #   an object suitable for directly passing as the second argument to
        #   the issubclass() builtin and *MUST* thus be reduced to the first
        #   child hint subscripting this metahint. That child hint *SHOULD* be
        #   an object suitable for directly passing as the second argument to
        #   the issubclass() builtin.
        #
        # In either case, ignore *ALL* annotations (i.e., *ALL* child hints
        # subscripting this PEP 593-compliant parent metahint, except the first)
        # by reducing this metahint to the first child hint it annotates.
        get_hint_pep593_metahint(
            hint=hint, exception_prefix=EXCEPTION_PLACEHOLDER)
    )
