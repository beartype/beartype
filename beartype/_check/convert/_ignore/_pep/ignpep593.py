#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`593`-compliant **type hint ignorers** (i.e., low-level
callables detecting whether :pep:`593`-compliant type hints are ignorable or
not).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.metadata.metasane import (
    HintOrHintSanifiedData,
    get_hint_or_sane_hint,
)
from beartype._util.hint.pep.proposal.pep593 import (
    get_hint_pep593_metahint,
    is_hint_pep593_beartype,
)

# ....................{ TESTERS                            }....................
def is_hint_pep593_ignorable(hint_or_sane: HintOrHintSanifiedData) -> bool:
    '''
    :data:`True` only if the passed :pep:`593`-compliant type hint is ignorable.

    Specifically, this tester returns :data:`True` only if either:

    * The first subscripted argument of this hint is an ignorable type hint
      (e.g., :obj:`typing.Any`).
    * The second subscripted argument is *not* a beartype validator (e.g.,
      ``typing.Annotated[typing.Any, bool]``).

    This tester is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as this tester is only safely callable by
    the memoized parent
    :func:`beartype._check.convert._ignore.ignhint.is_hint_ignorable` tester.

    Parameters
    ----------
    hint_or_sane : HintOrHintSanifiedData
        Either a type hint *or* **sanified type hint metadata** (i.e.,
        :data:`.HintSanifiedData` object) to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this :pep:`593`-compliant type hint is ignorable.
    '''

    # Avoid circular import dependencies.
    from beartype._check.convert.convsanify import is_hint_sanified_ignorable
    # print(f'!!!!!!!Received 593 hint: {repr(hint)} [{repr(hint_sign)}]')

    # Hint encapsulated by this metadata.
    hint = get_hint_or_sane_hint(hint_or_sane)

    # First child hint subscripting this hint (e.g., the "Any" in
    # "Annotated[Any, 50, False]").
    metahint = get_hint_pep593_metahint(hint)

    # Return true only if...
    return (
        # This metahint is ignorable with respect to this parent hint *AND*...
        is_hint_sanified_ignorable(
            hint=metahint, hint_or_sane_parent=hint_or_sane) and
        # The second argument subscripting this parent hint is *NOT* a beartype
        # validator and is thus also ignorable (e.g., the "50" in
        # "Annotated[Any, 50, False]").
        not is_hint_pep593_beartype(hint)
    )
