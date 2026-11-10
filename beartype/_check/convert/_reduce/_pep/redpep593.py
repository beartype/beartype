#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`593`-compliant **type metahint reducers** (i.e., low-level
callables converting higher-level type hints created by subscripting the
:obj:`typing.Annotated` type hint factory to lower-level type hints more readily
consumable by :mod:`beartype`).

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
    get_hint_pep593_metadata,
    get_hint_pep593_metahint,
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
    # Defer heavyweight imports.
    from beartype.vale._core._valecore import BeartypeValidator

    # Child hint annotated by this metahint.
    hint_child = get_hint_pep593_metahint(
        hint=hint, exception_prefix=EXCEPTION_PLACEHOLDER)

    # If this metahint is a child hint transitively subscripting a PEP 484- or
    # 585-compliant parent subclass hint (e.g., "type[Annotated[cls, ...]]"), a
    # metahint is *NOT* suitable for passing to issubclass(). Reduce it to the
    # child hint it annotates, ignoring *ALL* annotations.
    if (
        hint_parent_sane is not None and
        hint_parent_sane.is_hint_parent_pep484585_subclass
    ):
        return hint_child

    # Tuple of all arbitrary objects annotating this metahint.
    metadata = get_hint_pep593_metadata(hint)

    # List of only the beartype validators annotating this metahint, silently
    # ignoring all other beartype-agnostic metadata (e.g., from third-party
    # packages like "annotated_types" and Pydantic) intermingled with them.
    validators = [
        datum for datum in metadata if isinstance(datum, BeartypeValidator)]

    # If this metahint is annotated by *NO* beartype validators, ignore all
    # annotations by reducing this metahint to the child hint it annotates.
    if not validators:
        return hint_child

    # If this metahint is annotated by only beartype validators, preserve it.
    if len(validators) == len(metadata):
        return hint

    # Else, this metahint is annotated by both validators and agnostic
    # metadata. Reduce it to a metahint annotated by only those validators,
    # preserving the metahint class (e.g., "typing" vs. "typing_extensions").
    return type(hint)(hint_child, tuple(validators))  # pyright: ignore
