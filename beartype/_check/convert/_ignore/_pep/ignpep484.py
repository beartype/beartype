#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **type hint ignorers** (i.e., low-level
callables detecting whether :pep:`484`-compliant type hints are ignorable or
not).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.metadata.metasane import (
    HintSanifiedData,
    HintOrHintSanifiedData,
)
from beartype._util.utilobject import SENTINEL

# ....................{ TESTERS                            }....................
#FIXME: Remove this *AFTER* properly supporting type variables. *sigh*
def is_hint_pep484_typevar_ignorable(
    hint_or_sane: HintOrHintSanifiedData) -> bool:
    '''
    :data:`True` only if the passed :pep:`484`-compliant **type variable**
    (i.e., :obj:`typing.TypeVar`object) is *not* already mapped by the **type
    variable lookup table** (i.e., immutable dictionary mapping from the type
    variables originally parametrizing the origins of all transitive parent
    hints of this hint to the corresponding child hints subscripting these
    parent hints) encapsulated by the passed metadata.

    This tester currently ignores *all* unmapped type variables. Dynamically
    generating runtime code type-checking "pure" type variables is extremely
    non-trivial and possibly even infeasible in the general case.

    This tester is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as this tester is only safely callable by
    the memoized parent
    :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester.

    Parameters
    ----------
    hint_or_sane : HintOrHintSanifiedData
        Either a type hint *or* **sanified type hint metadata** (i.e.,
        :data:`.HintSanifiedData` object) to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this type variable is ignorable.
    '''

    # Avoid circular import dependencies.
    from beartype._check.convert.convsanify import is_hint_sanified_ignorable

    # If this type variable is *NOT* encapsulated by metadata providing an
    # associated type variable lookup table, this type variable *CANNOT* map to
    # a lower-level hint that is type-checkable by @beartype. Ergo, this type
    # variable is currently ignorable.
    if not isinstance(hint_or_sane, HintSanifiedData):
        return True
    # Else, this type variable is encapsulated by metadata providing an
    # associated type variable lookup table.

    # Lower-level hint mapped to this type variable by this table if this table
    # maps this type variable *OR* the sentinel placeholder otherwise (i.e., if
    # this type variable is unmapped by this table).
    hint_child = hint_or_sane.typevar_to_hint.get(hint_or_sane.hint, SENTINEL)  # pyright: ignore

    # Return true only if either...
    return (
        # This table does *NOT* map this type variable to a lower-level hint (in
        # which case this type variable is ignorable) *OR*...
        hint_child is SENTINEL or
        # This table maps this type variable to an ignorable lower-level hint.
        is_hint_sanified_ignorable(
            hint=hint_child, hint_or_sane_parent=hint_or_sane)
    )
