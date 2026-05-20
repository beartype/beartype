#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **subclass hint reducers** (i.e.,
low-level callables converting higher-level subscripted and unsubscripted
:pep:`484`-compliant ``typing.Type[...]`` and :pep:`585`-compliant ``type[...]``
hints to lower-level hints more readily consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.cls.hint.hintsane import (
    HintSane,
    HintOrSane,
    make_hint_sane,
)
from beartype._data.typing.datatypingport import Hint
from typing import (
    Optional,

    # PEP 484-specific type hint factories intentionally imported as such.
    Type as typing_Type,
)

# ....................{ REDUCERS                           }....................
def reduce_hint_pep484585_subclass(
    hint: Hint,
    hint_parent_sane: Optional[HintSane],
    exception_prefix: str,
    **kwargs
) -> HintOrSane:
    '''
    Reduce the passed :pep:`484`- or :pep:`585`-compliant **subclass hint**
    (i.e., hint constraining objects to subclass that superclass) to the
    :class:`type` superclass if that hint is subscripted by an ignorable child
    hint *or* preserve this hint as is otherwise (i.e., if this hint is *not*
    subscripted by an ignorable child hint).

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : Hint
        Subclass type hint to be reduced.
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
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    All remaining passed keyword-only parameters are silently ignored.

    Returns
    -------
    HintSane
        Sanified hint metadata encapsulating the possibly lower-level hint
        reduced from this subclass hint.

    Raises
    ------
    BeartypeDecorHintPep484585Exception
        If this hint is neither a :pep:`484`- nor :pep:`585`-compliant subclass
        hint.
    '''

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype._check.convert._reduce._pep.pep484.redpep484core import (
        reduce_hint_pep484_deprecated)

    # ....................{ PEP 484                        }....................
    # If this is a PEP 484-compliant subclass hint, this hint has been
    # deprecated by PEP 585. In this case, issue a non-fatal warning.
    reduce_hint_pep484_deprecated(hint, exception_prefix)

    # If this hint is the unsubscripted PEP 484-compliant subclass hint, reduce
    # this hint to the "type" superclass.
    #
    # Note that this is *NOT* merely a nonsensical optimization. The
    # implementation of the unsubscripted PEP 484-compliant subclass type hint
    # significantly differs across Python versions. Under some but *NOT* all
    # supported Python versions (notably, Python 3.7 and 3.8), the "typing"
    # module subversively subscripts this hint by a type variable; under all
    # others, this hint remains unsubscripted. In the latter case, passing this
    # hint to the subsequent get_hint_pep484585_args() call would erroneously
    # raise an exception.
    if hint is typing_Type:
        # print(f'Reducing subclass hint {hint} to "type"...')
        return type  # pyright: ignore
    # Else, this hint is *NOT* the unsubscripted PEP 484-compliant subclass
    # hint. In this case, preserve this hint as is.

    # ....................{ SANIFY                         }....................
    # Sanified hint metadata encapsulating this possibly reduced hint.
    hint_sane = make_hint_sane(  # type: ignore[assignment]
        hint=hint,
        hint_parent_sane=hint_parent_sane,
        # Notify subsequent hint reductions reducing child hints transitively
        # subscripting this parent subclass hint that those child hints
        # transitively subscripting a parent subclass hint. Why? Because such
        # child hints *MUST* be reduced in a subclass-specific manner (e.g.,
        # reducing the PEP 593-compliant child hint "Annotated[cls, ...]"
        # subscripting the PEP 585-compliant parent subclass hint
        # "type[Annotated[cls, ...]]" to merely "type[cls]", thus eliminating
        # PEP 593 compliance entirely).
        is_hint_parent_pep484585_subclass=True,
    )

    # ....................{ RETURN                         }....................
    # Return this metadata.
    return hint_sane
